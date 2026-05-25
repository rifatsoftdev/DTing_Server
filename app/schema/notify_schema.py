from pydantic import BaseModel

from app.enums import NotificationType


class AdminNotyfyResuest(BaseModel):
    user_id: str | None = None
    notification_type: NotificationType | None = None
    type: NotificationType | None = None
    title: str
    message: str | None = None
    body: str | None = None
    image_url: str | None = None

    button_text: str | None = None
    button_link: str | None = None
    send_push: bool = True
    send_email: bool = False
    send_sms: bool = False
