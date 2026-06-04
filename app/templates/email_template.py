from typing import Dict, List
from app.constants import String



BRAND_COLOR = "#1E88E5"

HEADER = f"""
<html>
  <body style="margin:0; padding:0; font-family:'Helvetica Neue',Arial,sans-serif; background-color:#f5f6fa;">
      <table align="center" width="100%" style="max-width:600px; margin:auto; background-color:#ffffff; border-radius:10px; overflow:hidden; box-shadow:0 0 15px rgba(0,0,0,0.1);">
        
          <!-- Header -->
          <tr>
              <td style="background-color:#1E88E5; padding:25px; text-align:center;">
                  <img src="{String.COMPANY_LOGO}" alt="{String.COMPANY_NAME} Logo" width="120" style="display:block; margin:auto;">
              </td>
          </tr>
"""

FOOTER = f"""
<tr>
            <td style="background-color:#f1f2f6; padding:20px; text-align:center; font-size:12px; color:#777777;">
              {String.COMPANY_NAME} | {String.COMPANY_ADDRESS} | {String.COMPANY_CONTACT}<br>
              &copy; {String.COMPANY_NAME} {2026}
            </td>
          </tr>

      </table>
  </body>
</html>
"""


class EmailTemplate:
    @staticmethod
    def welcome_template(name: str):
        return {
            "title": f"Welcome to {String.COMPANY_NAME}!",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Welcome, {name}!</h2>
                      
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Thank you for joining <strong>{String.COMPANY_NAME}</strong>! We're excited to have you on board.
                    </p>

                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Get ready to explore our services and enjoy seamless experiences with your new account.
                    </p>

                    <p style="color:#555555; font-size:16px; line-height:1.5; margin-top:25px;">
                        If you have any questions, our support team is always here to help.
                    </p>

                    <div style="text-align:center; margin-top:30px;">
                        <a href="" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:14px 28px; border-radius:6px; font-size:16px; font-weight:bold;">Get Started</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def otp_template(name: str, email: str, otp: str):
        return {
            "title": f"Your OTP Code for {String.COMPANY_NAME}",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Welcome, {name}!</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        You're almost ready to start using <strong>{String.COMPANY_NAME}</strong>.  
                        Please use the verification code below to confirm your email address.
                    </p>

                    <div style="margin:25px 0;">
                        <span style="display:inline-block; font-size:36px; font-weight:bold; color:#1E88E5; padding:15px 30px; border:2px dashed #1E88E5; border-radius:8px;">{otp}</span>
                    </div>

                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        This code is valid for the next 5 minutes.  
                        If you did not request this, please ignore this email.
                    </p>

                    <p style="color:#999999; font-size:13px; margin-top:30px;">
                        Thank you for choosing {String.COMPANY_NAME}. Let's get started!
                    </p>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def login_alert_template(name: str, ip_address: str):
        return {
            "title": "New Login Detected 🔐",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Hi {name},</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        We detected a new login to your <strong>{String.COMPANY_NAME}</strong> account.
                    </p>

                    <div style="background-color:#f1f2f6; padding:18px; border-radius:8px; margin:20px 0; text-align:left; font-size:14px; color:#333333;">
                        <p style="margin:6px 0;"><strong>IP Address:</strong> {ip_address}</p>
                        <p style="margin:6px 0;"><strong>Location:</strong> Unknown</p>
                        <p style="margin:6px 0;"><strong>Time:</strong> Just now</p>
                    </div>

                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        If this was you, you can safely ignore this message. If you did not sign in, please secure your account immediately by resetting your password and reviewing recent activity.
                    </p>

                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#E53935; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Secure Account</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def kyc_update_template(name: str, status: str):
        return {
            "title": "KYC Verification Update",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Hello, {name}</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Your KYC verification status has been updated to <strong>{status.upper()}</strong>.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        If you have any questions about your KYC status, please contact our support team.
                    </p>
                    <p style="color:#999999; font-size:13px; margin-top:30px;">
                        Thank you for being a valued member of {String.COMPANY_NAME}.
                    </p>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def reset_password_template(name: str, email: str, reset_link: str):
        return {
            "title": "Reset Your Password",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Hello, {name}</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        We received a request to reset the password for your account <strong>{email}</strong>.  
                        Click the button below to set a new password securely.
                    </p>

                    <a href="http://192.168.1.100:8000/auth/reset-password/{reset_link}" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:15px 30px; border-radius:5px; font-size:16px; margin:25px 0;">Reset Password</a>

                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        This link is valid for the next 15 minutes.  
                        If you did not request a password reset, you can safely ignore this email — your account is safe.
                    </p>

                    <p style="color:#999999; font-size:13px; margin-top:30px;">
                        Thank you for using {String.COMPANY_NAME}. Stay secure!
                    </p>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def general_notification_template(name: str, title: str, message: str, button_text: str = None, button_link: str = None):
        button_html = f'<a href="{button_link}" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:15px 30px; border-radius:5px; font-size:16px; margin:25px 0;">{button_text}</a>' if button_text and button_link else ""
        return {
            "title": title,
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Hello, {name}</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        {message}
                    </p>
                    {button_html}
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def link_google_template():
        return {
            "title": "Google Account Linked Successfully",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Security Alert</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Your <strong>{String.COMPANY_NAME}</strong> account has been successfully linked with Google.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        You can now use your Google account to sign in more quickly and securely.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5; margin-top:20px;">
                        If you did not perform this action, please contact our support team immediately.
                    </p>
                </td>
            </tr>
            {FOOTER}
            """
        }
    
    @staticmethod
    def password_changed_template(name: str, changed_at: str, ip_address: str) -> Dict[str, str]:
        return {
            "title": "Password Changed Successfully",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Password Updated</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, the password for your <strong>{String.COMPANY_NAME}</strong> account was recently changed.
                    </p>

                    <div style="background-color:#f1f2f6; padding:18px; border-radius:8px; margin:20px 0; text-align:left; font-size:14px; color:#333333;">
                        <p style="margin:6px 0;"><strong>Time:</strong> {changed_at}</p>
                        <p style="margin:6px 0;"><strong>IP Address:</strong> {ip_address}</p>
                    </div>

                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        If you made this change, you can disregard this email. If you did not change your password, please secure your account immediately.
                    </p>

                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#E53935; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Secure My Account</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def email_changed_template(name: str, old_email: str, new_email: str) -> Dict[str, str]:
        return {
            "title": "Email Address Changed",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Email Updated</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, the email address for your <strong>{String.COMPANY_NAME}</strong> account has been changed.
                    </p>

                    <div style="background-color:#f1f2f6; padding:18px; border-radius:8px; margin:20px 0; text-align:left; font-size:14px; color:#333333;">
                        <p style="margin:6px 0;"><strong>Old Email:</strong> {old_email}</p>
                        <p style="margin:6px 0;"><strong>New Email:</strong> {new_email}</p>
                    </div>

                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        If you did not make this change, please contact our support team immediately to secure your account.
                    </p>

                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#E53935; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Contact Support</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def two_factor_enabled_template(name: str) -> Dict[str, str]:
        return {
            "title": "Two-Factor Authentication Enabled",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">2FA Enabled</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, two-factor authentication (2FA) has been successfully enabled on your <strong>{String.COMPANY_NAME}</strong> account.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        Your account now has an extra layer of security. You will be prompted for a code whenever you sign in.
                    </p>
                    <p style="color:#999999; font-size:13px; margin-top:30px;">
                        If you did not enable this, please contact our support team immediately.
                    </p>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def two_factor_disabled_template(name: str) -> Dict[str, str]:
        return {
            "title": "Two-Factor Authentication Disabled",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#D32F2F; margin-bottom:15px;">2FA Disabled</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, two-factor authentication (2FA) has been <strong>disabled</strong> on your <strong>{String.COMPANY_NAME}</strong> account.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        Your account is now less secure. If you did not perform this action, please secure your account immediately.
                    </p>
                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#E53935; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Secure My Account</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def account_locked_template(name: str, unlock_time: str = None) -> Dict[str, str]:
        unlock_text = f" Try again after {unlock_time}." if unlock_time else ""
        return {
            "title": "Account Temporarily Locked",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#D32F2F; margin-bottom:15px;">Security Alert: Account Locked</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, your <strong>{String.COMPANY_NAME}</strong> account has been temporarily locked due to multiple failed login attempts.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        This is a security measure to protect your information.{unlock_text}
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5; margin-top:20px;">
                        If this wasn't you, we recommend resetting your password once the account is unlocked.
                    </p>
                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Reset Password</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def account_unlocked_template(name: str) -> Dict[str, str]:
        return {
            "title": "Account Unlocked",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Account Unlocked</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, your <strong>{String.COMPANY_NAME}</strong> account has been successfully unlocked.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        You can now sign in to your account as usual.
                    </p>
                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Sign In Now</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def email_verification_template(name: str, verification_link: str) -> Dict[str, str]:
        return {
            "title": "Verify Your Email Address",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Verify Your Email</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, thank you for signing up with <strong>{String.COMPANY_NAME}</strong>.  
                        Please click the button below to verify your email address and complete your registration.
                    </p>

                    <a href="{verification_link}" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:15px 30px; border-radius:5px; font-size:16px; margin:25px 0;">Verify Email</a>

                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        If the button above doesn't work, copy and paste the following link into your browser:
                    </p>
                    <p style="color:#1E88E5; font-size:13px; word-break:break-all;">
                        {verification_link}
                    </p>

                    <p style="color:#999999; font-size:13px; margin-top:30px;">
                        If you did not create an account, no further action is required.
                    </p>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def password_reset_success_template(name: str) -> Dict[str, str]:
        return {
            "title": "Password Reset Successful",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Password Reset Successful</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, your password for <strong>{String.COMPANY_NAME}</strong> has been successfully reset.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        You can now log in using your new password. If you did not perform this action, please contact our support team immediately.
                    </p>
                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Log In</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def recovery_code_template(name: str, recovery_codes: List[str]) -> Dict[str, str]:
        return {
            "title": "Your Recovery Codes",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">New Recovery Codes</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, new recovery codes have been generated for your <strong>{String.COMPANY_NAME}</strong> account.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        Use these codes to access your account if you lose your two-factor authentication device. <strong>Keep them in a safe place.</strong>
                    </p>

                    <div style="background-color:#f1f2f6; padding:20px; border-radius:8px; margin:25px 0; font-family:monospace; font-size:18px; color:#333333; letter-spacing: 1px;">
                        {"<br>".join(recovery_codes)}
                    </div>

                    <p style="color:#D32F2F; font-size:13px; font-weight:bold;">
                        Each code can only be used once.
                    </p>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def account_deleted_template(name: str) -> Dict[str, str]:
        return {
            "title": "Account Deleted Successfully",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Account Deleted</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, your <strong>{String.COMPANY_NAME}</strong> account has been successfully deleted as per your request.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        We're sorry to see you go. All your personal data has been removed from our active systems.
                    </p>
                    <p style="color:#999999; font-size:13px; margin-top:30px;">
                        If this was a mistake, please contact our support team immediately.
                    </p>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def account_deactivated_template(name: str, reason: str = None) -> Dict[str, str]:
        reason_text = f" Reason: {reason}." if reason else ""
        return {
            "title": "Account Deactivated",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#D32F2F; margin-bottom:15px;">Account Deactivated</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, your <strong>{String.COMPANY_NAME}</strong> account has been deactivated.{reason_text}
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        While deactivated, you will not be able to access your account or services. If you believe this is an error, please reach out to our support team.
                    </p>
                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Contact Support</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def account_reactivated_template(name: str) -> Dict[str, str]:
        return {
            "title": "Account Reactivated",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Account Reactivated</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, your <strong>{String.COMPANY_NAME}</strong> account has been successfully reactivated.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        Welcome back! You can now sign in and access all your services as usual.
                    </p>
                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Sign In Now</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def subscription_expiry_template(name: str, expiry_date: str) -> Dict[str, str]:
        return {
            "title": "Subscription Expiry Notice",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Subscription Expiring Soon</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, your subscription for <strong>{String.COMPANY_NAME}</strong> is set to expire on <strong>{expiry_date}</strong>.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        To ensure uninterrupted access to all our premium features, please renew your subscription before the expiry date.
                    </p>
                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Renew Subscription</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def maintenance_notification_template(name: str, maintenance_time: str) -> Dict[str, str]:
        return {
            "title": "Scheduled Maintenance Notice",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">System Maintenance</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, please be advised that <strong>{String.COMPANY_NAME}</strong> will undergo scheduled maintenance on <strong>{maintenance_time}</strong>.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        During this period, some services may be temporarily unavailable. We apologize for any inconvenience this may cause and appreciate your patience.
                    </p>
                    <p style="color:#999999; font-size:13px; margin-top:30px;">
                        Thank you for your understanding.
                    </p>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def terms_update_template(name: str) -> Dict[str, str]:
        return {
            "title": "Terms and Conditions Updated",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">Terms Update</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, we are updating our Terms and Conditions to better serve our community.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        These changes reflect our commitment to transparency and the security of your data. We encourage you to review the updated terms.
                    </p>
                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Review Updated Terms</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def admin_alert_template(title: str, message: str) -> Dict[str, str]:
        return {
            "title": title,
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#D32F2F; margin-bottom:15px;">System Alert</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        {message}
                    </p>
                    <p style="color:#999999; font-size:13px; margin-top:30px;">
                        This is an automated administrative notification from {String.COMPANY_NAME}.
                    </p>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def api_key_created_template(name: str, key_name: str) -> Dict[str, str]:
        return {
            "title": "API Key Created",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#333333; margin-bottom:15px;">New API Key Created</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, a new API key named <strong>'{key_name}'</strong> has been successfully created for your account.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        If you did not perform this action, please log in to your dashboard and revoke the key immediately to secure your account.
                    </p>
                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">Manage API Keys</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }

    @staticmethod
    def api_key_revoked_template(name: str, key_name: str) -> Dict[str, str]:
        return {
            "title": "API Key Revoked",
            "body": f"""
            {HEADER}
            <tr>
                <td style="padding:35px; text-align:center;">
                    <h2 style="color:#D32F2F; margin-bottom:15px;">API Key Revoked</h2>
                    <p style="color:#555555; font-size:16px; line-height:1.5;">
                        Hello {name}, the API key named <strong>'{key_name}'</strong> has been successfully revoked and can no longer be used.
                    </p>
                    <p style="color:#555555; font-size:15px; line-height:1.5;">
                        If you did not perform this action, please contact our support team immediately.
                    </p>
                    <div style="text-align:center; margin-top:25px;">
                        <a href="" style="display:inline-block; background-color:#1E88E5; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px; font-size:15px; font-weight:bold;">View API Keys</a>
                    </div>
                </td>
            </tr>
            {FOOTER}
            """
        }


