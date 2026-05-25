# app/utils/auth.py
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from jose import JWTError

from app.constants.colors import AnsiColor
from app.constants.string import String

from app.core.database import get_db
from app.model.admin_table import AdminTable
from app.utils.token import Token



def get_current_admin(request: Request, db: Session = Depends(get_db)) -> AdminTable:
    token = request.cookies.get("admin_access_token")
    if not token:
        print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {token}")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        token_service = Token()
        payload = token_service.decode_token(token)
        admin_id = payload.get("admin_id")

        if not admin_id:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {admin_id}")
            raise HTTPException(status_code=401, detail=String.INVALID_TOKEN)

        admin = db.query(AdminTable).filter(AdminTable.admin_id == admin_id).first()

        if not admin:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {admin}")
            raise HTTPException(status_code=401, detail="Admin not found")

        return admin

    except JWTError:
        print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {JWTError}")
        raise HTTPException(status_code=401, detail=String.INVALID_OR_EXPIRED_TOKEN)
