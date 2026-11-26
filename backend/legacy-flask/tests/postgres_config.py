"""Configuración explícita para PostgreSQL efímero de Docker."""
import os

from tests.safety import assert_safe_test_settings


class PostgreSQLTestConfig:
    TESTING = True
    SECRET_KEY = "synthetic-postgres-test-only"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg2://talca_test_runner:synthetic-local-only-change-me"
        "@127.0.0.1:55432/talca_rrhh_test",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    TRILAY_SYNC_ENABLED = False
    UPLOAD_FOLDER = ".test-artifacts/uploads"
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


def validate():
    config = {
        key: getattr(PostgreSQLTestConfig, key)
        for key in (
            "TESTING", "SQLALCHEMY_DATABASE_URI", "TRILAY_SYNC_ENABLED"
        )
    }
    assert_safe_test_settings(config)
    if "@127.0.0.1:55432/" not in config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("PostgreSQL de pruebas debe usar 127.0.0.1:55432")
    return config

