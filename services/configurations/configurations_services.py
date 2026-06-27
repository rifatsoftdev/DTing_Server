from typing import Any, Dict
from fastapi import BackgroundTasks, Request, HTTPException, status
from sqlalchemy.orm import Session

from app.model import AppConfigTable
from app.schema import GlobalResponse



class ConfigurationsServices:
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks = None,
        request: Request = None,
        authorization: str = None
    ):
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization


    def get_email_settings(self) -> Dict:
        config: AppConfigTable = self.db.query(AppConfigTable).filter(
            AppConfigTable.key == "email_settings"
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email settings not found"
            )
        
        return config.value

    def get_push_settings(self) -> Dict:
        config: AppConfigTable = self.db.query(AppConfigTable).filter(
            AppConfigTable.key == "push_settings"
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Push settings not found"
            )
        
        return config.value

    def get_sms_settings(self) -> Dict:
        config: AppConfigTable = self.db.query(AppConfigTable).filter(
            AppConfigTable.key == "sms_settings"
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SMS settings not found"
            )
        
        return config.value
    
    def get_signup_settings(self) -> Dict:
        config: AppConfigTable = self.db.query(AppConfigTable).filter(
            AppConfigTable.key == "signup_settings"
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signup settings not found"
            )
        
        return config.value

    def get_signin_settings(self) -> Dict:
        config: AppConfigTable = self.db.query(AppConfigTable).filter(
            AppConfigTable.key == "signin_settings"
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signin settings not found"
            )
        
        return config.value
    

    def update_config(self, payload: Dict) -> GlobalResponse:
        if (self.authorization == None):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        
