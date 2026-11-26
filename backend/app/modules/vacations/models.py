from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.modules.employees.models import EmployeeReadModel


class VacationBalance(Base):
    __tablename__ = "vacaciones_saldos"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee2_id: Mapped[int] = mapped_column("empleado2_id", ForeignKey("rrhh.empleados2.id"))
    period: Mapped[int] = mapped_column("periodo", Integer)
    calculation_start_date: Mapped[date | None] = mapped_column("fecha_ingreso_calculo", Date)
    seniority_months: Mapped[int | None] = mapped_column("antiguedad_meses", Integer)
    entitled_days: Mapped[Decimal] = mapped_column("dias_correspondientes", Numeric(8, 2))
    base_balance: Mapped[Decimal] = mapped_column("saldo_base", Numeric(8, 2))
    adjustments: Mapped[Decimal] = mapped_column("ajustes", Numeric(8, 2))
    available_balance: Mapped[Decimal] = mapped_column("saldo_disponible", Numeric(8, 2))
    source: Mapped[str] = mapped_column("origen", String(30))
    cutoff_date: Mapped[date | None] = mapped_column("fecha_corte", Date)
    observations: Mapped[str | None] = mapped_column("observaciones", Text)


class VacationMovement(Base):
    __tablename__ = "vacaciones_movimientos"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee2_id: Mapped[int] = mapped_column("empleado2_id", ForeignKey("rrhh.empleados2.id"))
    balance_id: Mapped[int | None] = mapped_column("saldo_id", BigInteger)
    license_id: Mapped[int | None] = mapped_column("licencia_id", Integer)
    kind: Mapped[str] = mapped_column("tipo", String(40))
    date_from: Mapped[date | None] = mapped_column("fecha_desde", Date)
    date_to: Mapped[date | None] = mapped_column("fecha_hasta", Date)
    return_date: Mapped[date | None] = mapped_column("fecha_reintegro", Date)
    days: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    resulting_balance: Mapped[Decimal | None] = mapped_column("saldo_resultante", Numeric(8, 2))
    detail: Mapped[str | None] = mapped_column("detalle", Text)
    observations: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column("origen", String(30))
    source_reference: Mapped[str] = mapped_column("referencia_origen", String(100))
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)
    employee: Mapped[EmployeeReadModel] = relationship(lazy="joined")
