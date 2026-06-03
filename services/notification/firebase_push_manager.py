from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError
from firebase_admin.exceptions import FirebaseError

from app.constants import AnsiColor


class FirebasePushManager:
    def send_push(
        self,
        fcm_token: str,
        title: str,
        body: str,
        payload: dict | None = None
    ) -> bool:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=payload or {},
                token=fcm_token
            )

            response = messaging.send(message)

            print(f"{AnsiColor.BLUE}INFO:{AnsiColor.RESET}     Push sent to {fcm_token}")

            return bool(response)

        except UnregisteredError:
            print(f"{AnsiColor.RED}ERROR:{AnsiColor.RESET}     FCM token {fcm_token} is unregistered.")
            return False

        except FirebaseError as e:
            print(f"{AnsiColor.RED}ERROR:{AnsiColor.RESET}     Firebase error: {e}")
            return False

        except Exception as e:
            print(f"{AnsiColor.RED}ERROR:{AnsiColor.RESET}     Unexpected error: {e}")
            return False
    
    def add_history(self, fcm_token: str, title: str, body: str, payload: dict = None) -> None:
        # Implement logic to save push notification history to database or log
        pass