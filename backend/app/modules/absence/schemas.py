from datetime import date

from pydantic import BaseModel, ConfigDict


class AbsenceTypeView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: int
    category: str
    description: str
    productivity_impact: str | None


class AbsenceView(BaseModel):
    id: int
    employee_number: str
    employee_name: str
    area: str | None
    plant: str | None
    type_code: int
    category: str
    description: str
    date_from: date
    date_to: date
    calendar_days: int


class AbsencePage(BaseModel):
    items: list[AbsenceView]
    total_records: int
    total_people: int
    total_days: int
    page: int
    page_size: int


class ChartSeries(BaseModel):
    labels: list[str]
    values: list[float]


class AbsenceIndicators(BaseModel):
    date_from: date
    date_to: date
    active_employees: int
    absent_employees: int
    absent_workdays: int
    rate: float
    unjustified_days: int
    average_per_absent_employee: float
    variation: float | None
    categories: ChartSeries
    people: ChartSeries
    areas: ChartSeries
    weekdays: ChartSeries
    detail: list[AbsenceView]


class TrendIndicators(BaseModel):
    labels: list[str]
    days: list[int]
    rates: list[float]
    heatmap: list[list[float]]
    weekdays: list[str]
