from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import SlidingWindowLimiter
from app.core.security import Principal, csrf_token, current_principal, verify_csrf
from app.database.session import get_session
from app.modules.auth.models import User, UserSession
from app.modules.auth.passwords import hash_password, verify_password
from app.modules.auth.schemas import CsrfResponse, LoginRequest, LoginResponse, PasswordChangeRequest, UserView
from app.modules.auth.service import authenticate, configured_int, open_session, permissions_for

router = APIRouter(prefix="/auth", tags=["authentication"])
_settings = get_settings()
_login_limiter = SlidingWindowLimiter(_settings.login_max_attempts, _settings.login_window_seconds)


def _view(user: User, principal: Principal) -> UserView:
    return UserView(id=user.id, username=user.username, display_name=user.display_name, role=principal.role, employee_id=user.employee_id, employee2_id=user.employee2_id, must_change_password=user.must_change_password, permissions=sorted(principal.permissions))


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, response: Response, session: Session = Depends(get_session)):
    client_ip = request.client.host if request.client else "unknown"
    limit_key = f"{client_ip}:{payload.username.strip().casefold()}"
    if not _login_limiter.allow(limit_key):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="too_many_login_attempts", headers={"Retry-After": str(_settings.login_window_seconds)})
    result = authenticate(session, payload.username, payload.password)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")
    _login_limiter.reset(limit_key)
    user, principal = result
    record = open_session(session, user, request.client.host if request.client else None, request.headers.get("user-agent"))
    settings = _settings
    response.set_cookie(settings.session_cookie_name, record.id, httponly=True, secure=settings.cookie_secure, samesite="strict", max_age=configured_int(session, "session_max_minutes", settings.session_max_minutes) * 60, path="/")
    return LoginResponse(user=_view(user, principal), csrf_token=csrf_token(record.id))


@router.get("/me", response_model=UserView)
def me(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    user = session.get(User, principal.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return _view(user, principal)


@router.get("/csrf", response_model=CsrfResponse)
def get_csrf(request: Request, _: Principal = Depends(current_principal)):
    session_id = request.cookies.get(get_settings().session_cookie_name)
    if not session_id:
        raise HTTPException(status_code=401, detail="authentication_required")
    return CsrfResponse(csrf_token=csrf_token(session_id))


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, session: Session = Depends(get_session)):
    verify_csrf(request)
    settings = get_settings()
    session_id = request.cookies.get(settings.session_cookie_name)
    record = session.get(UserSession, session_id) if session_id else None
    if record and record.closed_at is None:
        record.closed_at = datetime.utcnow()
        record.closed_reason = "Cierre de sesión"
        session.commit()
    response.delete_cookie(settings.session_cookie_name, path="/")


@router.post("/password", status_code=204)
def change_password(payload: PasswordChangeRequest, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    user = session.get(User, principal.user_id)
    if user is None or not verify_password(user.password_hash, payload.current_password)[0]:
        raise HTTPException(status_code=400, detail="current_password_invalid")
    if len(payload.new_password) < configured_int(session, "password_min_length", 10):
        raise HTTPException(status_code=422, detail="password_too_short")
    if verify_password(user.password_hash, payload.new_password)[0]:
        raise HTTPException(status_code=422, detail="password_must_change")
    user.password_hash = hash_password(payload.new_password)
    user.must_change_password = False
    session.commit()
