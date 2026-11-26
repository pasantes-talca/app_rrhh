"""Configuración Pytest: fail-fast antes de recolectar pruebas peligrosas."""
import os


def pytest_sessionstart(session):
    os.environ.setdefault("APP_ENV", "testing")
    os.environ.setdefault("TESTING", "true")
    os.environ["TRILAY_SYNC_ENABLED"] = "false"

