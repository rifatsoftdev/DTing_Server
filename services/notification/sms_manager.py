from twilio.rest import Client

from app.constants import ENV, AnsiColor




class SMSManager:
    def __init__(self):
        self.account_sid = ENV.TWILIO_ACCOUNT_SID
        self.auth_token = ENV.TWILIO_AUTH_TOKEN
        self.twilio_phone_number = ENV.TWILIO_PHONE_NUMBER

    def __send_with_twilio(self, phone_number: str, body: str) -> bool:
        try:
            if not self.account_sid or not self.auth_token or not self.twilio_phone_number:
                print(f"{AnsiColor.RED}ERROR:{AnsiColor.RESET}    Twilio SMS configuration is incomplete")
                return False
            
            client = Client(self.account_sid, self.auth_token)
            message = client.messages.create(
                from_=self.twilio_phone_number,
                body=body,
                to=phone_number
            )

            print(f"{AnsiColor.BLUE}INFO:     SMS send on {phone_number}{AnsiColor.RESET}")

            return True
        
        except Exception as e:
            print(f"{AnsiColor.RED}ERROR:{AnsiColor.RESET}    Failed to send SMS to {phone_number}: {e}")
            return False

    def send_sms(self, phone_number: str, title: str, body: str) -> bool:
        """Phone number should be in E.164 format, e.g. +1234567890"""
        return self.__send_with_twilio(phone_number, body)

    def add_history(self, phone_number: str, title: str, body: str) -> None:
        # Implement logic to save SMS history to database or log
        pass



