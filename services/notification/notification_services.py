from enum import Enum
from typing import Callable
from fastapi import BackgroundTasks, Request
from matplotlib.pyplot import title
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.model import SessionTable
from app.templates.email_template import EmailTemplate
from app.templates.push_template import PushTemplate
from app.templates.sms_template import SMSTemplate

from services.notification.email_manager import EmailManager
from services.notification.firebase_push_manager import FirebasePushManager
from services.notification.sms_manager import SMSManager
from services.notification.websocket_push_manager import NotifyWebSocket, WebsocketPushManager


class NotificationEvent(Enum):
    WELCOME = "welcome"
    OTP = "otp"
    LOGIN_ALERT = "login_alert"
    KYC_UPDATE = "kyc_update"
    RESET_PASSWORD = "reset_password"
    GENERAL_NOTIFICATION = "general_notification"
    LINK_GOOGLE = "link_google"
    PASSWORD_CHANGE = "password_change"
    
    


class NotificationData(BaseModel):
    user_id: str | None = None
    email_address: str | None = None
    phone_number: str | None = None
    fcm_token: str | None = None

    event: NotificationEvent | str | None = None
    title: str | None = None
    body: str | None = None
    template: str | None = None
    context: dict = {}
    data: dict = {}

    push: bool = False
    email: bool = False
    sms: bool = False
    payload: dict = {}


# Maps one notification event to the correct template function for each channel.
NOTIFICATION_TEMPLATE_REGISTRY: dict[NotificationEvent, dict[str, Callable]] = {
    NotificationEvent.WELCOME: {
        "email": EmailTemplate.welcome_template,
        "sms": SMSTemplate.welcome_template,
        "push": PushTemplate.welcome_template,
    },
    NotificationEvent.OTP: {
        "email": EmailTemplate.otp_template,
        "sms": SMSTemplate.otp_template,
        "push": PushTemplate.otp_template,
    },
    NotificationEvent.LOGIN_ALERT: {
        "email": EmailTemplate.login_alert_template,
        "sms": SMSTemplate.login_alert_template,
        "push": PushTemplate.login_alert_template,
    },
    NotificationEvent.KYC_UPDATE: {
        "email": EmailTemplate.kyc_update_template,
        "sms": SMSTemplate.kyc_update_template,
        "push": PushTemplate.kyc_update_template,
    },
    NotificationEvent.RESET_PASSWORD: {
        "email": EmailTemplate.reset_password_template,
        "sms": SMSTemplate.reset_password_template,
        "push": PushTemplate.reset_password_template,
    },
    NotificationEvent.GENERAL_NOTIFICATION: {
        "email": EmailTemplate.general_notification_template,
        "sms": SMSTemplate.general_notification_template,
        "push": PushTemplate.general_notification_template,
    },
    NotificationEvent.LINK_GOOGLE: {
        "email": EmailTemplate.link_google_template,
        "sms": SMSTemplate.link_google_template,
        "push": PushTemplate.link_google_template,
    },
    NotificationEvent.PASSWORD_CHANGE: {
        "email": EmailTemplate.password_changed_template,
        "sms": SMSTemplate.password_changed_template,
        "push": PushTemplate.password_changed_template,
    },
}


# Keeps old template strings working while the new code uses NotificationEvent.
NOTIFICATION_EVENT_ALIASES: dict[str, NotificationEvent] = {
    "welcome": NotificationEvent.WELCOME,
    "auth.welcome": NotificationEvent.WELCOME,
    "otp": NotificationEvent.OTP,
    "auth.otp": NotificationEvent.OTP,
    "login_alert": NotificationEvent.LOGIN_ALERT,
    "auth.login_alert": NotificationEvent.LOGIN_ALERT,
    "kyc_update": NotificationEvent.KYC_UPDATE,
    "kyc.update": NotificationEvent.KYC_UPDATE,
    "reset_password": NotificationEvent.RESET_PASSWORD,
    "auth.password.reset.request": NotificationEvent.RESET_PASSWORD,
    "general_notification": NotificationEvent.GENERAL_NOTIFICATION,
    "link_google": NotificationEvent.LINK_GOOGLE,
    "auth.link_google": NotificationEvent.LINK_GOOGLE,
    
    "password_change": NotificationEvent.PASSWORD_CHANGE,
    "auth.password_change": NotificationEvent.PASSWORD_CHANGE,
    "auth.password.changed": NotificationEvent.PASSWORD_CHANGE,
    "auth.password.reset.success": NotificationEvent.PASSWORD_CHANGE,

    "admin.custom": NotificationEvent.GENERAL_NOTIFICATION,
}


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

    def _get_channels(self, data: NotificationData) -> list[str]:
        # Convert boolean flags into a stable channel list.
        channels = []
        if data.email:
            channels.append("email")
        if data.sms:
            channels.append("sms")
        if data.push:
            channels.append("push")
        return channels

    def _get_event(self, data: NotificationData) -> NotificationEvent | None:
        # New code should pass data.event, but template aliases support old callers.
        event = data.event or data.template
        if event is None:
            return None

        if isinstance(event, NotificationEvent):
            return event

        event_key = str(event).strip()
        if event_key in NOTIFICATION_EVENT_ALIASES:
            return NOTIFICATION_EVENT_ALIASES[event_key]

        try:
            return NotificationEvent(event_key)
        except ValueError:
            return None

    def _get_template_data(self, data: NotificationData) -> dict:
        # context is the current field name; data is kept for clearer new calls.
        template_data = {}
        template_data.update(data.context or {})
        template_data.update(data.data or {})

        if data.title and "title" not in template_data:
            template_data["title"] = data.title
        if data.body and "message" not in template_data:
            template_data["message"] = data.body

        return template_data

    def _render_content(self, data: NotificationData, channel: str) -> dict | None:
        # Fixed notifications render from event + channel; custom notifications use title/body.
        event = self._get_event(data)
        if event:
            template_func = NOTIFICATION_TEMPLATE_REGISTRY.get(event, {}).get(channel)
            if template_func is None:
                print(f"Notification template not found for event={event.value}, channel={channel}")
                return None

            try:
                return template_func(**self._get_template_data(data))
            except TypeError as e:
                print(f"Notification template data mismatch for event={event.value}, channel={channel}: {e}")
                return None

        if data.title and data.body:
            return {
                "title": data.title,
                "body": data.body
            }

        print("Notification title/body or valid event is required")
        return None

    def _get_fcm_token(self, data: NotificationData) -> str | None:
        # Caller can pass fcm_token directly; otherwise use the latest active session token.
        if data.fcm_token:
            return data.fcm_token

        if not data.user_id:
            return None

        session = self.db.query(SessionTable).filter(
            SessionTable.user_id == data.user_id,
            SessionTable.is_login == True,
            SessionTable.fcm_token.isnot(None)
        ).order_by(SessionTable.last_seen_at.desc()).first()

        return session.fcm_token if session else None

    def _send_email_notification(self, email_address: str, content: dict) -> bool:
        # EmailManager expects email_address, subject, body.
        return EmailManager().send_email(
            email_address=email_address,
            subject=content["title"],
            body=content["body"]
        )

    def _send_sms_notification(self, phone_number: str, content: dict) -> bool:
        # SMSManager expects phone_number, title, body.
        return SMSManager().send_sms(
            phone_number=phone_number,
            title=content["title"],
            body=content["body"]
        )

    async def _send_push_notification(self, data: NotificationData, content: dict) -> bool:
        # Push first tries live websocket by user_id, then falls back to Firebase by fcm_token.
        if data.user_id:
            notifier = NotifyWebSocket(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )

            if await notifier.check_online_user(data.user_id):
                await notifier.send_notification(
                    user_id=data.user_id,
                    title=content["title"],
                    body=content["body"],
                    payload=data.payload
                )
                return True

        fcm_token = self._get_fcm_token(data)
        if not fcm_token:
            print("Push notification skipped: user is offline and fcm_token was not found")
            return False

        return FirebasePushManager().send_push(
            fcm_token=fcm_token,
            title=content["title"],
            body=content["body"],
            payload=data.payload
        )

    def send_notification(self, data: NotificationData = None, **kwargs) -> bool:
        # Accept both send_notification(NotificationData(...)) and send_notification(data=...).
        if data is None:
            data = kwargs.get("data")
        if data is None:
            data = NotificationData(**kwargs)
        if isinstance(data, dict):
            data = NotificationData(**data)

        channels = self._get_channels(data)
        if not channels:
            print("Notification skipped: no channel selected")
            return False

        queued = False

        for channel in channels:
            content = self._render_content(data, channel)
            if not content:
                continue

            if channel == "email":
                if not data.email_address:
                    print("Email notification skipped: email_address is required")
                    continue
                self.background_tasks.add_task(
                    self._send_email_notification,
                    data.email_address,
                    content
                )
                queued = True

            elif channel == "sms":
                if not data.phone_number:
                    print("SMS notification skipped: phone_number is required")
                    continue
                self.background_tasks.add_task(
                    self._send_sms_notification,
                    data.phone_number,
                    content
                )
                queued = True

            elif channel == "push":
                if not data.user_id and not data.fcm_token:
                    print("Push notification skipped: user_id or fcm_token is required")
                    continue
                self.background_tasks.add_task(
                    self._send_push_notification,
                    data,
                    content
                )
                queued = True

        return queued




# ==============================================================================
# ==============================================================================
