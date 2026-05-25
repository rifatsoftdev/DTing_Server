from typing import Dict, List, Optional

from app.constants import String


BRAND_COLOR = "#1E88E5"


def main_structure(body: str):
    return f"""
<html>
  <body style="margin:0; padding:0; font-family:'Helvetica Neue',Arial,sans-serif; background-color:#f5f6fa;">
    <table align="center" width="100%" style="max-width:600px; margin:auto; background-color:#ffffff; border-radius:10px; overflow:hidden; box-shadow:0 0 15px rgba(0,0,0,0.1);">
      <tr>
        <td style="background-color:{BRAND_COLOR}; padding:25px; text-align:center;">
          <img src="{String.COMPANY_LOGO}" alt="{String.COMPANY_NAME} Logo" width="120" style="display:block; margin:auto;">
        </td>
      </tr>
      {body}
      <tr>
        <td style="background-color:#f1f2f6; padding:20px; text-align:center; font-size:12px; color:#777777;">
          {String.COMPANY_NAME} | {String.COMPANY_ADDRESS} | {String.COMPANY_CONTACT}<br>
          &copy; {String.COMPANY_NAME} 2026
        </td>
      </tr>
    </table>
  </body>
</html>
"""


def _button(button_text: Optional[str], button_link: Optional[str]):
    if not button_text or not button_link:
        return ""

    return f"""
      <div style="text-align:center; margin:25px 0;">
        <a href="{button_link}" style="display:inline-block; background-color:{BRAND_COLOR}; color:#ffffff; text-decoration:none; padding:14px 28px; border-radius:6px; font-size:16px; font-weight:bold;">{button_text}</a>
      </div>
    """


def _details_table(details: Optional[Dict[str, str]] = None):
    rows = ""
    for key, value in (details or {}).items():
        if value is None or value == "":
            continue
        rows += f"""
          <tr>
            <td style="padding:8px 0; color:#777777;">{key}</td>
            <td style="padding:8px 0; color:#333333; text-align:right; font-weight:bold;">{value}</td>
          </tr>
        """

    if not rows:
        return ""

    return f"""
      <table width="100%" style="background-color:#f1f2f6; padding:15px; border-radius:8px; margin:20px 0; font-size:14px;">
        {rows}
      </table>
    """


def _body(
    title: str,
    message: str,
    name: Optional[str] = None,
    details: Optional[Dict[str, str]] = None,
    button_text: Optional[str] = None,
    button_link: Optional[str] = None,
    footer_note: Optional[str] = None,
):
    greeting = f"Hello, {name}" if name else "Hello,"
    footer_note = footer_note or f"This is an automated notification from {String.COMPANY_NAME}. Please do not reply directly to this email."

    return main_structure(f"""
      <tr>
        <td style="padding:35px;">
          <h2 style="color:#333333; text-align:center; margin-bottom:20px;">{title}</h2>
          <p style="color:#555555; font-size:16px; line-height:1.5;">{greeting}</p>
          <p style="color:#555555; font-size:16px; line-height:1.5;">{message}</p>
          {_details_table(details)}
          {_button(button_text, button_link)}
          <p style="color:#999999; font-size:13px; margin-top:25px; text-align:center;">
            {footer_note}
          </p>
        </td>
      </tr>
    """)


def _pack(title: str, body: str) -> Dict[str, str]:
    return {"title": title, "body": body}


class EmailTemplate:
    @staticmethod
    def welcome_email_template(name: str):
        title = f"Welcome to {String.COMPANY_NAME}!"
        body = _body(
            title=title,
            name=name,
            message=f"Thank you for joining {String.COMPANY_NAME}. Your account has been successfully set up and is ready to use.",
            button_text="Get Started",
            button_link="",
            footer_note=f"If you have any questions, the {String.COMPANY_NAME} support team is here to help.",
        )
        return _pack(title, body)

    @staticmethod
    def otp_email_template(name: str, email: str, otp: str):
        title = f"Your OTP Code for {String.COMPANY_NAME} Verification"
        body = _body(
            title=title,
            name=name,
            message="Please use the verification code below to confirm your email address. This code is valid for the next 5 minutes.",
            details={"Email": email, "OTP": otp},
            footer_note="If you did not request this code, you can safely ignore this email.",
        )
        return _pack(title, body)

    @staticmethod
    def login_alert_email_template(name: str, email: str, ip_address: str):
        return EmailTemplate.new_device_login_template(
            name=name,
            device="Unknown device",
            ip_address=ip_address,
            location=None,
            email=email,
        )

    @staticmethod
    def kyc_update_email_template(name: str, status: str):
        title = f"KYC Verification Update for {String.COMPANY_NAME}"
        body = _body(
            title=title,
            name=name,
            message=f"Your KYC verification status has been updated to {status.upper()}.",
            details={"KYC Status": status.upper()},
        )
        return _pack(title, body)

    @staticmethod
    def reset_password_template(name: str, email: str, reset_link: str):
        title = "Reset Your Password"
        body = _body(
            title=title,
            name=name,
            message=f"We received a request to reset the password for your account {email}. Click the button below to set a new password securely.",
            button_text="Reset Password",
            button_link=f"http://192.168.1.100:8000/auth/reset-password/{reset_link}",
            footer_note="This link is valid for the next 15 minutes. If you did not request a password reset, you can safely ignore this email.",
        )
        return _pack(title, body)

    @staticmethod
    def general_notification_template(name: str, title: str, message: str, button_text: str = None, button_link: str = None):
        body = _body(
            title=title,
            name=name,
            message=message,
            button_text=button_text,
            button_link=button_link,
        )
        return _pack(title, body)

    @staticmethod
    def password_changed_template(name: str, changed_at: str, ip_address: str) -> Dict[str, str]:
        title = "Password Changed"
        body = _body(
            title=title,
            name=name,
            message="Your account password was changed successfully. If this was not you, reset your password immediately and contact support.",
            details={"Changed At": changed_at, "IP Address": ip_address},
        )
        return _pack(title, body)

    @staticmethod
    def email_changed_template(name: str, old_email: str, new_email: str) -> Dict[str, str]:
        title = "Email Address Changed"
        body = _body(
            title=title,
            name=name,
            message="The email address on your account has been changed successfully.",
            details={"Old Email": old_email, "New Email": new_email},
            footer_note="If you did not make this change, please contact support immediately.",
        )
        return _pack(title, body)

    @staticmethod
    def two_factor_enabled_template(name: str) -> Dict[str, str]:
        title = "Two-Factor Authentication Enabled"
        body = _body(
            title=title,
            name=name,
            message="Two-factor authentication has been enabled for your account. Your sign-ins now have an extra layer of security.",
        )
        return _pack(title, body)

    @staticmethod
    def two_factor_disabled_template(name: str) -> Dict[str, str]:
        title = "Two-Factor Authentication Disabled"
        body = _body(
            title=title,
            name=name,
            message="Two-factor authentication has been disabled for your account. If this was not you, secure your account immediately.",
        )
        return _pack(title, body)

    @staticmethod
    def new_device_login_template(name: str, device: str, ip_address: str, location: str = None, email: str = None) -> Dict[str, str]:
        title = "New Login Detected"
        details = {
            "Account": email,
            "Device": device,
            "IP Address": ip_address,
            "Location": location,
        }
        body = _body(
            title=title,
            name=name,
            message="We noticed a new login to your account. If this was you, no action is needed.",
            details=details,
            footer_note="If this was not you, please change your password and review your account security.",
        )
        return _pack(title, body)

    @staticmethod
    def account_locked_template(name: str, unlock_time: str = None) -> Dict[str, str]:
        title = "Account Locked"
        details = {"Unlock Time": unlock_time} if unlock_time else None
        body = _body(
            title=title,
            name=name,
            message="Your account has been temporarily locked because of too many failed attempts.",
            details=details,
            footer_note="If you need help accessing your account, please contact support.",
        )
        return _pack(title, body)

    @staticmethod
    def account_unlocked_template(name: str) -> Dict[str, str]:
        title = "Account Unlocked"
        body = _body(
            title=title,
            name=name,
            message="Your account has been unlocked. You can now sign in again.",
        )
        return _pack(title, body)

    @staticmethod
    def email_verification_template(name: str, verification_link: str) -> Dict[str, str]:
        title = "Verify Your Email Address"
        body = _body(
            title=title,
            name=name,
            message=f"Please verify your email address to finish setting up your {String.COMPANY_NAME} account.",
            button_text="Verify Email",
            button_link=verification_link,
            footer_note="If you did not create this account, you can safely ignore this email.",
        )
        return _pack(title, body)

    @staticmethod
    def password_reset_success_template(name: str) -> Dict[str, str]:
        title = "Password Reset Successful"
        body = _body(
            title=title,
            name=name,
            message="Your password has been reset successfully. You can now sign in with your new password.",
        )
        return _pack(title, body)

    @staticmethod
    def recovery_code_template(name: str, recovery_codes: List[str]) -> Dict[str, str]:
        title = "Your Recovery Codes"
        code_rows = "".join(
            f"<div style=\"font-family:monospace; font-size:16px; padding:6px 0; color:#333333;\">{code}</div>"
            for code in recovery_codes
        )
        body = main_structure(f"""
          <tr>
            <td style="padding:35px;">
              <h2 style="color:#333333; text-align:center; margin-bottom:20px;">{title}</h2>
              <p style="color:#555555; font-size:16px; line-height:1.5;">Hello, {name}</p>
              <p style="color:#555555; font-size:16px; line-height:1.5;">
                Save these recovery codes in a secure place. Each code can be used once if you lose access to your two-factor authentication method.
              </p>
              <div style="background-color:#f1f2f6; border-radius:8px; padding:18px; text-align:center; margin:20px 0;">
                {code_rows}
              </div>
              <p style="color:#999999; font-size:13px; margin-top:25px; text-align:center;">
                Do not share these codes with anyone.
              </p>
            </td>
          </tr>
        """)
        return _pack(title, body)

    @staticmethod
    def account_deleted_template(name: str) -> Dict[str, str]:
        title = "Account Deleted"
        body = _body(
            title=title,
            name=name,
            message=f"Your {String.COMPANY_NAME} account has been deleted successfully.",
            footer_note="We are sorry to see you go. If this was a mistake, please contact support.",
        )
        return _pack(title, body)

    @staticmethod
    def account_deactivated_template(name: str, reason: str = None) -> Dict[str, str]:
        title = "Account Deactivated"
        body = _body(
            title=title,
            name=name,
            message="Your account has been deactivated.",
            details={"Reason": reason},
            footer_note="Please contact support if you believe this action was taken by mistake.",
        )
        return _pack(title, body)

    @staticmethod
    def account_reactivated_template(name: str) -> Dict[str, str]:
        title = "Account Reactivated"
        body = _body(
            title=title,
            name=name,
            message="Your account has been reactivated. You can now sign in and use your account again.",
        )
        return _pack(title, body)

    @staticmethod
    def subscription_expiry_template(name: str, expiry_date: str) -> Dict[str, str]:
        title = "Subscription Expiry Notice"
        body = _body(
            title=title,
            name=name,
            message="Your subscription is nearing its expiry date.",
            details={"Expiry Date": expiry_date},
            footer_note=f"Renew before the expiry date to keep using premium {String.COMPANY_NAME} features without interruption.",
        )
        return _pack(title, body)

    @staticmethod
    def maintenance_notification_template(name: str, maintenance_time: str) -> Dict[str, str]:
        title = "Scheduled Maintenance"
        body = _body(
            title=title,
            name=name,
            message=f"{String.COMPANY_NAME} will undergo scheduled maintenance. Some services may be temporarily unavailable during this time.",
            details={"Maintenance Time": maintenance_time},
        )
        return _pack(title, body)

    @staticmethod
    def terms_update_template(name: str) -> Dict[str, str]:
        title = "Terms and Conditions Updated"
        body = _body(
            title=title,
            name=name,
            message=f"We have updated the {String.COMPANY_NAME} terms and conditions. Please review the latest terms when you have a moment.",
        )
        return _pack(title, body)

    @staticmethod
    def admin_alert_template(title: str, message: str) -> Dict[str, str]:
        body = _body(
            title=title,
            name="Admin",
            message=message,
            footer_note=f"This internal alert was generated by {String.COMPANY_NAME}.",
        )
        return _pack(title, body)

    @staticmethod
    def api_key_created_template(name: str, key_name: str) -> Dict[str, str]:
        title = "API Key Created"
        body = _body(
            title=title,
            name=name,
            message="A new API key has been created for your developer account.",
            details={"Key Name": key_name},
            footer_note="If you did not create this key, revoke it immediately and contact support.",
        )
        return _pack(title, body)

    @staticmethod
    def api_key_revoked_template(name: str, key_name: str) -> Dict[str, str]:
        title = "API Key Revoked"
        body = _body(
            title=title,
            name=name,
            message="An API key has been revoked from your developer account.",
            details={"Key Name": key_name},
        )
        return _pack(title, body)


# if __name__ == "__main__":
#     # Example usage
    
#     template = EmailTemplate.welcome_email_template("John Doe")
    
#     print("Title:", template["title"])
#     print("Body:", template["body"])
#     with open("welcome_email.html", "w") as f:
#         f.write(template["body"])
      
    