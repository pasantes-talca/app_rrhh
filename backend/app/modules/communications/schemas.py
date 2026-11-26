from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class NewsView(BaseModel):
    id: int
    title: str
    content: str
    has_image: bool
    visible_to_all: bool
    is_important_date: bool
    important_date: date | None
    company_id: int | None
    sector_id: int | None
    published_at: datetime | None


class ImportantDateCreate(BaseModel):
    date: date
    description: str


class ImportantDateView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date
    description: str | None
