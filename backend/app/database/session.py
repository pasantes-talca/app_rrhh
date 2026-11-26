from sqlalchemy import create_engine
from collections.abc import Generator

from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def build_session_factory():
    settings = get_settings()
    engine = create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        future=True,
    )
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


_session_factory = None


def get_session() -> Generator[Session, None, None]:
    global _session_factory
    if _session_factory is None:
        _session_factory = build_session_factory()
    with _session_factory() as session:
        yield session

