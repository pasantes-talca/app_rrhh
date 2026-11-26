from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    message: str
    kind: str
    read: bool
    created_at: datetime


class ChecklistCreate(BaseModel):
    description: str = Field(min_length=1, max_length=250)


class ChecklistView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    description: str
    completed: bool
    created_at: datetime
    completed_at: datetime | None
