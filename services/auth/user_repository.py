from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.model import *
from app.utils.hashing import Hashing
from app.constants.string import String



class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def check_user_already_exists(
        self,
        email: str = None,
        phone: str = None,
        country_code: str = None
    ) -> UserTable | None:
        filters = []

        if email:
            filters.append(UserTable.email_address == email)

        if phone:
            phone_filter = UserTable.phone_number == phone
            if country_code:
                phone_filter = phone_filter & (UserTable.country_code == country_code)
            filters.append(phone_filter)

        if not filters:
            return False

        user = self.db.query(UserTable).filter(or_(*filters)).first()

        return user
    
    
    