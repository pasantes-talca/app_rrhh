from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal
from app.database.session import get_session
from app.modules.employees.models import EmployeeReadModel
from .models import Absence, AbsenceType
from .schemas import AbsenceIndicators, AbsencePage, AbsenceTypeView, AbsenceView, TrendIndicators
from .service import absence_summary, trend_summary

router = APIRouter(tags=["absence"])
ABSENCE_ROLES = {"recursos_humanos", "gerencia", "administrador"}
INDICATOR_ROLES = {"gerencia", "administrador"}


def _require_role(principal: Principal, roles: set[str]) -> None:
    if principal.role not in roles:
        raise HTTPException(status_code=403, detail="permission_denied")


def _view(item: Absence) -> AbsenceView:
    return AbsenceView(id=item.id, employee_number=item.source_employee_number, employee_name=item.source_name or f"Legajo {item.source_employee_number}", area=item.source_area, plant=item.source_plant, type_code=item.type_code, category=item.absence_type.category, description=item.absence_type.description, date_from=item.date_from, date_to=item.date_to, calendar_days=item.calendar_days)


@router.get("/absence/types", response_model=list[AbsenceTypeView])
def types(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _require_role(principal, ABSENCE_ROLES)
    return session.scalars(select(AbsenceType).order_by(AbsenceType.description)).all()


@router.get("/absence", response_model=AbsencePage)
def list_absence(date_from: date = Query(default_factory=lambda: date(date.today().year, 1, 1)), date_to: date = Query(default_factory=lambda: date(date.today().year, 12, 31)), q: str = "", type_code: int | None = None, plant: str = "", page: int = Query(1, ge=1), page_size: int = Query(30, ge=1, le=100), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _require_role(principal, ABSENCE_ROLES)
    if date_to < date_from:
        date_from, date_to = date_to, date_from
    statement = select(Absence).where(Absence.date_from <= date_to, Absence.date_to >= date_from)
    if q.strip():
        pattern = f"%{q.strip()}%"
        statement = statement.outerjoin(EmployeeReadModel, Absence.employee2_id == EmployeeReadModel.id).where(or_(EmployeeReadModel.nombre_completo.ilike(pattern), EmployeeReadModel.nombre.ilike(pattern), EmployeeReadModel.apellido.ilike(pattern), EmployeeReadModel.numero_legajo.ilike(pattern), Absence.source_name.ilike(pattern)))
    if type_code is not None:
        statement = statement.where(Absence.type_code == type_code)
    if plant:
        statement = statement.where(Absence.source_plant == plant)
    subquery = statement.subquery()
    total = session.scalar(select(func.count()).select_from(subquery)) or 0
    people = session.scalar(select(func.count(func.distinct(subquery.c.source_employee_number)))) or 0
    days = session.scalar(select(func.coalesce(func.sum(subquery.c.calendar_days), 0))) or 0
    items = session.scalars(statement.order_by(Absence.date_from.desc(), Absence.id.desc()).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return AbsencePage(items=[_view(item) for item in items], total_records=total, total_people=people, total_days=days, page=page, page_size=page_size)


@router.get("/indicators/absence", response_model=AbsenceIndicators)
def indicators(year: int = Query(default_factory=lambda: date.today().year, ge=2000, le=2100), month: int = Query(0, ge=0, le=12), plant: str = "", principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _require_role(principal, INDICATOR_ROLES)
    return absence_summary(session, year, month, plant)


@router.get("/indicators/absence/trend", response_model=TrendIndicators)
def trend(year: int = Query(default_factory=lambda: date.today().year, ge=2000, le=2100), plant: str = "", principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _require_role(principal, INDICATOR_ROLES)
    return trend_summary(session, year, plant)
