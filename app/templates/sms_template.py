from typing import Dict, List
from app.constants import String



class SMSTemplate:
    @staticmethod
    def welcome_template(name: str):
        return {
            "title": f"Welcome to {String.COMPANY_NAME}!",
            "body": f"Hello {name}, your account is ready. Thanks for joining us.",
        }

    @staticmethod
    def otp_template(name: str, email: str, otp: str):
        return {
            "title": "Your OTP Code",
            "body": f"Hello {name}, your OTP is {otp}. Valid for 5 minutes.",
        }

    @staticmethod
    def login_alert_template(name: str, device: str, ip_address: str, location: str = None, email: str = None) -> Dict[str, str]:
        location_text = f" near {location}" if location else ""
        return {
            "title": "New Login Detected",
            "body": f"Hello {name}, new login from {device}, IP {ip_address}{location_text}.",
        }

    @staticmethod
    def kyc_update_template(name: str, status: str):
        return {
            "title": "KYC Verification Update",
            "body": f"Hello {name}, your KYC status is now {status.upper()}.",
        }

    @staticmethod
    def reset_password_template(name: str, email: str, reset_link: str):
        return {
            "title": "Reset Your Password",
            "body": f"Hello {name}, a password reset was requested for {email}. Tap to reset it.",
        }

    @staticmethod
    def general_notification_template(name: str, title: str, message: str, button_text: str = None, button_link: str = None):
        return {
            "title": title,
            "body": f"Hello {name}, {message}"
        }

    @staticmethod
    def link_google_template():
        return {
            "title": "Google Account Linked",
            "body": f"Your {String.COMPANY_NAME} account has been successfully linked with Google.",
        }
        
    @staticmethod
    def password_changed_template(name: str, changed_at: str, ip_address: str) -> Dict[str, str]:
        return {
            "title": "Password Changed",
            "body": f"Hello {name}, your password was changed from IP {ip_address}. Secure your account if this was not you.",
        }

    @staticmethod
    def email_changed_template(name: str, old_email: str, new_email: str) -> Dict[str, str]:
        return {
            "title": "Email Address Changed",
            "body": f"Hello {name}, your email changed to {new_email}. Contact support if this was not you.",
        }

    @staticmethod
    def two_factor_enabled_template(name: str) -> Dict[str, str]:
        return {
            "title": "Two-Factor Authentication Enabled",
            "body": f"Hello {name}, two-factor authentication is now enabled.",
        }

    @staticmethod
    def two_factor_disabled_template(name: str) -> Dict[str, str]:
        return {
            "title": "Two-Factor Authentication Disabled",
            "body": f"Hello {name}, two-factor authentication was disabled. Secure your account if this was not you.",
        }

    @staticmethod
    def account_locked_template(name: str, unlock_time: str = None) -> Dict[str, str]:
        unlock_text = f" Try again after {unlock_time}." if unlock_time else ""
        return {
            "title": "Account Locked",
            "body": f"Hello {name}, your account is temporarily locked.{unlock_text}",
        }

    @staticmethod
    def account_unlocked_template(name: str) -> Dict[str, str]:
        return {
            "title": "Account Unlocked",
            "body": f"Hello {name}, your account has been unlocked.",
        }

    @staticmethod
    def email_verification_template(name: str, verification_link: str) -> Dict[str, str]:
        return {
            "title": "Verify Your Email Address",
            "body": f"Hello {name}, tap to verify your email address.",
        }

    @staticmethod
    def password_reset_success_template(name: str) -> Dict[str, str]:
        return {
            "title": "Password Reset Successful",
            "body": f"Hello {name}, your password has been reset successfully.",
        }

    @staticmethod
    def recovery_code_template(name: str, recovery_codes: List[str]) -> Dict[str, str]:
        return {
            "title": "Your Recovery Codes",
            "body": f"Hello {name}, new recovery codes were generated. Keep them secure.",
        }

    @staticmethod
    def account_deleted_template(name: str) -> Dict[str, str]:
        return {
            "title": "Account Deleted",
            "body": f"Hello {name}, your account has been deleted successfully.",
        }

    @staticmethod
    def account_deactivated_template(name: str, reason: str = None) -> Dict[str, str]:
        reason_text = f" Reason: {reason}." if reason else ""
        return {
            "title": "Account Deactivated",
            "body": f"Hello {name}, your account has been deactivated.{reason_text}",
        }

    @staticmethod
    def account_reactivated_template(name: str) -> Dict[str, str]:
        return {
            "title": "Account Reactivated",
            "body": f"Hello {name}, your account has been reactivated.",
        }

    @staticmethod
    def subscription_expiry_template(name: str, expiry_date: str) -> Dict[str, str]:
        return {
            "title": "Subscription Expiry Notice",
            "body": f"Hello {name}, your subscription expires on {expiry_date}.",
        }

    @staticmethod
    def maintenance_notification_template(name: str, maintenance_time: str) -> Dict[str, str]:
        return {
            "title": "Scheduled Maintenance",
            "body": f"{String.COMPANY_NAME} maintenance is scheduled for {maintenance_time}.",
        }

    @staticmethod
    def terms_update_template(name: str) -> Dict[str, str]:
        return {
            "title": "Terms and Conditions Updated",
            "body": f"Hello {name}, our terms and conditions have been updated.",
        }

    @staticmethod
    def admin_alert_template(title: str, message: str) -> Dict[str, str]:
        return {
            "title": title,
            "body": f"Admin alert: {message}"
        }

    @staticmethod
    def api_key_created_template(name: str, key_name: str) -> Dict[str, str]:
        return {
            "title": "API Key Created",
            "body": f"Hello {name}, API key '{key_name}' was created.",
        }

    @staticmethod
    def api_key_revoked_template(name: str, key_name: str) -> Dict[str, str]:
        return {
            "title": "API Key Revoked",
            "body": f"Hello {name}, API key '{key_name}' was revoked.",
        }


