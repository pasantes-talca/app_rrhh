from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.database.session import build_session_factory
from app.modules.administration.models import AuditEvent, SystemError
from app.modules.auth.models import User


def _classification(request: Request) -> tuple[str, str]:
    parts = [part for part in request.url.path.split("/") if part]
    module = parts[2] if len(parts) > 2 and parts[:2] == ["api", "v1"] else "system"
    method = request.method.upper()
    if method == "GET":
        action = "exportar" if request.url.path.endswith(".csv") or request.url.path.endswith("/file") else "consultar"
    elif method == "POST":
        action = "crear"
    elif method in {"PUT", "PATCH"}:
        action = "editar"
    else:
        action = "anular"
    return module[:60], action


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.session_factory = build_session_factory()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/api/v1/health", "/api/v1/auth/csrf"} or request.url.path.startswith("/api/docs"):
            return await call_next(request)
        try:
            response = await call_next(request)
        except Exception as error:
            self._record_error(request, error)
            raise
        self._record_audit(request, response.status_code)
        return response

    def _record_audit(self, request: Request, status_code: int) -> None:
        principal = getattr(request.state, "principal", None)
        if principal is None:
            return
        module, action = _classification(request)
        route = request.scope.get("route")
        endpoint = getattr(route, "path", request.url.path)
        try:
            with self.session_factory() as session:
                user = session.get(User, principal.user_id)
                session.add(AuditEvent(user_id=principal.user_id, username=user.username if user else None, module=module, action=action, endpoint=str(endpoint)[:150], method=request.method[:10], detail=None, ip=(request.headers.get("X-Forwarded-For") or (request.client.host if request.client else ""))[:64], http_status=status_code, created_at=datetime.utcnow()))
                session.commit()
        except Exception:
            # Audit persistence must never make the business request fail.
            return

    def _record_error(self, request: Request, error: Exception) -> None:
        principal = getattr(request.state, "principal", None)
        try:
            with self.session_factory() as session:
                session.add(SystemError(code=500, endpoint=request.url.path[:150], method=request.method[:10], message=type(error).__name__, user_id=principal.user_id if principal else None, ip=(request.headers.get("X-Forwarded-For") or (request.client.host if request.client else ""))[:64], reviewed=False, created_at=datetime.utcnow()))
                session.commit()
        except Exception:
            return
