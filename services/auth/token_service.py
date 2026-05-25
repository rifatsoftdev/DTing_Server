from fastapi import HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.constants import ENV, String, AnsiColor
from app.schema import AccessTokenRequest, GlobalResponse, FCMTokenRequest
from app.model import SessionTable
from app.utils import Hashing


class TokenGenerators:
    def __init__(self, db: Session):
        self.SECRET_KEY = ENV.SECRET_KEY
        self.ALGORITHM = ENV.ALGORITHM

    def _create_token(
        self,
        data: dict,
        token_type: str = "access",
        expire_day: float = 0,
        expire_min: float = 0
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=expire_day, minutes=expire_min)
        to_encode.update({
            "exp": expire,
            "type": token_type
        })
        
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        
    def _decode_token(self, token: str):
        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            return payload
        
        except JWTError as j:
            return None
    

class TokenService(TokenGenerators):
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request,
        authorization: str
    ):
        super().__init__(db)
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization

    
    
