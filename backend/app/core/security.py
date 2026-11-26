from dataclasses import dataclass
from hashlib import sha256
import hmac

from fastapi import Depends, HTTPException, Request, status

from app.core.config import get_settings


@dataclass(frozen=True)
class Principal:
    user_id: int
    role: str
    employee_id: int | None
    permissions: frozenset[str]
    employee2_id: int | None = None


def current_principal(request: Request) -> Principal:
    principal = getattr(request.state, "principal", None)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication_required")
    return principal


def require_permission(permission: str):
    def dependency(principal: Principal = Depends(current_principal)):
        if "*" not in principal.permissions and permission not in principal.permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission_denied")
        return principal
    return dependency


def csrf_token(session_id: str) -> str:
    secret = get_settings().session_secret.get_secret_value().encode()
    return hmac.new(secret, session_id.encode(), sha256).hexdigest()


def verify_csrf(request: Request) -> None:
    session_id = request.cookies.get(get_settings().session_cookie_name)
    supplied = request.headers.get("X-CSRF-Token", "")
    if not session_id or not hmac.compare_digest(supplied, csrf_token(session_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="csrf_validation_failed")

