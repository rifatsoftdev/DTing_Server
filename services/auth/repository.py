from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.constants import AnsiColor
from app.model import *
from app.constants.string import String



class Repository:
    def __init__(self, db: Session):
        self.db = db

    def _check_user_already_exists(
        self,
        email: str = None,
        phone: str = None,
        country_code: str = None
    ) -> UserTable | None:
        user: UserTable | None = self.db.query(UserTable).filter(
            or_(
                UserTable.email_address == email if email else None,
                and_(
                    UserTable.phone_number == phone if phone else None,
                    UserTable.country_code == country_code if country_code else None
                )
            )
        ).first()

        return user

    def _get_admin(self, admin_id: str) -> AdminTable:
        admin: AdminTable = self.db.query(AdminTable).filter(
            AdminTable.admin_id == admin_id
        ).first()
    
        if not admin:
            print(f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}     User with ID {admin_id} not found on AdminTable")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=String.USER_NOT_FOUND
            )

        return admin

    def _get_user(self, user_id: str) -> UserTable:
        user: UserTable = self.db.query(UserTable).filter(
            UserTable.user_id == user_id
        ).first()
    
        if not user:
            print(f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}     User with ID {user_id} not found on UserTable")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=String.USER_NOT_FOUND
            )

        return user

    def _get_settings(self, user_id: str) -> SettingsTable:
        settings = self.db.query(SettingsTable).filter(
            SettingsTable.user_id == user_id
        ).first()

        if not settings:
            print(f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}     User with ID {user_id} not found on SettingsTable")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=String.SETTINGS_NOT_FOUND
            )
        
        return settings

    def _get_kyc(self, user_id: str) -> KYCTable:
        kyc: KYCTable = self.db.query(KYCTable).filter(
            KYCTable.user_id == user_id
        ).first()

        if not kyc:
            print(f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}     User with ID {user_id} not found on KYCTable")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=String.KYC_NOT_FOUND
            )
        
        return kyc

    def _get_session(self, user_id: str, device_id: str, device_uuid: str, admin=False) -> SessionTable:
        id_column = SessionTable.admin_id if admin else SessionTable.user_id
        session = self.db.query(SessionTable).filter(
            id_column == user_id,
            SessionTable.device_id == device_id,
            SessionTable.device_uuid == device_uuid,
            SessionTable.is_login == True
        ).first()

        if not session:
            print(f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}     User with ID {user_id} not found on SessionTable")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=String.SESSION_NOT_FOUND
            )
        
        return session

    def _get_dev(self, user_id: str) -> DevTable:
        dev: DevTable = self.db.query(DevTable).filter(
            DevTable.user_id == user_id
        ).first()

        if not dev:
            print(f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}     User with ID {user_id} not found on DevTable")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=String.DEV_NOT_FOUND
            )
        
        return dev




# ==============================================================================
# ==============================================================================
