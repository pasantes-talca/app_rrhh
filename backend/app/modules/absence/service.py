import calendar
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Absence, AbsenceEmployee

MONTHS_SHORT = ("Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic")
WEEKDAYS = ("Lun", "Mar", "Mié", "Jue", "Vie")


def business_days(date_from: date, date_to: date) -> int:
    if date_to < date_from:
        return 0
    total = (date_to - date_from).days + 1
    weeks, remainder = divmod(total, 7)
    return weeks * 5 + sum(1 for offset in range(remainder) if (date_from.weekday() + offset) % 7 < 5)


def period(year: int, month: int) -> tuple[date, date]:
    first_month, last_month = (month, month) if month else (1, 12)
    return date(year, first_month, 1), date(year, last_month, calendar.monthrange(year, last_month)[1])


def _active_employees(session: Session, date_from: date, date_to: date, plant: str):
    statement = select(AbsenceEmployee)
    if plant:
        statement = statement.where(AbsenceEmployee.plant == plant)
    return [employee for employee in session.scalars(statement).all() if (not employee.start_date or employee.start_date <= date_to) and (not employee.end_date or employee.end_date >= date_from)]


def _events(session: Session, date_from: date, date_to: date, plant: str):
    statement = select(Absence).where(Absence.date_from <= date_to, Absence.date_to >= date_from)
    if plant:
        statement = statement.where(Absence.source_plant == plant)
    return session.scalars(statement.order_by(Absence.date_from)).unique().all()


def absence_summary(session: Session, year: int, month: int = 0, plant: str = "") -> dict:
    date_from, date_to = period(year, month)
    employees = _active_employees(session, date_from, date_to, plant)
    capacity_by_area: defaultdict[str, int] = defaultdict(int)
    total_capacity = 0
    for employee in employees:
        start = max(date_from, employee.start_date) if employee.start_date else date_from
        end = min(date_to, employee.end_date) if employee.end_date else date_to
        capacity = business_days(start, end)
        total_capacity += capacity
        capacity_by_area[employee.area or "Sin área"] += capacity
    rows = [(event, business_days(max(event.date_from, date_from), min(event.date_to, date_to))) for event in _events(session, date_from, date_to, plant)]
    rows = [(event, days) for event, days in rows if days > 0]
    categories: defaultdict[str, int] = defaultdict(int)
    people_days: defaultdict[str, int] = defaultdict(int)
    names: dict[str, str] = {}
    area_days: defaultdict[str, int] = defaultdict(int)
    weekday_days: defaultdict[str, int] = defaultdict(int)
    unjustified = 0
    detail = []
    for event, days in rows:
        category = event.absence_type.category if event.absence_type else "SIN CATEGORÍA"
        categories[category] += days
        people_days[event.source_employee_number] += days
        names[event.source_employee_number] = event.source_name or f"Legajo {event.source_employee_number}"
        area = event.source_area or "Sin área"
        area_days[area] += days
        unjustified += days if category.upper() == "INJUSTIFICADA" else 0
        current, end = max(event.date_from, date_from), min(event.date_to, date_to)
        while current <= end:
            if current.weekday() < 5:
                weekday_days[WEEKDAYS[current.weekday()]] += 1
            current += timedelta(days=1)
        detail.append({"id": event.id, "employee_number": event.source_employee_number, "employee_name": names[event.source_employee_number], "area": event.source_area, "plant": event.source_plant, "type_code": event.type_code, "category": category, "description": event.absence_type.description if event.absence_type else event.source_description or "-", "date_from": event.date_from, "date_to": event.date_to, "calendar_days": event.calendar_days})
    total_days = sum(days for _, days in rows)
    people = set(people_days)
    rate = total_days / total_capacity * 100 if total_capacity else 0
    previous_to = date_from - timedelta(days=1)
    previous_from = previous_to - timedelta(days=(date_to - date_from).days)
    previous_days = sum(business_days(max(event.date_from, previous_from), min(event.date_to, previous_to)) for event in _events(session, previous_from, previous_to, plant))
    variation = (total_days - previous_days) / previous_days * 100 if previous_days else None
    area_rates = {area: days / capacity_by_area.get(area, 0) * 100 if capacity_by_area.get(area) else 0 for area, days in area_days.items()}
    top_people = sorted(people_days, key=people_days.get, reverse=True)[:10]
    top_areas = sorted(area_rates, key=area_rates.get, reverse=True)[:10]
    return {"date_from": date_from, "date_to": date_to, "active_employees": len(employees), "absent_employees": len(people), "absent_workdays": total_days, "rate": rate, "unjustified_days": unjustified, "average_per_absent_employee": total_days / len(people) if people else 0, "variation": variation, "categories": {"labels": list(categories), "values": list(categories.values())}, "people": {"labels": [names[key] for key in top_people], "values": [people_days[key] for key in top_people]}, "areas": {"labels": top_areas, "values": [round(area_rates[key], 2) for key in top_areas]}, "weekdays": {"labels": list(WEEKDAYS), "values": [weekday_days[day] for day in WEEKDAYS]}, "detail": sorted(detail, key=lambda item: (item["calendar_days"], item["date_from"]), reverse=True)}


def trend_summary(session: Session, year: int, plant: str = "") -> dict:
    summaries = [absence_summary(session, year, month, plant) for month in range(1, 13)]
    return {"labels": list(MONTHS_SHORT), "days": [item["absent_workdays"] for item in summaries], "rates": [round(item["rate"], 2) for item in summaries], "heatmap": [item["weekdays"]["values"] for item in summaries], "weekdays": list(WEEKDAYS)}
