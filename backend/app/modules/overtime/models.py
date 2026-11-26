from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.modules.auth.models import User
from app.modules.licenses.models import LegacyEmployee


class Overtime(Base):
    __tablename__ = "horas_extra"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column("empleado_id", ForeignKey("rrhh.empleados.id"))
    date: Mapped[date] = mapped_column("fecha", Date)
    time_from: Mapped[time | None] = mapped_column("hora_desde", Time)
    time_to: Mapped[time | None] = mapped_column("hora_hasta", Time)
    hours: Mapped[Decimal | None] = mapped_column("cantidad_horas", Numeric(10, 2))
    reason: Mapped[str | None] = mapped_column("motivo", Text)
    sector_id: Mapped[int | None] = mapped_column("sector_id", Integer)
    supervisor_id: Mapped[int | None] = mapped_column("supervisor_id", Integer)
    state: Mapped[str] = mapped_column("estado", String(50))
    observations: Mapped[str | None] = mapped_column("observaciones", Text)
    loaded_by: Mapped[int | None] = mapped_column("cargado_por", ForeignKey("rrhh.usuarios.id"))
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)
    employee: Mapped[LegacyEmployee] = relationship(lazy="joined")
    loader: Mapped[User | None] = relationship(lazy="joined")


class Company(Base):
    __tablename__ = "empresas"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column("nombre", String(100))
    weekday_rate: Mapped[Decimal | None] = mapped_column("tarifa_lav", Numeric(10, 2))
    saturday_rate: Mapped[Decimal | None] = mapped_column("tarifa_sab", Numeric(10, 2))
    sunday_holiday_rate: Mapped[Decimal | None] = mapped_column("tarifa_dom_fer", Numeric(10, 2))


class Sector(Base):
    __tablename__ = "sectores"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column("nombre", String(100))
