import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.database.session import Base
from app.database import models  # noqa: F401


config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def migration_url():
    if os.environ.get("ALLOW_ALEMBIC") != "true":
        raise RuntimeError("Alembic bloqueado: requiere ALLOW_ALEMBIC=true")
    url = get_settings().database_url.get_secret_value()
    if get_settings().environment == "testing" and "test" not in url.lower():
        raise RuntimeError("Destino de testing inseguro")
    return url


def run_migrations_offline():
    context.configure(url=migration_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = migration_url()
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_offline() if context.is_offline_mode() else run_migrations_online()

