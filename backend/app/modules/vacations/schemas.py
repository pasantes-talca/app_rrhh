from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class VacationSummary(BaseModel):
    year: int
    employee_name: str
    employee_number: str | None
    start_date: date | None
    seniority_months: int | None
    entitled_days: Decimal | None
    used_days: Decimal
    reserved_days: Decimal
    current_balance: Decimal
    available_to_request: Decimal
    source: str


class VacationEvent(BaseModel):
    key: str
    employee2_id: int
    employee_name: str
    employee_number: str | None
    date_from: date
    date_to: date
    original_date_to: date | None = None
    inconsistent_date: bool = False
    days: Decimal | None
    status: str
    kind: str
    detail: str | None


class VacationCalendar(BaseModel):
    year: int
    month: int
    management_view: bool
    people_count: int
    events: list[VacationEvent]
