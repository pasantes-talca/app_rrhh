from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal, verify_csrf
from app.database.session import get_session
from app.modules.auth.models import User
from app.modules.self_service.models import Notification
from app.shared.files import resolve_private_path, save_upload
from .models import EmployeeSupervisor, LeaveRequest, LeaveType
from .schemas import LeaveCreate, LeaveResolution, LeaveTypeView, LeaveView

router = APIRouter(prefix="/licenses", tags=["licenses"])
MANAGEMENT_ROLES = {"administrador", "recursos_humanos"}
ATTACHMENT_TYPES = frozenset({"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "image/jpeg", "image/png"})


def _view(item: LeaveRequest) -> LeaveView:
    return LeaveView(id=item.id, employee_id=item.employee_id, employee_name=item.employee.display_name, type_id=item.type_id, type_name=item.leave_type.name, date_from=item.date_from, date_to=item.date_to, days=item.days, reason=item.reason, status=item.status, supervisor_status=item.supervisor_status, hr_observation=item.hr_observation, supervisor_observation=item.supervisor_observation, has_attachment=bool(item.attachment), created_at=item.created_at)


def _supervised_employee_ids(session: Session, principal: Principal) -> set[int]:
    if principal.employee2_id is None:
        return set()
    source_ids = session.scalars(select(EmployeeSupervisor.employee2_id).where(EmployeeSupervisor.supervisor_employee2_id == principal.employee2_id, EmployeeSupervisor.active.is_(True))).all()
    if not source_ids:
        return set()
    return set(session.scalars(select(User.employee_id).where(User.employee2_id.in_(source_ids), User.employee_id.is_not(None))).all())


def _notify(session: Session, user_id: int, title: str, message: str, reference: int, reference_type: str = "license") -> None:
    existing = session.scalar(select(Notification).where(Notification.user_id == user_id, Notification.reference_type == reference_type, Notification.reference_id == reference))
    if existing is None:
        session.add(Notification(user_id=user_id, title=title, message=message, kind="licencia", reference_type=reference_type, reference_id=reference, read=False, created_at=datetime.utcnow()))


def _supervisors_and_status(session: Session, principal: Principal, leave_type: LeaveType):
    vacation = "vacacion" in leave_type.name.lower().replace("Ã³", "o")
    supervisors = session.scalars(select(EmployeeSupervisor).where(EmployeeSupervisor.employee2_id == principal.employee2_id, EmployeeSupervisor.active.is_(True))).all() if vacation and principal.employee2_id else []
    return supervisors, "Pendiente" if supervisors else ("Sin asignar" if vacation else "No requerido")


def _create_and_notify(session: Session, principal: Principal, leave_type: LeaveType, *, date_from: date, date_to: date, days: Decimal, reason: str | None, attachment: str | None) -> LeaveRequest:
    supervisors, supervisor_status = _supervisors_and_status(session, principal, leave_type)
    item = LeaveRequest(employee_id=principal.employee_id, type_id=leave_type.id, date_from=date_from, date_to=date_to, days=days, reason=reason, attachment=attachment, status="Pendiente", supervisor_status=supervisor_status, created_at=datetime.utcnow())
    session.add(item); session.flush()
    targets = {row.supervisor_employee2_id for row in supervisors}
    if targets:
        recipients = session.scalars(select(User).where(User.employee2_id.in_(targets), User.active.is_(True))).all()
        reference_type = "license_supervisor"
    else:
        recipients = session.scalars(select(User).join(User.role).where(User.active.is_(True), User.role.has(name="recursos_humanos"))).all()
        reference_type = "license_no_supervisor" if supervisor_status == "Sin asignar" else "license_hr"
    for recipient in recipients:
        _notify(session, recipient.id, "Nueva solicitud de licencia", f"{item.employee.display_name} solicitÃ³ {leave_type.name}.", item.id, reference_type)
    session.commit(); session.refresh(item)
    return item


@router.get("/types", response_model=list[LeaveTypeView])
def leave_types(_: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    return session.scalars(select(LeaveType).where(LeaveType.active.is_(True)).order_by(LeaveType.name)).all()


@router.get("", response_model=list[LeaveView])
def list_leaves(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    statement = select(LeaveRequest).order_by(LeaveRequest.date_from.desc())
    if principal.role not in MANAGEMENT_ROLES:
        allowed = _supervised_employee_ids(session, principal)
        clauses = [LeaveRequest.employee_id == principal.employee_id] if principal.employee_id else []
        if allowed:
            clauses.append(LeaveRequest.employee_id.in_(allowed))
        if not clauses:
            return []
        statement = statement.where(or_(*clauses))
    return [_view(item) for item in session.scalars(statement).unique().all()]


@router.post("", response_model=LeaveView, status_code=status.HTTP_201_CREATED)
def create_leave(payload: LeaveCreate, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    if principal.employee_id is None:
        raise HTTPException(status_code=409, detail="user_has_no_employee")
    leave_type = session.get(LeaveType, payload.type_id)
    if leave_type is None or not leave_type.active:
        raise HTTPException(status_code=400, detail="invalid_leave_type")
    if leave_type.attachment_required:
        raise HTTPException(status_code=422, detail="attachment_required_use_upload_endpoint")
    return _view(_create_and_notify(session, principal, leave_type, date_from=payload.date_from, date_to=payload.date_to, days=payload.days, reason=payload.reason, attachment=None))


@router.post("/upload", response_model=LeaveView, status_code=status.HTTP_201_CREATED)
async def create_leave_with_attachment(request: Request, type_id: int = Form(), date_from: str = Form(), date_to: str = Form(), days: str = Form(), reason: str | None = Form(None), attachment: UploadFile | None = File(None), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    if principal.employee_id is None:
        raise HTTPException(status_code=409, detail="user_has_no_employee")
    leave_type = session.get(LeaveType, type_id)
    if leave_type is None or not leave_type.active:
        raise HTTPException(status_code=400, detail="invalid_leave_type")
    if leave_type.attachment_required and attachment is None:
        raise HTTPException(status_code=422, detail="attachment_required")
    try:
        start, end, amount = date.fromisoformat(date_from), date.fromisoformat(date_to), Decimal(days)
    except (ValueError, InvalidOperation):
        raise HTTPException(status_code=422, detail="invalid_leave_period")
    if end < start or amount <= 0 or amount > 365:
        raise HTTPException(status_code=422, detail="invalid_leave_period")
    path = await save_upload(attachment, "licenses", ATTACHMENT_TYPES) if attachment else None
    return _view(_create_and_notify(session, principal, leave_type, date_from=start, date_to=end, days=amount, reason=reason, attachment=path))


@router.post("/{leave_id}/supervisor-resolution", response_model=LeaveView)
def supervisor_resolution(leave_id: int, payload: LeaveResolution, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    item = session.get(LeaveRequest, leave_id)
    if item is None:
        raise HTTPException(status_code=404, detail="license_not_found")
    if item.employee_id not in _supervised_employee_ids(session, principal) or item.status != "Pendiente" or item.supervisor_status != "Pendiente":
        raise HTTPException(status_code=403, detail="license_not_available_for_supervisor")
    item.supervisor_status, item.supervisor_resolved_by, item.supervisor_resolved_at, item.supervisor_observation = payload.decision, principal.user_id, datetime.utcnow(), payload.observation
    owner = session.scalar(select(User).where(User.employee_id == item.employee_id, User.active.is_(True)))
    if payload.decision == "Rechazada":
        item.status, item.resolved_at = "Rechazada", datetime.utcnow()
        if owner:
            _notify(session, owner.id, "ActualizaciÃ³n de vacaciones", "Tu solicitud de vacaciones fue rechazada por supervisiÃ³n.", item.id, "license_supervisor_result")
    else:
        for recipient in session.scalars(select(User).join(User.role).where(User.active.is_(True), User.role.has(name="recursos_humanos"))).all():
            _notify(session, recipient.id, "Vacaciones aprobadas por supervisiÃ³n", f"{item.employee.display_name} tiene una solicitud pendiente de resoluciÃ³n final.", item.id, "license_hr")
        if owner:
            _notify(session, owner.id, "ActualizaciÃ³n de vacaciones", "Tu supervisor aprobÃ³ la solicitud. Ahora serÃ¡ revisada por RR. HH.", item.id, "license_supervisor_result")
    session.commit(); session.refresh(item)
    return _view(item)


@router.post("/{leave_id}/hr-resolution", response_model=LeaveView)
def hr_resolution(leave_id: int, payload: LeaveResolution, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    if principal.role not in MANAGEMENT_ROLES:
        raise HTTPException(status_code=403, detail="permission_denied")
    item = session.get(LeaveRequest, leave_id)
    if item is None:
        raise HTTPException(status_code=404, detail="license_not_found")
    if item.status != "Pendiente" or item.supervisor_status not in {"Aprobada", "No requerido", "Sin asignar"}:
        raise HTTPException(status_code=409, detail="license_not_ready_for_hr")
    item.status, item.hr_observation, item.resolved_by, item.resolved_at = payload.decision, payload.observation, principal.user_id, datetime.utcnow()
    owner = session.scalar(select(User).where(User.employee_id == item.employee_id, User.active.is_(True)))
    if owner:
        _notify(session, owner.id, f"Licencia {payload.decision.lower()}", f"Tu solicitud fue {payload.decision.lower()} por RR. HH.", item.id, "license")
    session.commit(); session.refresh(item)
    return _view(item)


@router.get("/{leave_id}/attachment")
def leave_attachment(leave_id: int, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    item = session.get(LeaveRequest, leave_id)
    if item is None or not item.attachment:
        raise HTTPException(status_code=404, detail="attachment_not_found")
    allowed = principal.role in MANAGEMENT_ROLES or principal.employee_id == item.employee_id or item.employee_id in _supervised_employee_ids(session, principal)
    if not allowed:
        raise HTTPException(status_code=404, detail="attachment_not_found")
    return FileResponse(resolve_private_path(item.attachment))
