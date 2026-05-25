import pyotp
import qrcode
import time



class TwoFactorAuth:
    @staticmethod
    def generate_secret() -> str:
        """Generate a base32 secret"""
        return pyotp.random_base32()

    @staticmethod
    def get_qr_uri(user_email: str, issuer: str, secret: str) -> str:
        """Generate provisioning URI"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=issuer
        )
    
    @staticmethod
    def generate_qr_image(uri: str, filename: str = "two_factor.png") -> str:
        """Generate QR code image"""
        if not filename:
            filename = f"totp_{int(time.time())}.png"

        img = qrcode.make(uri)
        img.save(filename)
        return filename

    @staticmethod
    def verify_otp(secret: str, user_code: str) -> bool:
        """Verify user OTP"""
        try:
            totp = pyotp.TOTP(secret)

            # valid_window=1 -> allow +/- 30 second clock drift
            return totp.verify(
                user_code.strip(),
                valid_window=1
            )
        except Exception:
            return False

    @staticmethod
    def generate_otp_from_secret(secret: str) -> str:
        """
        Given a secret, generate the current 6-digit OTP.
        Use for debugging/testing only.
        """
        totp = pyotp.TOTP(secret)
        return totp.now()



# if __name__ == "__main__":
#     secret = "D4GHQ6TV55LEYTOQDWHLLW4XJEUGDK4A"
#     twoaf = TwoFactorAuth()

#     # print(twoaf.generate_secret())
#     # print(twoaf.generate_otp_from_secret(secret))
#     # print(twoaf.verify_otp(secret, input("Enter Code : ")))
    
#     uri = twoaf.get_qr_uri("demo@gmail.com", "PocketPay", secret)
#     twoaf.generate_qr_image(uri)
