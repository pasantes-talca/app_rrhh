from datetime import datetime
from pydantic import BaseModel, Field

class AdminSummary(BaseModel):
    users: int; active_users: int; operations_30_days: int; unreviewed_errors: int; open_sessions: int

class AdminUserView(BaseModel):
    id: int; username: str; display_name: str | None; email: str | None; employee_id: int | None; role_id: int; role: str; active: bool; protected: bool; editable: bool; last_access: datetime | None

class AdminUserInput(BaseModel):
    username: str = Field(min_length=3, max_length=100); display_name: str = Field(min_length=1, max_length=150); email: str | None = Field(default=None, max_length=150); employee_id: int | None = None; role_id: int; active: bool = True; password: str | None = Field(default=None, max_length=256)

class PasswordReset(BaseModel): password: str = Field(min_length=1, max_length=256)
class PermissionInput(BaseModel): permissions: list[str]
class RoleView(BaseModel): id: int; name: str
class AuditView(BaseModel):
    id: int; username: str | None; module: str; action: str; endpoint: str | None; method: str | None; detail: str | None; ip: str | None; http_status: int | None; created_at: datetime
class ActivityReportRow(BaseModel):
    username: str | None; module: str; action: str; total: int
class ErrorView(BaseModel):
    id: int; code: int | None; endpoint: str | None; method: str | None; message: str; ip: str | None; reviewed: bool; review_reason: str | None; created_at: datetime
class ErrorReview(BaseModel): reason: str = Field(min_length=5, max_length=1000)
class SecuritySettings(BaseModel): password_min_length: int = Field(ge=8, le=64); session_max_minutes: int = Field(ge=15, le=10080)
class SessionView(BaseModel): id: str; username: str; ip: str | None; started_at: datetime; last_activity: datetime
class SystemStatus(BaseModel): database_version: str; database_latency_ms: float; database_name: str; schema_name: str; python_version: str; environment: str; controls: dict[str, bool]
