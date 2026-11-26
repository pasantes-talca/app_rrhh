"""Configuración objetivo aislada; aún no se aplica a create_app."""
import re
import time
from collections import defaultdict, deque

from flask_wtf.csrf import CSRFProtect


csrf_protection = CSRFProtect()


SENSITIVE_KEYS = re.compile(
    r"(password|passwd|secret|token|authorization|cookie|cbu|cuenta_bancaria)",
    re.IGNORECASE,
)


def secure_settings(environment: str, secret_key: str | None):
    production = environment.lower() in {"production", "prod"}
    if production and (not secret_key or secret_key == "default_secret_key" or len(secret_key) < 32):
        raise RuntimeError("production_secret_required")
    return {
        "DEBUG": False if production else None,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SECURE": production,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "PERMANENT_SESSION_LIFETIME": 480 * 60,
        "WTF_CSRF_ENABLED": True,
    }


def redact_mapping(values):
    return {
        key: "[REDACTED]" if SENSITIVE_KEYS.search(str(key)) else value
        for key, value in values.items()
    }


def apply_flask_security(app):
    """Aplica el prototipo a una app aislada; no se invoca desde app.py."""
    csrf_protection.init_app(app)
    app.config.update({
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
    })
    return app


class FixedWindowRateLimiter:
    """Prototipo en memoria para pruebas; producción requerirá backend compartido."""
    def __init__(self, limit: int, window_seconds: int, clock=time.monotonic):
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock
        self.events = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = self.clock()
        queue = self.events[key]
        while queue and now - queue[0] >= self.window_seconds:
            queue.popleft()
        if len(queue) >= self.limit:
            return False
        queue.append(now)
        return True

