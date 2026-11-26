import calendar
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Principal
from app.modules.communications.models import ImportantDate
from app.modules.licenses.models import LegacyEmployee
from .models import Notification


def _birthday_today(born: date | None, today: date) -> bool:
    if born is None:
        return False
    if (born.month, born.day) == (today.month, today.day):
        return True
    return born.month == 2 and born.day == 29 and today.month == 2 and today.day == 28 and not calendar.isleap(today.year)


def _create_once(session: Session, principal: Principal, *, title: str, message: str, kind: str, reference_type: str, reference_id: int) -> bool:
    exists = session.scalar(select(Notification.id).where(Notification.user_id == principal.user_id, Notification.reference_type == reference_type, Notification.reference_id == reference_id))
    if exists:
        return False
    session.add(Notification(user_id=principal.user_id, title=title, message=message, kind=kind, reference_type=reference_type, reference_id=reference_id, read=False, created_at=datetime.utcnow()))
    return True


def ensure_daily_notifications(session: Session, principal: Principal, today: date | None = None) -> int:
    today = today or date.today()
    created = 0
    employee = session.get(LegacyEmployee, principal.employee_id) if principal.employee_id else None
    if employee and _birthday_today(employee.birth_date, today):
        created += _create_once(session, principal, title="¡Feliz cumpleaños!", message=f"¡Feliz cumpleaños, {employee.display_name}! Todo el equipo de Talca te desea un excelente día.", kind="cumpleanos", reference_type=f"cumpleanos_{today.year}", reference_id=employee.id)
    for item in session.scalars(select(ImportantDate).where(ImportantDate.date == today)).all():
        created += _create_once(session, principal, title="Fecha importante", message=item.description or "Hoy es una fecha importante.", kind="fecha_importante", reference_type=f"fecha_importante_{today.year}", reference_id=item.id)
    if created:
        session.commit()
    return created
