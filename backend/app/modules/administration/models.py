from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base


class AuditEvent(Base):
    __tablename__ = "auditoria"; __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int | None] = mapped_column("usuario_id", Integer)
    username: Mapped[str | None] = mapped_column("usuario_nombre", String(100))
    module: Mapped[str] = mapped_column("modulo", String(60))
    action: Mapped[str] = mapped_column("accion", String(40))
    endpoint: Mapped[str | None] = mapped_column(String(150))
    method: Mapped[str | None] = mapped_column("metodo", String(10))
    detail: Mapped[str | None] = mapped_column("detalle", Text)
    ip: Mapped[str | None] = mapped_column(String(64))
    http_status: Mapped[int | None] = mapped_column("estado_http", Integer)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)


class SystemError(Base):
    __tablename__ = "errores_sistema"; __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[int | None] = mapped_column("codigo", Integer)
    endpoint: Mapped[str | None] = mapped_column(String(150))
    method: Mapped[str | None] = mapped_column("metodo", String(10))
    message: Mapped[str] = mapped_column("mensaje", Text)
    user_id: Mapped[int | None] = mapped_column("usuario_id", Integer)
    ip: Mapped[str | None] = mapped_column(String(64))
    reviewed: Mapped[bool] = mapped_column("revisado", Boolean)
    reviewed_by: Mapped[int | None] = mapped_column("revisado_por", Integer)
    reviewed_at: Mapped[datetime | None] = mapped_column("revisado_en", DateTime)
    review_reason: Mapped[str | None] = mapped_column("motivo_revision", Text)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)


class SystemConfiguration(Base):
    __tablename__ = "configuracion_sistema"; __table_args__ = {"schema": "rrhh"}
    key: Mapped[str] = mapped_column("clave", String(80), primary_key=True)
    value: Mapped[str] = mapped_column("valor", String(250))
    description: Mapped[str | None] = mapped_column("descripcion", String(250))
    updated_by: Mapped[int | None] = mapped_column("actualizado_por", Integer)
    updated_at: Mapped[datetime] = mapped_column("actualizado_en", DateTime)
