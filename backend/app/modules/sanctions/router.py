from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal, verify_csrf
from app.database.session import get_session
from app.modules.auth.models import User
from app.modules.licenses.models import LegacyEmployee
from app.modules.self_service.models import Notification
from app.shared.files import resolve_private_path, save_upload
from .models import Sanction
from .schemas import SanctionEmployee, SanctionSummary, SanctionView

router = APIRouter(prefix="/sanctions", tags=["sanctions"])
MANAGEMENT_ROLES = {"administrador", "recursos_humanos"}
FILE_TYPES = frozenset({"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "image/jpeg", "image/png"})
KINDS = {"Apercibimiento", "Llamado de atención", "Suspensión", "Otra"}
STATES = {"Borrador", "Notificada", "Archivada"}


def _require_management(principal: Principal) -> None:
    if principal.role not in MANAGEMENT_ROLES:
        raise HTTPException(status_code=403, detail="permission_denied")


def _view(item: Sanction) -> SanctionView:
    remaining = max((item.date_to - date.today()).days, 0) if item.date_to else None
    return SanctionView(id=item.id, employee_id=item.employee_id, employee_name=item.employee.display_name, employee_number=item.employee.employee_number, kind=item.kind, date=item.date, date_from=item.date_from, date_to=item.date_to, days=item.days, remaining_days=remaining, reason=item.reason, description=item.description, observations=item.observations, state=item.state, has_file=bool(item.file_path), original_filename=item.original_filename, notified_at=item.notified_at)


def _validate(kind: str, state: str, date_from: date | None, date_to: date | None, days: Decimal | None) -> None:
    if kind not in KINDS or state not in STATES:
        raise HTTPException(status_code=422, detail="invalid_sanction_value")
    if kind == "Suspensión" and (date_from is None or date_to is None or days is None):
        raise HTTPException(status_code=422, detail="suspension_period_required")
    if date_from and date_to and date_to < date_from:
        raise HTTPException(status_code=422, detail="invalid_suspension_period")
    if days is not None and not Decimal("0.5") <= days <= Decimal("365"):
        raise HTTPException(status_code=422, detail="invalid_suspension_days")


def _notify(item: Sanction, session: Session) -> None:
    user = session.scalar(select(User).where(User.employee_id == item.employee_id, User.active.is_(True)))
    if user is None:
        return
    existing = session.scalar(select(Notification).where(Notification.user_id == user.id, Notification.reference_type == "sancion", Notification.reference_id == item.id))
    if existing:
        return
    message = f"Se registró una medida de tipo {item.kind} con fecha {item.date:%d/%m/%Y}. Motivo: {item.reason}."
    if item.kind == "Suspensión" and item.date_from and item.date_to:
        message += f" Período: {item.date_from:%d/%m/%Y} al {item.date_to:%d/%m/%Y}."
    session.add(Notification(user_id=user.id, title="Nueva medida disciplinaria notificada", message=message, kind="sancion", reference_type="sancion", reference_id=item.id, read=False, created_at=datetime.utcnow()))


@router.get("/employees", response_model=list[SanctionEmployee])
def active_employees(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _require_management(principal)
    return session.scalars(select(LegacyEmployee).where(LegacyEmployee.state == "Activo").order_by(LegacyEmployee.display_name)).all()


@router.get("", response_model=SanctionSummary)
def list_sanctions(q: str = "", kind: str = "", state: str = "", principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _require_management(principal)
    statement = select(Sanction)
    if q.strip():
        pattern = f"%{q.strip()}%"
        statement = statement.join(Sanction.employee).where(or_(LegacyEmployee.display_name.ilike(pattern), LegacyEmployee.employee_number.ilike(pattern), LegacyEmployee.document_number.ilike(pattern), Sanction.reason.ilike(pattern)))
    if kind:
        statement = statement.where(Sanction.kind == kind)
    if state:
        statement = statement.where(Sanction.state == state)
    items = session.scalars(statement.order_by(Sanction.date.desc(), Sanction.created_at.desc())).unique().all()
    total = session.scalar(select(func.count()).select_from(Sanction)) or 0
    drafts = session.scalar(select(func.count()).select_from(Sanction).where(Sanction.state == "Borrador")) or 0
    notified = session.scalar(select(func.count()).select_from(Sanction).where(Sanction.state == "Notificada")) or 0
    suspensions = session.scalar(select(func.count()).select_from(Sanction).where(Sanction.kind == "Suspensión")) or 0
    return SanctionSummary(total=total, drafts=drafts, notified=notified, suspensions=suspensions, items=[_view(item) for item in items])


@router.get("/active", response_model=list[SanctionView])
def active_sanctions(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    statement = select(Sanction).where(Sanction.state == "Notificada", or_(Sanction.date_to.is_(None), Sanction.date_to >= date.today()))
    if principal.role not in MANAGEMENT_ROLES:
        if principal.employee_id is None:
            return []
        statement = statement.where(Sanction.employee_id == principal.employee_id)
    return [_view(item) for item in session.scalars(statement.order_by(Sanction.date_to.asc().nullslast(), Sanction.notified_at.desc())).unique().all()]


@router.post("", response_model=SanctionView, status_code=201)
async def create_sanction(request: Request, employee_id: int = Form(), kind: str = Form(), sanction_date: date = Form(), date_from: date | None = Form(None), date_to: date | None = Form(None), days: Decimal | None = Form(None), reason: str = Form(min_length=1, max_length=200), description: str | None = Form(None), observations: str | None = Form(None), state: str = Form(), attachment: UploadFile | None = File(None), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); _require_management(principal); _validate(kind, state, date_from, date_to, days)
    employee = session.get(LegacyEmployee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="employee_not_found")
    file_path = await save_upload(attachment, "sanctions_private", FILE_TYPES) if attachment else None
    item = Sanction(employee_id=employee_id, kind=kind, date=sanction_date, date_from=date_from if kind == "Suspensión" else None, date_to=date_to if kind == "Suspensión" else None, days=days if kind == "Suspensión" else None, reason=reason.strip(), description=description, observations=observations, original_filename=attachment.filename if attachment else None, file_path=file_path, state=state, notified_at=datetime.utcnow() if state == "Notificada" else None, created_by=principal.user_id, created_at=datetime.utcnow())
    session.add(item); session.flush()
    if state == "Notificada": _notify(item, session)
    session.commit(); session.refresh(item)
    return _view(item)


@router.put("/{sanction_id}", response_model=SanctionView)
async def update_sanction(sanction_id: int, request: Request, employee_id: int = Form(), kind: str = Form(), sanction_date: date = Form(), date_from: date | None = Form(None), date_to: date | None = Form(None), days: Decimal | None = Form(None), reason: str = Form(min_length=1, max_length=200), description: str | None = Form(None), observations: str | None = Form(None), state: str = Form(), attachment: UploadFile | None = File(None), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); _require_management(principal); _validate(kind, state, date_from, date_to, days)
    item = session.get(Sanction, sanction_id)
    if item is None: raise HTTPException(status_code=404, detail="sanction_not_found")
    previous_state = item.state
    item.employee_id, item.kind, item.date, item.reason = employee_id, kind, sanction_date, reason.strip()
    item.date_from, item.date_to, item.days = (date_from, date_to, days) if kind == "Suspensión" else (None, None, None)
    item.description, item.observations, item.state = description, observations, state
    if attachment:
        item.file_path = await save_upload(attachment, "sanctions_private", FILE_TYPES)
        item.original_filename = attachment.filename
    if state == "Notificada" and previous_state != "Notificada": item.notified_at = datetime.utcnow()
    if state == "Notificada": _notify(item, session)
    session.commit(); session.refresh(item)
    return _view(item)


@router.get("/{sanction_id}/file")
def sanction_file(sanction_id: int, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _require_management(principal)
    item = session.get(Sanction, sanction_id)
    if item is None or not item.file_path: raise HTTPException(status_code=404, detail="file_not_found")
    relative = item.file_path if "/" in item.file_path or "\\" in item.file_path else str(Path("sanctions_private") / item.file_path)
    return FileResponse(resolve_private_path(relative), filename=item.original_filename)
