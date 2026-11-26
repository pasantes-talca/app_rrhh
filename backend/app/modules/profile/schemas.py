from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class CatalogItem(BaseModel):
    id: int
    name: str


class ProfileCatalogs(BaseModel):
    companies: list[CatalogItem]
    sectors: list[CatalogItem]
    positions: list[CatalogItem]
    schedules: list[CatalogItem]
    supervisors: list[CatalogItem]


class ProfileView(BaseModel):
    username: str
    display_name: str
    email: str | None
    has_photo: bool
    employee_id: int | None
    source_employee2: bool
    phone: str | None
    birth_date: date | None
    gender: str | None
    address: str | None
    province: str | None
    postal_code: str | None
    driver_license: str | None
    document_number: str | None
    cuil: str | None
    employee_number: str | None
    company_id: int | None
    sector_id: int | None
    position_id: int | None
    supervisor_id: int | None
    schedule_id: int | None
    workday_hours: Decimal | None
    start_date: date | None
    employee_state: str | None


class ProfileUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=150)
    email: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=50)
    birth_date: date | None = None
    gender: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=200)
    province: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    driver_license: str | None = Field(default=None, max_length=100)
    document_number: str | None = Field(default=None, max_length=20)
    cuil: str | None = Field(default=None, max_length=30)
    employee_number: str | None = Field(default=None, max_length=50)
    company_id: int | None = None
    sector_id: int | None = None
    position_id: int | None = None
    supervisor_id: int | None = None
    schedule_id: int | None = None
    workday_hours: Decimal | None = Field(default=None, ge=0, le=24)
    start_date: date | None = None
    employee_state: str | None = None
