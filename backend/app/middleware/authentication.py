from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import get_settings
from app.database.session import build_session_factory
from app.modules.auth.service import resolve_session


class SessionAuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.session_factory = build_session_factory()

    async def dispatch(self, request: Request, call_next):
        session_id = request.cookies.get(get_settings().session_cookie_name)
        if session_id:
            with self.session_factory() as session:
                request.state.principal = resolve_session(session, session_id)
        return await call_next(request)
