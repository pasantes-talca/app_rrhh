from datetime import date
from pydantic import BaseModel

class BirthdayView(BaseModel):
    employee_name: str; date: date; days: int; age: int
class CalendarEvent(BaseModel):
    date: date; title: str; kind: str
class DashboardCounts(BaseModel):
    active_employees: int | None = None; pending_licenses: int; pending_overtime: int; received_documents: int; pending_receipts: int
class DashboardOverview(BaseModel):
    name: str; management: bool; birthday_today: bool; counts: DashboardCounts; birthdays: list[BirthdayView]; upcoming_events: list[CalendarEvent]; calendar_events: list[CalendarEvent]; year: int; month: int
