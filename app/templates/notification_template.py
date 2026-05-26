from datetime import datetime
import logging
from typing import Callable, Dict, Iterable

from app.templates.email_template import EmailTemplate
from app.templates.push_template import PushTemplate
from app.templates.sms_template import SMSTemplate


logger = logging.getLogger(__name__)
CHANNELS = ("push", "email", "sms")


class NotificationTemplate:
    @staticmethod
    def fallback(title: str, body: str) -> Dict[str, Dict[str, str]]:
        content = {"title": title or "Notification", "body": body or ""}
        return {
            "push": dict(content),
            "email": dict(content),
            "sms": dict(content),
        }

    @staticmethod
    def resolve(
        template: str,
        context: dict = None,
        title: str = None,
        body: str = None,
        channels: Iterable[str] = None,
    ) -> Dict[str, Dict[str, str]]:
        context = context or {}
        selected_channels = NotificationTemplate._selected_channels(channels)
        fallback = NotificationTemplate.fallback(
            title=title,
            body=body or context.get("body") or context.get("message") or "",
        )

        resolvers: Dict[str, Callable[[dict], Dict[str, Dict[str, str]]]] = {
            "auth.welcome": NotificationTemplate._welcome,
            "auth.password.reset.request": NotificationTemplate._password_reset_request,
            "auth.password.reset.success": NotificationTemplate._password_reset_success,
            "auth.password.changed": NotificationTemplate._password_changed,
            "admin.custom": NotificationTemplate._custom,
            "transaction.payment": NotificationTemplate._transaction_payment,
        }

        resolver = resolvers.get(template)
        if not resolver:
            logger.warning("Notification template not found: %s", template)
            return {channel: fallback[channel] for channel in selected_channels}

        try:
            render_context = dict(context)
            if title is not None:
                render_context["title"] = title
            if body is not None:
                render_context["body"] = body

            rendered = resolver(render_context)
            return {
                channel: NotificationTemplate._valid_content(rendered.get(channel)) or fallback[channel]
                for channel in selected_channels
            }
        except Exception:
            logger.exception("Notification template render failed: %s", template)
            return {channel: fallback[channel] for channel in selected_channels}

    @staticmethod
    def _selected_channels(channels: Iterable[str] = None) -> tuple[str, ...]:
        if not channels:
            return CHANNELS

        selected = tuple(channel for channel in channels if channel in CHANNELS)
        return selected or CHANNELS

    @staticmethod
    def _valid_content(content: dict = None) -> dict | None:
        if not isinstance(content, dict):
            return None

        return {
            "title": str(content.get("title") or "Notification"),
            "body": str(content.get("body") or ""),
        }

    @staticmethod
    def _name(context: dict) -> str:
        return context.get("name") or context.get("full_name") or "User"

    @staticmethod
    def _welcome(context: dict) -> Dict[str, Dict[str, str]]:
        name = NotificationTemplate._name(context)
        return {
            "push": PushTemplate.welcome_push_template(name),
            "email": EmailTemplate.welcome_email_template(name),
            "sms": SMSTemplate.welcome_sms_template(name),
        }

    @staticmethod
    def _password_reset_request(context: dict) -> Dict[str, Dict[str, str]]:
        name = NotificationTemplate._name(context)
        email = context.get("email") or context.get("email_address") or ""
        reset_link = context.get("reset_link") or context.get("password_token") or ""
        return {
            "push": PushTemplate.reset_password_push_template(name, email, reset_link),
            "email": EmailTemplate.reset_password_template(name, email, reset_link),
            "sms": SMSTemplate.reset_password_sms_template(name, email, reset_link),
        }

    @staticmethod
    def _password_reset_success(context: dict) -> Dict[str, Dict[str, str]]:
        name = NotificationTemplate._name(context)
        return {
            "push": PushTemplate.password_reset_success_push_template(name),
            "email": EmailTemplate.password_reset_success_template(name),
            "sms": SMSTemplate.password_reset_success_sms_template(name),
        }

    @staticmethod
    def _password_changed(context: dict) -> Dict[str, Dict[str, str]]:
        name = NotificationTemplate._name(context)
        changed_at = context.get("changed_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip_address = context.get("ip_address") or context.get("ip") or "unknown"
        return {
            "push": PushTemplate.password_changed_push_template(name, changed_at, ip_address),
            "email": EmailTemplate.password_changed_template(name, changed_at, ip_address),
            "sms": SMSTemplate.password_changed_sms_template(name, changed_at, ip_address),
        }

    @staticmethod
    def _custom(context: dict) -> Dict[str, Dict[str, str]]:
        name = NotificationTemplate._name(context)
        title = context.get("title") or "Notification"
        message = context.get("body") or context.get("message") or ""
        return {
            "push": PushTemplate.general_notification_push_template(name, title, message),
            "email": EmailTemplate.general_notification_template(name, title, message),
            "sms": SMSTemplate.general_notification_sms_template(name, title, message),
        }

    @staticmethod
    def _transaction_payment(context: dict) -> Dict[str, Dict[str, str]]:
        name = NotificationTemplate._name(context)
        amount = context.get("amount") or 0
        push = PushTemplate.transaction_push_template(
            transaction_type="payment",
            amount=amount,
            **{key: value for key, value in context.items() if key not in {"title", "body", "amount"}},
        )
        return {
            "push": push,
            "email": EmailTemplate.general_notification_template(name, push["title"], push["body"]),
            "sms": SMSTemplate.general_notification_sms_template(name, push["title"], push["body"]),
        }
