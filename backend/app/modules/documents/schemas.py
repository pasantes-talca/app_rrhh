from datetime import date, datetime
from pydantic import BaseModel, Field


class DocumentTypeView(BaseModel):
    id: int
    name: str


class DocumentView(BaseModel):
    id: int
    employee_id: int | None
    employee_name: str | None
    employee_number: str | None
    type_id: int
    type_name: str
    name: str
    original_filename: str | None
    visible_to_employee: bool
    observations: str | None
    state: str
    source: str
    created_at: datetime


class EmployeeFolder(BaseModel):
    employee_id: int
    employee_name: str
    employee_number: str | None
    employee_sent: int
    shared_by_hr: int
    total: int
    last_document_at: datetime


class ReceiptView(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    employee_number: str | None
    period: str
    deadline: date | None
    state: str
    viewed_at: datetime | None
    responded_at: datetime | None
    response: str | None
    employee_observation: str | None
    original_filename: str | None
    file_hash: str
    created_at: datetime


class ReceiptResponse(BaseModel):
    response: str
    observation: str | None = Field(default=None, max_length=2000)


class ReceiptSummary(BaseModel):
    total: int
    pending: int
    compliant: int
    non_compliant: int
    items: list[ReceiptView]

