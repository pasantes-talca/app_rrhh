from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LeaveTypeView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    attachment_required: bool


class LeaveCreate(BaseModel):
    type_id: int
    date_from: date
    date_to: date
    days: Decimal = Field(gt=0, le=365)
    reason: str | None = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def dates_are_ordered(self):
        if self.date_to < self.date_from:
            raise ValueError("date_to must be on or after date_from")
        return self


class LeaveResolution(BaseModel):
    decision: str = Field(pattern="^(Aprobada|Rechazada)$")
    observation: str | None = Field(default=None, max_length=4000)


class LeaveView(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    type_id: int
    type_name: str
    date_from: date
    date_to: date
    days: Decimal | None
    reason: str | None
    status: str
    supervisor_status: str
    hr_observation: str | None
    supervisor_observation: str | None
    has_attachment: bool
    created_at: datetime
