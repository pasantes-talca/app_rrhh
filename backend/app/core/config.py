from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TALCA_API_", env_file=None, extra="ignore",
    )

    environment: Literal["development", "testing", "staging", "production"] = "development"
    database_url: SecretStr = Field(default=SecretStr("postgresql+psycopg://invalid:invalid@127.0.0.1/invalid"))
    session_secret: SecretStr = Field(default=SecretStr(""))
    allowed_origins: tuple[str, ...] = ("http://localhost:5173",)
    trilay_enabled: bool = False
    session_cookie_name: str = "talca_session"
    session_max_minutes: int = 480
    login_max_attempts: int = 8
    login_window_seconds: int = 300
    cookie_secure: bool = False
    upload_root: Path = Path("uploads")
    max_upload_bytes: int = 10 * 1024 * 1024
    overtime_template: Path = Path("app/assets/formato_horas_extra.xlsx")

    @model_validator(mode="after")
    def validate_sensitive_settings(self):
        url = self.database_url.get_secret_value()
        if self.environment in {"testing", "production"} and not self.session_secret.get_secret_value():
            raise ValueError("session_secret is required")
        if self.environment == "testing":
            if "test" not in url.lower() or any(marker in url for marker in ("10.242.", "192.168.")):
                raise ValueError("testing database must be isolated")
            if self.trilay_enabled:
                raise ValueError("Trilay must remain disabled in testing")
        if self.environment == "production" and len(self.session_secret.get_secret_value()) < 32:
            raise ValueError("production session secret must contain at least 32 characters")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

