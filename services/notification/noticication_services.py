import json
import logging
import smtplib
import firebase_admin

from enum import Enum
from firebase_admin import credentials, messaging
from firebase_admin._messaging_utils import UnregisteredError
from firebase_admin.exceptions import FirebaseError
from fastapi import BackgroundTasks, Request
from sqlalchemy.orm import Session
from email.mime.text import MIMEText

from twilio.rest import Client

from app.constants import ENV
from app.model import UserTable, SessionTable
from app.templates import NotificationTemplate

from app.router.notify_router import check_online_user, send_notification as send_ws_notification


logger = logging.getLogger(__name__)


class NotificationData:
    def __init__(
        self,
        user_id: str = None,
        target_id: str = None,
        title: str = None,
        body: str = None,
        template: str = None,
        context: dict = None,

        noty_type: str = "default",
        type: str = None,
        data: dict = None,
        image_url: str = None,
        priority: str = "normal",

        push: bool = True,
        email: bool = True,
        sms: bool = True
    ):
        self.user_id = user_id or target_id
        self.title = title or "Notification"
        self.body = body or ""
        self.template = template
        self.context = context or {}

        self.noty_type = self._stringify(type or noty_type)
        self.data = data or {}
        self.image_url = image_url
        self.priority = priority

        self.push = push
        self.email = email
        self.sms = sms

    @property
    def channels(self) -> list[str]:
        channels = []
        if self.push:
            channels.append("push")
        if self.email:
            channels.append("email")
        if self.sms:
            channels.append("sms")
        return channels

    @staticmethod
    def _stringify(value) -> str:
        if value is None:
            return ""
        if isinstance(value, Enum):
            return str(value.value)
        return str(value)

    def render(self, channels: list[str] = None) -> dict:
        if self.template:
            return NotificationTemplate.resolve(
                template=self.template,
                context=self.context,
                title=self.title,
                body=self.body,
                channels=channels or self.channels,
            )

        fallback = NotificationTemplate.fallback(
            title=self.title,
            body=self.body,
        )
        selected_channels = channels or self.channels
        return {channel: fallback[channel] for channel in selected_channels if channel in fallback}


class NotificationServices:
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request = None,
        authorization: str = None
    ):
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization

        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred_dict = json.loads(ENV.POCKETPAY_ADMINSDK)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        

    def send_by_push(self, fcm_token: str, data: NotificationData, content: dict = None) -> bool:
        """
        Single device token এ push notification send
        Returns True if successful, False if failed
        """
        try:
            push_content = content or data.render()["push"]
            payload = {
                "type": data.noty_type,
                "noty_type": data.noty_type,
                "title": push_content["title"],
                "body": push_content["body"],
                "img_url": data.image_url or "",
                **data.data
            }

            message = messaging.Message(
                notification=messaging.Notification(
                    title=push_content["title"],
                    body=push_content["body"],
                    image=data.image_url
                ),
                data={key: NotificationData._stringify(value) for key, value in payload.items()},
                token=fcm_token
            )
            response = messaging.send(message)
            return True if response else False
        
        except UnregisteredError:
            logger.warning("Device unregistered for notification user_id=%s", data.user_id)
            return False
        
        except FirebaseError as e:
            logger.warning("Firebase notification failed for user_id=%s: %s", data.user_id, e)
            return False
        
        except Exception as e:
            logger.exception("Push notification failed for user_id=%s: %s", data.user_id, e)
            return False


    def send_by_email(self, to_email: str, data: NotificationData, content: dict = None) -> bool:
        email_address = ENV.EMAIL_ADDRESS
        email_password = ENV.EMAIL_PASSWORD
        smtp_server = ENV.SMTP_SERVER
        smtp_port = ENV.SMTP_PORT

        email_content = content or data.render()["email"]
        msg = MIMEText(email_content["body"], 'html')
        msg['Subject'] = email_content["title"]
        msg['From'] = email_address
        msg['To'] = to_email

        try:
            smtp_class = smtplib.SMTP_SSL if ENV.EMAIL_USE_SSL else smtplib.SMTP
            with smtp_class(smtp_server, smtp_port) as server:
                if ENV.EMAIL_USE_TLS and not ENV.EMAIL_USE_SSL:
                    server.starttls()
                server.login(email_address, email_password)
                server.sendmail(email_address, to_email, msg.as_string())
            return True
        
        except Exception as e:
            logger.exception("Email notification failed for user_id=%s to=%s: %s", data.user_id, to_email, e)
            return False


    def send_by_sms(self, phone_number: str, data: NotificationData, content: dict = None) -> bool:
        try:
            sms_content = content or data.render()["sms"]
            if not ENV.ACCOUNT_SID or not ENV.AUTH_TOKEN or not ENV.TWILIO_PHONE_NUMBER:
                logger.error("Twilio SMS configuration is incomplete")
                return False
            
            client = Client(ENV.ACCOUNT_SID, ENV.AUTH_TOKEN)
            message = client.messages.create(
                from_=ENV.TWILIO_PHONE_NUMBER,
                body=sms_content["body"],
                to=phone_number
            )
        except Exception as e:
            logger.exception("SMS notification failed for user_id=%s to=%s: %s", data.user_id, phone_number, e)
            return False

        logger.info("SMS notification sent user_id=%s to=%s sid=%s", data.user_id, phone_number, message.sid)
        return True

    
    def send_notification(self, data: NotificationData) -> bool:
        """
        Sends the notification through the channels selected in NotificationData.
        """
        self.background_tasks.add_task(self._process_notification, data)
        return True


    async def _process_notification(self, data: NotificationData):
        user = self.db.query(UserTable).filter(
            UserTable.user_id == data.user_id
        ).first()

        if not user:
            return

        content = data.render(data.channels)
        notification_delivered = False

        # 1. Try WebSocket (Real-time)
        if data.push and check_online_user(user.user_id):
            await send_ws_notification(
                user.user_id, data.noty_type, content["push"]["title"], content["push"]["body"], data.image_url
            )
            notification_delivered = True

        # 2. Try Push Notification (FCM)
        if data.push:
            sessions = self.db.query(SessionTable).filter(
                SessionTable.user_id == user.user_id,
                SessionTable.is_login == True,
                SessionTable.fcm_token != None
            ).all()
            
            for session in sessions:
                if self.send_by_push(session.fcm_token, data, content["push"]):
                    notification_delivered = True

        # 3. Email
        if data.email and user.email_address:
            if self.send_by_email(user.email_address, data, content["email"]):
                notification_delivered = True

        # 4. SMS
        if data.sms and user.phone_number:
            if self.send_by_sms(user.phone_number, data, content["sms"]):
                notification_delivered = True






# ==============================================================================
# ==============================================================================
