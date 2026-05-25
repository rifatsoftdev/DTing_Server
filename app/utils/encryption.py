import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# from app.constants.env import ENV




class Encryption:
    def __init__(self, password: str, salt: bytes):
        """
        password: user provided secret (string)
        salt: random bytes (store this safely, ex: DB / ENV)
        """

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=200_000,   # high iteration = slow brute-force
        )

        key = base64.urlsafe_b64encode(
            kdf.derive(password.encode())
        )

        self.fernet = Fernet(key)

    def encrypt(self, value: str) -> str:
        if not value:
            return value
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        if not value:
            return value
        return self.fernet.decrypt(value.encode()).decode()




# if __name__ == "__main__":
#     enc = Encryption("password", ENV.SALT)
#     print(enc.encrypt("value"))
#     print(enc.decrypt(enc.encrypt("value")))