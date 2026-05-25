from typing import Dict, List

from app.constants import String


def _pack(title: str, body: str) -> Dict[str, str]:
    return {"title": title, "body": body}


def _prefix(body: str) -> str:
    return f"{String.COMPANY_NAME}: {body}"


class SMSTemplate:
    @staticmethod
    def welcome_sms_template(name: str):
        return _pack(
            f"Welcome to {String.COMPANY_NAME}!",
            _prefix(f"Hello {name}, your account is ready. Thanks for joining {String.COMPANY_NAME}."),
        )

    @staticmethod
    def otp_sms_template(name: str, email: str, otp: str):
        return _pack(
            f"Your OTP Code for {String.COMPANY_NAME}",
            _prefix(f"Hello {name}, your OTP is {otp}. It is valid for 5 minutes. Do not share it."),
        )

    @staticmethod
    def login_alert_sms_template(name: str, ip_address: str):
        return SMSTemplate.new_device_login_sms_template(
            name=name,
            device="Unknown device",
            ip_address=ip_address,
        )

    @staticmethod
    def kyc_update_sms_template(name: str, status: str):
        return _pack(
            "KYC Verification Update",
            _prefix(f"Hello {name}, your KYC status is now {status.upper()}."),
        )

    @staticmethod
    def reset_password_sms_template(name: str, email: str, reset_link: str):
        return _pack(
            "Reset Your Password",
            _prefix(f"Hello {name}, reset your password using this link: {reset_link}. Valid for 15 minutes."),
        )

    @staticmethod
    def general_notification_sms_template(name: str, title: str, message: str, button_text: str = None, button_link: str = None):
        link_text = f" Link: {button_link}" if button_link else ""
        return _pack(title, _prefix(f"Hello {name}, {message}{link_text}"))

    @staticmethod
    def password_changed_sms_template(name: str, changed_at: str, ip_address: str) -> Dict[str, str]:
        return _pack(
            "Password Changed",
            _prefix(f"Hello {name}, your password was changed at {changed_at} from IP {ip_address}. If this was not you, secure your account."),
        )

    @staticmethod
    def email_changed_sms_template(name: str, old_email: str, new_email: str) -> Dict[str, str]:
        return _pack(
            "Email Address Changed",
            _prefix(f"Hello {name}, your account email changed from {old_email} to {new_email}. Contact support if this was not you."),
        )

    @staticmethod
    def two_factor_enabled_sms_template(name: str) -> Dict[str, str]:
        return _pack(
            "Two-Factor Authentication Enabled",
            _prefix(f"Hello {name}, two-factor authentication is now enabled on your account."),
        )

    @staticmethod
    def two_factor_disabled_sms_template(name: str) -> Dict[str, str]:
        return _pack(
            "Two-Factor Authentication Disabled",
            _prefix(f"Hello {name}, two-factor authentication was disabled. If this was not you, secure your account."),
        )

    @staticmethod
    def new_device_login_sms_template(name: str, device: str, ip_address: str, location: str = None, email: str = None) -> Dict[str, str]:
        location_text = f" near {location}" if location else ""
        return _pack(
            "New Login Detected",
            _prefix(f"Hello {name}, new login from {device}, IP {ip_address}{location_text}. If this was not you, secure your account."),
        )

    @staticmethod
    def account_locked_sms_template(name: str, unlock_time: str = None) -> Dict[str, str]:
        unlock_text = f" Try again after {unlock_time}." if unlock_time else ""
        return _pack(
            "Account Locked",
            _prefix(f"Hello {name}, your account is temporarily locked due to too many failed attempts.{unlock_text}"),
        )

    @staticmethod
    def account_unlocked_sms_template(name: str) -> Dict[str, str]:
        return _pack(
            "Account Unlocked",
            _prefix(f"Hello {name}, your account has been unlocked. You can sign in again."),
        )

    @staticmethod
    def email_verification_sms_template(name: str, verification_link: str) -> Dict[str, str]:
        return _pack(
            "Verify Your Email Address",
            _prefix(f"Hello {name}, verify your email using this link: {verification_link}"),
        )

    @staticmethod
    def password_reset_success_sms_template(name: str) -> Dict[str, str]:
        return _pack(
            "Password Reset Successful",
            _prefix(f"Hello {name}, your password has been reset successfully."),
        )

    @staticmethod
    def recovery_code_sms_template(name: str, recovery_codes: List[str]) -> Dict[str, str]:
        codes = ", ".join(recovery_codes)
        return _pack(
            "Your Recovery Codes",
            _prefix(f"Hello {name}, your recovery codes are: {codes}. Keep them secure."),
        )

    @staticmethod
    def account_deleted_sms_template(name: str) -> Dict[str, str]:
        return _pack(
            "Account Deleted",
            _prefix(f"Hello {name}, your account has been deleted successfully."),
        )

    @staticmethod
    def account_deactivated_sms_template(name: str, reason: str = None) -> Dict[str, str]:
        reason_text = f" Reason: {reason}." if reason else ""
        return _pack(
            "Account Deactivated",
            _prefix(f"Hello {name}, your account has been deactivated.{reason_text}"),
        )

    @staticmethod
    def account_reactivated_sms_template(name: str) -> Dict[str, str]:
        return _pack(
            "Account Reactivated",
            _prefix(f"Hello {name}, your account has been reactivated."),
        )

    @staticmethod
    def subscription_expiry_sms_template(name: str, expiry_date: str) -> Dict[str, str]:
        return _pack(
            "Subscription Expiry Notice",
            _prefix(f"Hello {name}, your subscription expires on {expiry_date}. Renew to avoid interruption."),
        )

    @staticmethod
    def maintenance_notification_sms_template(name: str, maintenance_time: str) -> Dict[str, str]:
        return _pack(
            "Scheduled Maintenance",
            _prefix(f"Hello {name}, scheduled maintenance is planned for {maintenance_time}. Some services may be unavailable."),
        )

    @staticmethod
    def terms_update_sms_template(name: str) -> Dict[str, str]:
        return _pack(
            "Terms and Conditions Updated",
            _prefix(f"Hello {name}, our terms and conditions have been updated. Please review the latest terms."),
        )

    @staticmethod
    def admin_alert_sms_template(title: str, message: str) -> Dict[str, str]:
        return _pack(title, _prefix(f"Admin alert: {message}"))

    @staticmethod
    def api_key_created_sms_template(name: str, key_name: str) -> Dict[str, str]:
        return _pack(
            "API Key Created",
            _prefix(f"Hello {name}, API key '{key_name}' was created. Revoke it if this was not you."),
        )

    @staticmethod
    def api_key_revoked_sms_template(name: str, key_name: str) -> Dict[str, str]:
        return _pack(
            "API Key Revoked",
            _prefix(f"Hello {name}, API key '{key_name}' was revoked."),
        )

    @staticmethod
    def cash_in_sms(amount: float, balance: float):
        return _prefix(f"Cash In of {amount} TK successful. Current balance {balance} TK. Transaction ID: [TXN_ID].")

    @staticmethod
    def cash_out_sms(amount: float, balance: float):
        return _prefix(f"Cash Out of {amount} TK successful. Current balance {balance} TK. Fee applied. Thank you.")

    @staticmethod
    def send_money_sms(amount: float, recipient: str):
        return _prefix(f"You have successfully sent {amount} TK to {recipient}. Thank you for using {String.COMPANY_NAME}.")

    @staticmethod
    def generic_alert_sms(message: str):
        return _prefix(f"Alert: {message}")



if __name__ == "__main__":
    # Example usage
    template = SMSTemplate.welcome_sms_template("John Doe")
    print(template)