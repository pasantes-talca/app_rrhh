from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class OvertimeCreate(BaseModel):
    date: date
    hours: Decimal = Field(ge=Decimal("0.25"), le=Decimal("16"))
    reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def not_in_future(self):
        if self.date > date.today():
            raise ValueError("date cannot be in the future")
        return self


class OvertimeDecision(BaseModel):
    observation: str | None = Field(default=None, max_length=2000)


class OvertimeDelete(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=500)


class OvertimeClear(BaseModel):
    confirmation: str = Field(pattern="^ELIMINAR$")


class OvertimeView(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    employee_number: str | None
    date: date
    time_from: time | None
    time_to: time | None
    hours: Decimal | None
    reason: str | None
    state: str
    observations: str | None
    manually_loaded_by_employee: bool
    created_at: datetime


class OvertimeSummary(BaseModel):
    items: list[OvertimeView]
    pending_manual: int


class ImportResult(BaseModel):
    created: int
    skipped: int
    errors: list[str]
