import csv, io, platform, time
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, func, or_, select, text
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.security import Principal, current_principal, verify_csrf
from app.database.session import get_session
from app.modules.auth.models import Role, User, UserPermission, UserSession
from app.modules.auth.passwords import hash_password
from app.modules.licenses.models import LegacyEmployee
from .models import AuditEvent, SystemConfiguration, SystemError
from .schemas import ActivityReportRow, AdminSummary, AdminUserInput, AdminUserView, AuditView, ErrorReview, ErrorView, PasswordReset, PermissionInput, RoleView, SecuritySettings, SessionView, SystemStatus

router = APIRouter(prefix="/administration", tags=["administration"])
MODULES = ("dashboard", "empleados", "licencias", "horas_extra", "sanciones", "noticias", "documentos", "estructura", "notificaciones", "ausentismo", "vacaciones", "indicadores")
ACTIONS = ("consultar", "crear", "editar", "anular", "exportar", "configurar")

def _admin(principal: Principal):
    if principal.role != "administrador": raise HTTPException(status_code=403, detail="administrator_required")
def _editable(user: User, principal: Principal) -> bool: return user.id != principal.user_id and not user.protected_account and user.role.name != "administrador"
def _user(user: User, principal: Principal) -> AdminUserView: return AdminUserView(id=user.id, username=user.username, display_name=user.display_name, email=user.email, employee_id=user.employee_id, role_id=user.role_id, role=user.role.name, active=user.active, protected=user.protected_account, editable=_editable(user, principal), last_access=user.last_access)
def _config(session: Session, key: str, default: int) -> int:
    item = session.get(SystemConfiguration, key)
    try: return int(item.value) if item else default
    except ValueError: return default

@router.get("/summary", response_model=AdminSummary)
def summary(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _admin(principal); since = datetime.utcnow() - timedelta(days=30)
    return AdminSummary(users=session.scalar(select(func.count()).select_from(User)) or 0, active_users=session.scalar(select(func.count()).select_from(User).where(User.active.is_(True))) or 0, operations_30_days=session.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.created_at >= since)) or 0, unreviewed_errors=session.scalar(select(func.count()).select_from(SystemError).where(SystemError.reviewed.is_(False))) or 0, open_sessions=session.scalar(select(func.count()).select_from(UserSession).where(UserSession.closed_at.is_(None))) or 0)

@router.get("/roles", response_model=list[RoleView])
def roles(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _admin(principal); return session.scalars(select(Role).where(Role.active.is_(True), Role.name.in_(("empleado", "supervisor", "recursos_humanos", "gerencia"))).order_by(Role.name)).all()

@router.get("/users", response_model=list[AdminUserView])
def users(q: str = "", principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _admin(principal); statement = select(User)
    if q.strip(): pattern=f"%{q.strip()}%"; statement=statement.where(or_(User.username.ilike(pattern), User.display_name.ilike(pattern), User.email.ilike(pattern)))
    return [_user(item, principal) for item in session.scalars(statement.order_by(User.username)).unique().all()]

def _validate_account(payload: AdminUserInput, session: Session, user_id: int | None = None):
    if session.scalar(select(User.id).where(User.username == payload.username.strip(), User.id != (user_id or 0))): raise HTTPException(status_code=409, detail="username_exists")
    role = session.get(Role, payload.role_id)
    if role is None or role.name == "administrador": raise HTTPException(status_code=422, detail="invalid_assignable_role")
    if payload.employee_id and session.get(LegacyEmployee, payload.employee_id) is None: raise HTTPException(status_code=422, detail="invalid_employee")

@router.post("/users", response_model=AdminUserView, status_code=201)
def create_user(payload: AdminUserInput, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); _admin(principal); _validate_account(payload, session)
    minimum=_config(session,"password_min_length",10)
    if not payload.password or len(payload.password)<minimum: raise HTTPException(status_code=422, detail="password_too_short")
    item=User(username=payload.username.strip(),display_name=payload.display_name.strip(),email=(payload.email or "").strip() or None,employee_id=payload.employee_id,employee2_id=None,role_id=payload.role_id,password_hash=hash_password(payload.password),active=payload.active,must_change_password=True,protected_account=False,created_at=datetime.utcnow())
    session.add(item); session.commit(); session.refresh(item); return _user(item,principal)

@router.put("/users/{user_id}", response_model=AdminUserView)
def update_user(user_id:int,payload:AdminUserInput,request:Request,principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    verify_csrf(request); _admin(principal); item=session.get(User,user_id)
    if item is None: raise HTTPException(status_code=404,detail="user_not_found")
    if not _editable(item,principal): raise HTTPException(status_code=403,detail="protected_user")
    _validate_account(payload,session,user_id); item.username=payload.username.strip();item.display_name=payload.display_name.strip();item.email=(payload.email or "").strip() or None;item.employee_id=payload.employee_id;item.role_id=payload.role_id;item.active=payload.active
    if not item.active:
        now=datetime.utcnow()
        for record in session.scalars(select(UserSession).where(UserSession.user_id==item.id,UserSession.closed_at.is_(None))).all(): record.closed_at=now;record.closed_by=principal.user_id;record.closed_reason="Cuenta desactivada"
    session.commit();session.refresh(item);return _user(item,principal)

@router.post("/users/{user_id}/password", status_code=204)
def reset_password(user_id:int,payload:PasswordReset,request:Request,principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    verify_csrf(request);_admin(principal);item=session.get(User,user_id)
    if item is None:raise HTTPException(status_code=404,detail="user_not_found")
    if not _editable(item,principal):raise HTTPException(status_code=403,detail="protected_user")
    if len(payload.password)<_config(session,"password_min_length",10):raise HTTPException(status_code=422,detail="password_too_short")
    item.password_hash=hash_password(payload.password);item.must_change_password=True;session.commit()

@router.get("/users/{user_id}/permissions", response_model=list[str])
def user_permissions(user_id:int,principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    _admin(principal);item=session.get(User,user_id)
    if item is None:raise HTTPException(status_code=404,detail="user_not_found")
    if not _editable(item,principal):raise HTTPException(status_code=403,detail="protected_user")
    return [f"{row.module}:{row.action}" for row in session.scalars(select(UserPermission).where(UserPermission.user_id==user_id,UserPermission.allowed.is_(True),UserPermission.module!="_config")).all()]

@router.put("/users/{user_id}/permissions", status_code=204)
def set_permissions(user_id:int,payload:PermissionInput,request:Request,principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    verify_csrf(request);_admin(principal);item=session.get(User,user_id)
    if item is None:raise HTTPException(status_code=404,detail="user_not_found")
    if not _editable(item,principal):raise HTTPException(status_code=403,detail="protected_user")
    parsed=[]
    for value in set(payload.permissions):
        try:module,action=value.split(":",1)
        except ValueError:raise HTTPException(status_code=422,detail="invalid_permission")
        if module not in MODULES or action not in ACTIONS:raise HTTPException(status_code=422,detail="invalid_permission")
        parsed.append((module,action))
    session.execute(delete(UserPermission).where(UserPermission.user_id==user_id));session.add(UserPermission(user_id=user_id,module="_config",action="_configured",allowed=True,assigned_by=principal.user_id,updated_at=datetime.utcnow()))
    for module,action in parsed:session.add(UserPermission(user_id=user_id,module=module,action=action,allowed=True,assigned_by=principal.user_id,updated_at=datetime.utcnow()))
    session.commit()

@router.get("/audit", response_model=list[AuditView])
def audit(module:str="",username:str="",action:str="",principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    _admin(principal);statement=select(AuditEvent)
    if module:statement=statement.where(AuditEvent.module==module)
    if action:statement=statement.where(AuditEvent.action==action)
    if username:statement=statement.where(AuditEvent.username.ilike(f"%{username}%"))
    return session.scalars(statement.order_by(AuditEvent.created_at.desc()).limit(500)).all()

@router.get("/audit.csv")
def audit_csv(principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    rows=audit(principal=principal,session=session);output=io.StringIO();writer=csv.writer(output);writer.writerow(["Fecha","Usuario","MÃ³dulo","AcciÃ³n","MÃ©todo","Detalle","IP","Estado"])
    for row in rows:writer.writerow([row.created_at.isoformat(" "),row.username,row.module,row.action,row.method,row.detail,row.ip,row.http_status])
    return StreamingResponse(iter(["\ufeff"+output.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=auditoria.csv"})

def _activity_rows(session: Session, date_from: str = "", date_to: str = ""):
    statement = select(AuditEvent.username, AuditEvent.module, AuditEvent.action, func.count(AuditEvent.id)).group_by(AuditEvent.username, AuditEvent.module, AuditEvent.action).order_by(func.count(AuditEvent.id).desc())
    if date_from:
        try: statement = statement.where(AuditEvent.created_at >= datetime.fromisoformat(date_from))
        except ValueError: raise HTTPException(status_code=422, detail="invalid_date_from")
    if date_to:
        try: statement = statement.where(AuditEvent.created_at < datetime.fromisoformat(date_to) + timedelta(days=1))
        except ValueError: raise HTTPException(status_code=422, detail="invalid_date_to")
    return session.execute(statement).all()

@router.get("/reports/activity", response_model=list[ActivityReportRow])
def activity_report(date_from:str="",date_to:str="",principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    _admin(principal)
    return [ActivityReportRow(username=row[0],module=row[1],action=row[2],total=row[3]) for row in _activity_rows(session,date_from,date_to)]

@router.get("/reports/activity.csv")
def activity_report_csv(date_from:str="",date_to:str="",principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    _admin(principal); output=io.StringIO(); writer=csv.writer(output); writer.writerow(["Usuario","Módulo","Acción","Cantidad"])
    writer.writerows(_activity_rows(session,date_from,date_to))
    return StreamingResponse(iter(["\ufeff"+output.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=reporte_actividad.csv"})

@router.get("/errors", response_model=list[ErrorView])
def errors(principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):_admin(principal);return session.scalars(select(SystemError).order_by(SystemError.created_at.desc()).limit(300)).all()
@router.post("/errors/{error_id}/review", response_model=ErrorView)
def review_error(error_id:int,payload:ErrorReview,request:Request,principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    verify_csrf(request);_admin(principal);item=session.get(SystemError,error_id)
    if item is None:raise HTTPException(status_code=404,detail="error_not_found")
    item.reviewed=True;item.reviewed_by=principal.user_id;item.reviewed_at=datetime.utcnow();item.review_reason=payload.reason.strip();session.commit();session.refresh(item);return item

@router.get("/security", response_model=SecuritySettings)
def security(principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):_admin(principal);return SecuritySettings(password_min_length=_config(session,"password_min_length",10),session_max_minutes=_config(session,"session_max_minutes",480))
@router.put("/security", response_model=SecuritySettings)
def update_security(payload:SecuritySettings,request:Request,principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    verify_csrf(request);_admin(principal)
    for key,value,description in (("password_min_length",payload.password_min_length,"Longitud mÃ­nima de nuevas contraseÃ±as"),("session_max_minutes",payload.session_max_minutes,"DuraciÃ³n mÃ¡xima de sesiÃ³n en minutos")):
        item=session.get(SystemConfiguration,key) or SystemConfiguration(key=key,value=str(value),updated_at=datetime.utcnow());item.value=str(value);item.description=description;item.updated_by=principal.user_id;item.updated_at=datetime.utcnow();session.add(item)
    session.commit();return payload

@router.get("/sessions",response_model=list[SessionView])
def sessions(principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    _admin(principal);rows=session.execute(select(UserSession,User.username).join(User,UserSession.user_id==User.id).where(UserSession.closed_at.is_(None)).order_by(UserSession.last_activity.desc())).all();return [SessionView(id=item.id,username=username,ip=item.ip,started_at=item.started_at,last_activity=item.last_activity) for item,username in rows]
@router.post("/sessions/{session_id}/close",status_code=204)
def close_session(session_id:str,request:Request,principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    verify_csrf(request);_admin(principal);item=session.get(UserSession,session_id);user=session.get(User,item.user_id) if item else None
    if item is None:raise HTTPException(status_code=404,detail="session_not_found")
    if item.user_id==principal.user_id or (user and user.protected_account):raise HTTPException(status_code=403,detail="protected_session")
    item.closed_at=datetime.utcnow();item.closed_by=principal.user_id;item.closed_reason="Cierre administrativo";session.commit()

@router.get("/system",response_model=SystemStatus)
def system(principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    _admin(principal);start=time.perf_counter();version=str(session.execute(text("select version()")).scalar());name=str(session.execute(text("select current_database()")).scalar());session.execute(text("select 1"));latency=round((time.perf_counter()-start)*1000,2);settings=get_settings()
    return SystemStatus(database_version=version,database_latency_ms=latency,database_name=name,schema_name="rrhh",python_version=platform.python_version(),environment=settings.environment,controls={"session_secret_configured":bool(settings.session_secret.get_secret_value()),"secure_cookie":settings.cookie_secure,"trilay_read_only":True})
