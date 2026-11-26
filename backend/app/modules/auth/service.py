from datetime import datetime, timedelta
import secrets

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import Principal
from app.modules.auth.models import User, UserPermission, UserSession
from app.modules.auth.passwords import hash_password, verify_password

ROLE_DEFAULTS: dict[str, frozenset[str]] = {
    "administrador": frozenset({"*"}),
    "recursos_humanos": frozenset({"employees:read", "licenses:manage", "documents:manage", "news:manage", "absence:read"}),
    "gerencia": frozenset({"employees:read", "absence:read", "indicators:read", "vacations:read_all"}),
    "supervisor": frozenset({"team:read", "licenses:supervise"}),
    "empleado": frozenset({"profile:read", "profile:update", "self_service:read"}),
}

LEGACY_PERMISSION_MAP = {
    ("empleados", "consultar"): "employees:read",
    ("licencias", "consultar"): "licenses:manage",
    ("licencias", "editar"): "licenses:manage",
    ("documentos", "consultar"): "documents:manage",
    ("documentos", "crear"): "documents:manage",
    ("documentos", "editar"): "documents:manage",
    ("noticias", "consultar"): "news:manage",
    ("noticias", "crear"): "news:manage",
    ("noticias", "editar"): "news:manage",
    ("ausentismo", "consultar"): "absence:read",
    ("vacaciones", "consultar"): "vacations:read_all",
    ("indicadores", "consultar"): "indicators:read",
}


def configured_int(session: Session, key: str, default: int) -> int:
    try:
        value = session.execute(text("select valor from rrhh.configuracion_sistema where clave = :key"), {"key": key}).scalar()
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def permissions_for(session: Session, user: User) -> frozenset[str]:
    rows = session.scalars(select(UserPermission).where(UserPermission.user_id == user.id)).all()
    configured = any(row.module == "_config" and row.action == "_configured" for row in rows)
    if configured:
        base = set()
        if user.role.name in {"recursos_humanos", "gerencia"}:
            base.add("absence:read")
        if user.role.name == "gerencia":
            base.add("indicators:read")
    else:
        base = set(ROLE_DEFAULTS.get(user.role.name, frozenset()))
    for row in rows:
        if row.module == "_config":
            continue
        permission = LEGACY_PERMISSION_MAP.get((row.module, row.action), f"{row.module}:{row.action}")
        if row.allowed:
            base.add(permission)
        else:
            base.discard(permission)
    return frozenset(base)


def principal_for(session: Session, user: User) -> Principal:
    return Principal(user.id, user.role.name, user.employee_id, permissions_for(session, user), user.employee2_id)


def authenticate(session: Session, username: str, password: str) -> tuple[User, Principal] | None:
    user = session.scalar(select(User).where(User.username == username))
    if user is None or not user.active:
        return None
    valid, rehash = verify_password(user.password_hash, password)
    if not valid:
        return None
    if rehash:
        user.password_hash = hash_password(password)
    user.last_access = datetime.utcnow()
    principal = principal_for(session, user)
    session.commit()
    return user, principal


def open_session(session: Session, user: User, ip: str | None, user_agent: str | None) -> UserSession:
    now = datetime.utcnow()
    record = UserSession(id=secrets.token_hex(32), user_id=user.id, ip=ip, user_agent=user_agent, started_at=now, last_activity=now)
    session.add(record)
    session.commit()
    return record


def resolve_session(session: Session, session_id: str) -> Principal | None:
    record = session.get(UserSession, session_id)
    if record is None or record.closed_at is not None:
        return None
    now = datetime.utcnow()
    maximum = configured_int(session, "session_max_minutes", get_settings().session_max_minutes)
    if now - record.last_activity > timedelta(minutes=maximum):
        record.closed_at = now
        record.closed_reason = "Sesión vencida"
        session.commit()
        return None
    user = session.get(User, record.user_id)
    if user is None or not user.active:
        return None
    record.last_activity = now
    session.commit()
    return principal_for(session, user)
