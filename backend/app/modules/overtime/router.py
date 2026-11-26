from datetime import date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import Principal, current_principal, verify_csrf
from app.database.session import get_session
from app.modules.auth.models import User
from app.modules.self_service.models import Notification
from .exporter import export_workbook
from .importer import import_report
from .models import Overtime
from .schemas import ImportResult, OvertimeClear, OvertimeCreate, OvertimeDecision, OvertimeDelete, OvertimeSummary, OvertimeView

router = APIRouter(prefix="/overtime", tags=["overtime"])
MANAGEMENT_ROLES = {"administrador", "recursos_humanos"}


def _require_management(principal: Principal) -> None:
    if principal.role not in MANAGEMENT_ROLES:
        raise HTTPException(status_code=403, detail="permission_denied")


def _view(item: Overtime) -> OvertimeView:
    manual = bool(item.loader and item.loader.role.name == "empleado")
    return OvertimeView(id=item.id, employee_id=item.employee_id, employee_name=item.employee.display_name, employee_number=item.employee.employee_number, date=item.date, time_from=item.time_from, time_to=item.time_to, hours=item.hours, reason=item.reason, state=item.state, observations=item.observations, manually_loaded_by_employee=manual, created_at=item.created_at)


def _notify_user(session: Session, user_id: int, title: str, message: str, reference: int, reference_type: str) -> None:
    existing = session.scalar(select(Notification).where(Notification.user_id == user_id, Notification.reference_type == reference_type, Notification.reference_id == reference))
    if existing is None:
        session.add(Notification(user_id=user_id, title=title, message=message, kind="horas_extra", reference_type=reference_type, reference_id=reference, read=False, created_at=datetime.utcnow()))


@router.get("", response_model=OvertimeSummary)
def list_overtime(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    statement = select(Overtime).order_by(Overtime.date.desc())
    if principal.role not in MANAGEMENT_ROLES:
        if principal.employee_id is None:
            return OvertimeSummary(items=[], pending_manual=0)
        statement = statement.where(Overtime.employee_id == principal.employee_id)
    items = session.scalars(statement).unique().all()
    views = [_view(item) for item in items]
    return OvertimeSummary(items=views, pending_manual=sum(1 for item in views if item.state == "Pendiente" and item.manually_loaded_by_employee))


@router.post("", response_model=OvertimeView, status_code=201)
def create_overtime(payload: OvertimeCreate, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    if principal.role in MANAGEMENT_ROLES:
        raise HTTPException(status_code=403, detail="manual_entry_is_for_employees")
    if principal.employee_id is None:
        raise HTTPException(status_code=409, detail="user_has_no_employee")
    duplicate = session.scalar(select(Overtime).where(Overtime.employee_id == principal.employee_id, Overtime.loaded_by == principal.user_id, Overtime.date == payload.date, Overtime.state.in_(["Pendiente", "Aprobado"])))
    if duplicate:
        raise HTTPException(status_code=409, detail="overtime_already_submitted_for_date")
    item = Overtime(employee_id=principal.employee_id, date=payload.date, hours=payload.hours, reason=payload.reason.strip() if payload.reason else None, state="Pendiente", loaded_by=principal.user_id, created_at=datetime.utcnow())
    session.add(item); session.flush()
    for user in session.scalars(select(User).where(User.active.is_(True), User.role.has(name="recursos_humanos"))).all():
        if user.id != principal.user_id:
            _notify_user(session, user.id, "Nueva solicitud de horas extra", f"{item.employee.display_name} informó horas extra para el {item.date:%d/%m/%Y}.", item.id, "horas_extra_rrhh")
    session.commit(); session.refresh(item)
    return _view(item)


@router.post("/{overtime_id}/approve", response_model=OvertimeView)
def approve(overtime_id: int, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); _require_management(principal)
    item = session.get(Overtime, overtime_id)
    if item is None: raise HTTPException(status_code=404, detail="overtime_not_found")
    item.state = "Aprobado"
    owner = session.scalar(select(User).where(User.employee_id == item.employee_id, User.active.is_(True)))
    if owner: _notify_user(session, owner.id, "Horas extra aprobadas", f"Tus horas extra del {item.date:%d/%m/%Y} fueron aprobadas.", item.id, "horas_extra")
    session.commit(); session.refresh(item); return _view(item)


@router.post("/{overtime_id}/reject", response_model=OvertimeView)
def reject(overtime_id: int, payload: OvertimeDecision, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); _require_management(principal)
    item = session.get(Overtime, overtime_id)
    if item is None: raise HTTPException(status_code=404, detail="overtime_not_found")
    item.state, item.observations = "Rechazado", payload.observation
    owner = session.scalar(select(User).where(User.employee_id == item.employee_id, User.active.is_(True)))
    if owner:
        message = f"Tus horas extra del {item.date:%d/%m/%Y} fueron rechazadas." + (f" Observación: {payload.observation}" if payload.observation else "")
        _notify_user(session, owner.id, "Horas extra rechazadas", message, item.id, "horas_extra")
    session.commit(); session.refresh(item); return _view(item)


@router.post("/import", response_model=ImportResult)
async def import_overtime(request: Request, report: UploadFile = File(), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); _require_management(principal)
    filename = report.filename or "reporte"
    if not filename.lower().endswith((".csv", ".xls", ".xlsx", ".html", ".htm")):
        raise HTTPException(status_code=415, detail="unsupported_report_type")
    content = await report.read(get_settings().max_upload_bytes + 1); await report.close()
    if len(content) > get_settings().max_upload_bytes: raise HTTPException(status_code=413, detail="file_too_large")
    try:
        created, skipped, errors = import_report(session, content, filename, principal.user_id)
        session.commit()
    except ValueError as error:
        session.rollback(); raise HTTPException(status_code=422, detail=str(error)) from error
    return ImportResult(created=created, skipped=skipped, errors=errors)


@router.post("/delete", status_code=204)
def delete_selected(payload: OvertimeDelete, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); _require_management(principal)
    session.execute(delete(Overtime).where(Overtime.id.in_(set(payload.ids)))); session.commit()


@router.post("/clear", status_code=204)
def clear_all(_: OvertimeClear, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); _require_management(principal)
    session.execute(delete(Overtime)); session.commit()


@router.get("/export")
def export(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _require_management(principal)
    records = session.scalars(select(Overtime).where(Overtime.state != "Rechazado").order_by(Overtime.date).options()).unique().all()
    records = [item for item in records if not item.loader or item.loader.role.name != "empleado" or item.state == "Aprobado"]
    if not records: raise HTTPException(status_code=404, detail="no_overtime_to_export")
    output = export_workbook(session, records)
    filename = f"HorasExtra_{datetime.now():%Y%m%d}.xlsx"
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{filename}"'})
