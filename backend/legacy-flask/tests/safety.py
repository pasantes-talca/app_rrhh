"""Barreras para impedir que la suite apunte a servicios corporativos."""
from urllib.parse import urlparse


FORBIDDEN_HOST_MARKERS = ("10.", "192.168.", "talca.com.ar")


def assert_safe_test_settings(config):
    if not config.get("TESTING"):
        raise RuntimeError("La suite requiere TESTING=true")
    if config.get("TRILAY_SYNC_ENABLED"):
        raise RuntimeError("Trilay debe estar deshabilitado durante las pruebas")
    uri = str(config.get("SQLALCHEMY_DATABASE_URI") or "")
    if not uri:
        raise RuntimeError("Falta una base aislada de pruebas")
    parsed = urlparse(uri)
    hostname = (parsed.hostname or "").lower()
    if any(marker in hostname for marker in FORBIDDEN_HOST_MARKERS):
        raise RuntimeError("La suite rechazó una dirección corporativa")
    if parsed.scheme.startswith("postgres") and "test" not in (parsed.path or "").lower():
        raise RuntimeError("Una base PostgreSQL de pruebas debe incluir 'test' en su nombre")

