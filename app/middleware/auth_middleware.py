from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import SessionLocal
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

        authorization = request.headers.get("authorization")
        if not authorization:
            return self._unauthorized("Missing Authorization header")

        if not authorization.startswith("Bearer "):
            return self._unauthorized("Invalid token format")

        access_token = authorization.split(" ", 1)[1].strip()
        if not access_token:
            return self._unauthorized("Invalid Token")

        db = SessionLocal()
        try:
            verifier = UserVerificationService(db=db, request=request, authorization=authorization)
            user_id = verifier.verify_access_token(access_token=access_token)
        except Exception as exc:
            status_code = getattr(exc, "status_code", status.HTTP_401_UNAUTHORIZED)
            detail = getattr(exc, "detail", "Invalid or Expired Token")
            message = detail if isinstance(detail, str) else str(detail)
            return self._unauthorized(message, status_code=status_code)
        finally:
            db.close()

        request.state.user_id = user_id
        request.state.access_token = access_token

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
            success=False,
            message=message,
            data={}
        )
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump()
        )
