from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.constants import AnsiColor
from app.model import UserTable
from app.schema import GlobalResponse
from services.auth.user_verification import UserVerificationService


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        protected_prefixes: list[str] | None = None,
        public_paths: list[str] | None = None
    ):
        super().__init__(app)
        self.protected_prefixes = protected_prefixes or []
        self.public_paths = public_paths or []

    async def dispatch(self, request, call_next):

        if (
            request.method == "OPTIONS"
            or self._is_public_path(request.url.path)
            or not self._is_protected_path(request.url.path)
        ):
            return await call_next(request)

        client_type = request.headers.get("X-Client-Type")

        # fallback detection (UA sniffing) - eta easily spoof kora jay,
        # tai eta sirf "helper", actual security na. Real security er
        # jonno X-Client-Signature (HMAC) approach use korar kotha
        # already aagei discuss hoyeche - shei layer aagei add korben.
        ua = request.headers.get("user-agent", "").lower()

        if not client_type:
            if "okhttp" in ua:
                client_type = "android"
            elif "mozilla" in ua:
                client_type = "web"
            else:
                client_type = "unknown"

        request.state.client_type = client_type

        # BLOCK unknown clients
        if client_type not in ["android", "web"]:
            return JSONResponse(
                status_code=403,
                content={"message": "Invalid client"}
            )

        # ============================================================
        # Client type onujayi token kothai theke nibo shetai thik kora
        # ============================================================
        token: str | None = None

        if client_type == "android":
            # App -> Authorization header e Bearer token
            authorization = request.headers.get("authorization")
            if authorization and authorization.lower().startswith("bearer "):
                token = authorization.split(" ", 1)[1].strip()

        elif client_type == "web":
            # Web -> Cookie e token (cookie naam apnar login flow er
            # cookie set korar shomoy ja diyechen, shetar shathe match
            # korben. ekhane "access_token" placeholder, replace korben.)
            token = request.cookies.get("access_token")

        if not token:
            return self._unauthorized(
                "Missing authentication token",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        # ============================================================
        # Token format same rekhe (Bearer <token>) purono service
        # UserVerificationService ke unchanged rakha hoyeche
        # ============================================================
        db: Session = SessionLocal()

        try:
            userVerificationService = UserVerificationService(
                db=db,
                authorization=f"Bearer {token}"
            )

            user: UserTable = userVerificationService.verify_user_authorization()

        except Exception as exc:
            status_code = getattr(exc, "status_code", status.HTTP_401_UNAUTHORIZED)
            detail = getattr(exc, "detail", "Invalid or Expired Token")
            message = detail if isinstance(detail, str) else str(detail)
            return self._unauthorized(message, status_code=status_code)
        finally:
            db.close()

        request.state.current_user = user

        return await call_next(request)

    def _is_protected_path(self, path: str) -> bool:
        return any(path == prefix or path.startswith(f"{prefix}/") for prefix in self.protected_prefixes)

    def _is_public_path(self, path: str) -> bool:
        return path in self.public_paths

    def _unauthorized(
        self,
        message: str,
        status_code: int = status.HTTP_401_UNAUTHORIZED
    ) -> JSONResponse:
        response = GlobalResponse(
            status_code=status_code,
            success=False,
            action="unauthorized",
            message=message,
            data={}
        )
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump()
        )




# ==============================================================================
# ==============================================================================
