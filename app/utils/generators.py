import uuid
import random
import string
from datetime import datetime

"""
USER
TNXR
BANK
"""
class Generators:
    # Unique ID generators
    # @staticmethod
    # def generate_user_id() -> str:
    #     """Generate a unique user ID."""
    #     return "USR"+str(uuid.uuid4().hex.upper())
    
    @staticmethod
    def generate_id(type: str) -> str:
        uid = uuid.uuid4().hex.upper()

        prefixes = {
            "admin": "ADM",
            "user": "USR",
            "bank": "BNK",
            "organization": "ORG",
            "country": "CNT",
            "operator": "OPR",
            "wallet": "WAL",
        }

        return prefixes.get(type, "GEN") + uid



    # Unique transaction ID generator
    @staticmethod
    def generate_transaction_id() -> str:
        """Generate a unique transaction ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"TXN{timestamp}{random_suffix}"


    # OTP generator
    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP."""
        return str(random.randint(100000, 999999))



# if __name__ == "__main__":
#     print(Generators.generate_id("country"))