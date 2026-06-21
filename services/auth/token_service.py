import uuid
from fastapi import HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.constants import ENV, String, AnsiColor
from app.schema import AccessTokenRequest, GlobalResponse, FCMTokenRequest
from app.model import SessionTable
from app.utils import Hashing


class TokenGenerators:
    def __init__(self):
        with open(ENV.PRIVATE_KEY_PATH, "r") as f:
            self.PRIVATE_KEY = f.read()

        with open(ENV.PUBLIC_KEY_PATH, "r") as f:
            self.PUBLIC_KEY = f.read()

        self.ALGORITHM = "RS256"

    def _create_token(
        self,
        data: dict,
        token_type: str = "access",
        expire_day: float = 0,
        expire_min: float = 0
    ) -> tuple[str, str]:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=expire_day, minutes=expire_min)
        jti = str(uuid.uuid4())   # unique token id - revoke/rotation track korar jonno

        to_encode.update({
            "exp": expire,
            "type": token_type,
            "jti": jti,
        })

        token = jwt.encode(to_encode, self.PRIVATE_KEY, algorithm=self.ALGORITHM)
        return token, jti   # jti return korlam, DB e save korar jonno proyojon hobe

    def _decode_token(
        self,
        token: str,
        audience: str | list[str] | None = None,
        issuer: str | None = None
    ):
        try:
            decode_kwargs = {
                "key": self.PUBLIC_KEY,
                "algorithms": [self.ALGORITHM],
            }
            
            if issuer is not None:
                decode_kwargs["issuer"] = issuer

            # Skip audience validation in jwt.decode() when audience is a multi-item list
            # python-jose doesn't support list audience validation
            if audience is not None and isinstance(audience, list) and len(audience) > 1:
                # Don't pass audience to jwt.decode - validate manually after
                pass
            elif audience is not None:
                decode_kwargs["audience"] = audience

            payload = jwt.decode(token, **decode_kwargs)
            
            print(f"{AnsiColor.CYAN}DEBUG{AnsiColor.RESET}:     audience param: {audience}, payload aud: {payload.get('aud')}")
            
            if audience is not None and isinstance(audience, list) and len(audience) > 1:
                token_aud = payload.get("aud", [])
                if isinstance(token_aud, str):
                    token_aud = [token_aud]
                expected_audiences = set(audience)
                token_audiences = set(token_aud)
                if not expected_audiences.intersection(token_audiences):
                    raise JWTError("Invalid audience")

            return payload

        except JWTError as j:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     JWT Error: {j}")
            return None


class TokenService(TokenGenerators):
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request,
        authorization: str
    ):
        super().__init__()
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization

    def create_access_token(self, user_id: str, device_id: str, device_uuid: str) -> str:
        payload = {
            "user_id": user_id,
            "device_id": device_id,
            "device_uuid": device_uuid,
            "iss": f"auth.{ENV.MAIN_DOMAIN}",
            "aud": ENV.ALLOWED_AUDIENCES,        # access token -> সব authorized service e valid
            "iat": datetime.utcnow(),
        }
        token, _ = self._create_token(
            data=payload,
            token_type="access",
            expire_min=ENV.ACCESS_EXPIRE
        )
        return token

    def create_refresh_token(self, user_id: str, device_id: str, device_uuid: str) -> str:
        payload = {
            "user_id": user_id,
            "device_id": device_id,
            "device_uuid": device_uuid,
            "iss": f"auth.{ENV.MAIN_DOMAIN}",
            "aud": f"auth.{ENV.MAIN_DOMAIN}",
            "iat": datetime.utcnow(),
        }
        token, jti = self._create_token(
            data=payload,
            token_type="refresh",
            expire_day=ENV.REFRESH_EXPIRE
        )

        # ---- DB e session record save kora (revoke/rotation er jonno) ----
        # session = SessionTable(
        #     user_id=user_id,
        #     device_id=device_id,
        #     device_uuid=device_uuid,
        #     jti=jti,
        #     refresh_token_hash=Hashing.hash(token),   # raw token DB e direct save na kore hash rakha better
        #     expires_at=datetime.utcnow() + timedelta(days=ENV.REFRESH_EXPIRE),
        #     is_revoked=False,
        # )
        # self.db.add(session)
        # self.db.commit()

        return token

    def verify_access_token(self, token: str) -> dict | None:
        payload = self._decode_token(
            token,
            audience=ENV.ALLOWED_AUDIENCES,
            issuer=f"auth.{ENV.MAIN_DOMAIN}",
        )
        if payload and payload.get("type") == "access":
            return payload
        
        return None

    def verify_refresh_token(self, token: str) -> dict | None:
        payload = self._decode_token(
            token,
            audience=f"auth.{ENV.MAIN_DOMAIN}",
            issuer=f"auth.{ENV.MAIN_DOMAIN}",
        )

        if not payload or payload.get("type") != "refresh":
            return None

        # ---- DB e check kora -> revoked hoyeche ki na ----
        # session = (
        #     self.db.query(SessionTable)
        #     .filter(SessionTable.jti == payload.get("jti"), SessionTable.is_revoked == False)
        #     .first()
        # )
        # if not session:
        #     return None  # revoked othoba kothao pawa jay nai

        return payload





# ==============================================================================
# ==============================================================================
