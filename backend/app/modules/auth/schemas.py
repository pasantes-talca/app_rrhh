from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=256)


class UserView(BaseModel):
    id: int
    username: str
    display_name: str | None
    role: str
    employee_id: int | None
    employee2_id: int | None
    must_change_password: bool
    permissions: list[str]


class LoginResponse(BaseModel):
    user: UserView
    csrf_token: str


class CsrfResponse(BaseModel):
    csrf_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=1, max_length=256)
