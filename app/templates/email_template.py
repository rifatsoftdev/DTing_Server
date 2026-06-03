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



