from fastapi import HTTPException, status
from datetime import datetime, timedelta
import pytz




def utc6dhaka():
    dhaka = pytz.timezone("Asia/Dhaka")
    return datetime.now(dhaka)


class Helpers:
    @staticmethod
    def utc6dhaka():
        dhaka = pytz.timezone("Asia/Dhaka")
        return datetime.now(dhaka)

    @staticmethod
    def authorization(authorization: str, advanced: bool = False) -> str:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header"
            )

        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )

        access_token = authorization.split(" ")[1]

        return access_token

    @staticmethod
    def print_payload(payload):
        for i, j in payload:
            print(f"{i} : {j}")
    
    @staticmethod
    def minutes_to_timedelta(minutes: int):
        return timedelta(minutes=minutes)
    
    @staticmethod
    def format_datetime(value):
        return value.strftime("%Y:%m:%d %I:%M:%S %p") if value else None


# if __name__ == "__main__":
#     print(Helpers.utc6dhaka())
    
