from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.modules.licenses.models import LegacyEmployee


class Sanction(Base):
    __tablename__ = "sanciones_disciplinarias"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column("empleado_id", ForeignKey("rrhh.empleados.id"))
    kind: Mapped[str] = mapped_column("tipo", String(50))
    date: Mapped[date] = mapped_column(Date)
    date_from: Mapped[date | None] = mapped_column("fecha_desde", Date)
    date_to: Mapped[date | None] = mapped_column("fecha_hasta", Date)
    days: Mapped[Decimal | None] = mapped_column("cantidad_dias", Numeric(6, 2))
    reason: Mapped[str] = mapped_column("motivo", String(200))
    description: Mapped[str | None] = mapped_column("descripcion", Text)
    observations: Mapped[str | None] = mapped_column(Text)
    original_filename: Mapped[str | None] = mapped_column("nombre_archivo", String(255))
    file_path: Mapped[str | None] = mapped_column("ruta_archivo", Text)
    state: Mapped[str] = mapped_column("estado", String(50))
    notified_at: Mapped[datetime | None] = mapped_column("notificado_en", DateTime)
    created_by: Mapped[int] = mapped_column("creado_por", Integer)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)
    updated_at: Mapped[datetime | None] = mapped_column("actualizado_en", DateTime)
    employee: Mapped[LegacyEmployee] = relationship(lazy="joined")
