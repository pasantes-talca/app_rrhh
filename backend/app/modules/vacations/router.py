from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal
from app.database.session import get_session
from app.modules.auth.models import User
from app.modules.employees.models import EmployeeReadModel
from app.modules.licenses.models import LeaveRequest
from .models import VacationBalance, VacationMovement
from .schemas import VacationCalendar, VacationEvent, VacationSummary
from .service import non_negative, seniority_months_at_year_end, vacation_days_for_seniority

router = APIRouter(prefix="/vacations", tags=["vacations"])
MANAGEMENT_ROLES = {"administrador", "recursos_humanos", "gerencia"}


def _is_vacation(item: LeaveRequest) -> bool:
    return "vacacion" in item.leave_type.name.lower().replace("ó", "o")


@router.get("/summary", response_model=VacationSummary)
def summary(year: int = Query(default_factory=lambda: date.today().year, ge=2000, le=2100), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    if principal.employee2_id is None:
        raise HTTPException(status_code=409, detail="user_has_no_employee2")
    employee = session.get(EmployeeReadModel, principal.employee2_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="employee_not_found")
    start_date = getattr(employee, "fecha_ingreso", None)
    months = seniority_months_at_year_end(start_date, year)
    entitled = vacation_days_for_seniority(months)
    balance = session.scalar(select(VacationBalance).where(VacationBalance.employee2_id == employee.id, VacationBalance.period == year))
    if balance:
        months = balance.seniority_months
        entitled = balance.entitled_days
    requests = []
    if principal.employee_id:
        requests = [item for item in session.scalars(select(LeaveRequest).where(LeaveRequest.employee_id == principal.employee_id, LeaveRequest.date_from >= date(year, 1, 1), LeaveRequest.date_from <= date(year, 12, 31))).unique().all() if _is_vacation(item)]
    used = sum((Decimal(item.days or 0) for item in requests if item.status == "Aprobada"), Decimal("0"))
    reserved = sum((Decimal(item.days or 0) for item in requests if item.status == "Pendiente"), Decimal("0"))
    current = Decimal(balance.available_balance or 0) if balance else non_negative(Decimal(entitled or 0) - used)
    return VacationSummary(year=year, employee_name=employee.nombre_completo or f"{employee.apellido or ''} {employee.nombre or ''}".strip(), employee_number=employee.numero_legajo, start_date=start_date, seniority_months=months, entitled_days=entitled, used_days=used, reserved_days=reserved, current_balance=current, available_to_request=non_negative(current - reserved), source=balance.source if balance else "CALCULO")


@router.get("/calendar", response_model=VacationCalendar)
def calendar(year: int = Query(default_factory=lambda: date.today().year, ge=2000, le=2100), month: int = Query(default_factory=lambda: date.today().month, ge=1, le=12), q: str = "", principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    management = principal.role in MANAGEMENT_ROLES
    if not management and principal.employee2_id is None:
        raise HTTPException(status_code=409, detail="user_has_no_employee2")
    first = date(year, month, 1)
    last = date(year, month, monthrange(year, month)[1])
    statement = select(VacationMovement).where(VacationMovement.date_from.is_not(None), VacationMovement.date_to.is_not(None), VacationMovement.date_from <= last, VacationMovement.date_to >= first)
    if not management:
        statement = statement.where(VacationMovement.employee2_id == principal.employee2_id)
    elif q.strip():
        pattern = f"%{q.strip()}%"
        statement = statement.join(VacationMovement.employee).where(or_(EmployeeReadModel.nombre_completo.ilike(pattern), EmployeeReadModel.nombre.ilike(pattern), EmployeeReadModel.apellido.ilike(pattern), EmployeeReadModel.numero_legajo.ilike(pattern)))
    events: list[VacationEvent] = []
    for movement in session.scalars(statement.order_by(VacationMovement.date_from)).unique().all():
        assert movement.date_from is not None and movement.date_to is not None
        visual_to = movement.date_to
        span = (movement.date_to - movement.date_from).days + 1
        informed = int(movement.days or 0)
        if span > 60 and 0 < informed <= 60:
            visual_to = movement.date_from + timedelta(days=informed - 1)
        if movement.date_from > last or visual_to < first:
            continue
        employee = movement.employee
        events.append(VacationEvent(key=f"movement-{movement.id}", employee2_id=movement.employee2_id, employee_name=employee.nombre_completo or f"{employee.apellido or ''} {employee.nombre or ''}".strip(), employee_number=employee.numero_legajo, date_from=movement.date_from, date_to=visual_to, original_date_to=movement.date_to, inconsistent_date=visual_to != movement.date_to, days=movement.days, status="Histórica", kind="historical", detail=movement.observations or movement.detail))
    people = {event.employee2_id for event in events}
    return VacationCalendar(year=year, month=month, management_view=management, people_count=len(people), events=events)
