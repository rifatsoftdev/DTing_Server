import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin._messaging_utils import UnregisteredError
from firebase_admin.exceptions import FirebaseError

from app.constants.colors import AnsiColor




class FCMNotification:
    def __init__(self, service_account_path: str):
        """
        service_account_path = Firebase serviceAccountKey.json file path
        """
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)

    # Single device send
    def send_single(self, fcm_token: str, type: str, title: str, body: str, img_url: str | None = None) -> str | None:
        """
        Single device token এ push notification send
        Returns message_id if successful, None if failed
        """
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=img_url
            ),
            data={
                "type": type,
                "title": title,
                "body": body,
                "img_url": img_url or ""
            },
            token=fcm_token
        )

        try:
            response = messaging.send(message)
            return response
        except UnregisteredError:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     Device unregistered!")
            return None
        except FirebaseError as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            return None
        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            return None

    # Multiple devices
    def send_multiple(self, tokens: list[str], type: str, title: str, body: str, img_url: str | None = None) -> dict:
        """
        Multicast push notification
        Returns dict with success/failure count
        """
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=img_url
            ),
            data={
                "type": type,
                "title": title,
                "body": body,
                "img_url": img_url or ""
            },
            tokens=tokens
        )

        try:
            response = messaging.send_multicast(message)
            return {
                "success": response.success_count,
                "failed": response.failure_count
            }
        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            return {"success": 0, "failed": len(tokens)}
