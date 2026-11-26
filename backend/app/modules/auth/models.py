from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column("nombre", String(50))
    description: Mapped[str | None] = mapped_column("descripcion", Text)
    active: Mapped[bool] = mapped_column("activo", Boolean)


class User(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int | None] = mapped_column("empleado_id", Integer)
    employee2_id: Mapped[int | None] = mapped_column("empleado2_id", BigInteger)
    role_id: Mapped[int] = mapped_column("rol_id", ForeignKey("rrhh.roles.id"))
    username: Mapped[str] = mapped_column("usuario", String(100))
    display_name: Mapped[str | None] = mapped_column("nombre_mostrar", String(150))
    email: Mapped[str | None] = mapped_column("correo", String(150))
    profile_photo: Mapped[str | None] = mapped_column("foto_perfil", String(255))
    protected_account: Mapped[bool] = mapped_column("cuenta_protegida", Boolean)
    password_hash: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column("activo", Boolean)
    must_change_password: Mapped[bool] = mapped_column("debe_cambiar_password", Boolean)
    last_access: Mapped[datetime | None] = mapped_column("ultimo_acceso", DateTime)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)
    role: Mapped[Role] = relationship(lazy="joined")


class UserPermission(Base):
    __tablename__ = "permisos_usuario"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("rrhh.usuarios.id"))
    module: Mapped[str] = mapped_column("modulo", String(50))
    action: Mapped[str] = mapped_column("accion", String(30))
    allowed: Mapped[bool] = mapped_column("permitido", Boolean)
    assigned_by: Mapped[int | None] = mapped_column("asignado_por", Integer)
    updated_at: Mapped[datetime] = mapped_column("actualizado_en", DateTime)


class UserSession(Base):
    __tablename__ = "sesiones_usuario"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("rrhh.usuarios.id"))
    ip: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column("agente", Text)
    started_at: Mapped[datetime] = mapped_column("iniciada_en", DateTime)
    last_activity: Mapped[datetime] = mapped_column("ultima_actividad", DateTime)
    closed_at: Mapped[datetime | None] = mapped_column("cerrada_en", DateTime)
    closed_by: Mapped[int | None] = mapped_column("cerrada_por", Integer)
    closed_reason: Mapped[str | None] = mapped_column("motivo_cierre", String(200))
