from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SanctionEmployee(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    display_name: str
    employee_number: str | None


class SanctionView(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    employee_number: str | None
    kind: str
    date: date
    date_from: date | None
    date_to: date | None
    days: Decimal | None
    remaining_days: int | None
    reason: str
    description: str | None
    observations: str | None
    state: str
    has_file: bool
    original_filename: str | None
    notified_at: datetime | None


class SanctionSummary(BaseModel):
    total: int
    drafts: int
    notified: int
    suspensions: int
    items: list[SanctionView]
