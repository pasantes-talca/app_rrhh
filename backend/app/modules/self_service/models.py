from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Notification(Base):
    __tablename__ = "notificaciones"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("rrhh.usuarios.id"))
    title: Mapped[str] = mapped_column("titulo", String(200))
    message: Mapped[str] = mapped_column("mensaje", Text)
    kind: Mapped[str] = mapped_column("tipo", String(50))
    reference_type: Mapped[str | None] = mapped_column("referencia_tipo", String(50))
    reference_id: Mapped[int | None] = mapped_column("referencia_id", Integer)
    read: Mapped[bool] = mapped_column("leida", Boolean)
    read_at: Mapped[datetime | None] = mapped_column("leida_en", DateTime)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)


class ChecklistTask(Base):
    __tablename__ = "tareas_checklist"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("rrhh.usuarios.id"))
    description: Mapped[str] = mapped_column("descripcion", String(250))
    completed: Mapped[bool] = mapped_column("completada", Boolean)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)
    completed_at: Mapped[datetime | None] = mapped_column("completado_en", DateTime)
