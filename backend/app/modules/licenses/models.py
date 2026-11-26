from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class LegacyEmployee(Base):
    __tablename__ = "empleados"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column("nombre_apellido", String(150))
    company_id: Mapped[int | None] = mapped_column("empresa_id", Integer)
    sector_id: Mapped[int | None] = mapped_column("sector_id", Integer)
    employee_number: Mapped[str | None] = mapped_column("legajo", String(50))
    document_number: Mapped[str] = mapped_column("dni", String(20))
    state: Mapped[str | None] = mapped_column("estado", String(50))
    cuil: Mapped[str | None] = mapped_column(String(30))
    workday_hours: Mapped[Decimal | None] = mapped_column("jornada_horas", Numeric(4, 2))
    birth_date: Mapped[date | None] = mapped_column("fecha_nacimiento", Date)
    gender: Mapped[str | None] = mapped_column("genero", String(50))
    phone: Mapped[str | None] = mapped_column("telefono", String(50))
    email: Mapped[str | None] = mapped_column("correo", String(150))
    address: Mapped[str | None] = mapped_column("domicilio", String(200))
    province: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column("codigo_postal", String(20))
    driver_license: Mapped[str | None] = mapped_column("licencia_conducir", String(100))
    position_id: Mapped[int | None] = mapped_column("puesto_id", Integer)
    supervisor_id: Mapped[int | None] = mapped_column(Integer)
    schedule_id: Mapped[int | None] = mapped_column("jornada_id", Integer)
    start_date: Mapped[date | None] = mapped_column("fecha_ingreso", Date)


class LeaveType(Base):
    __tablename__ = "tipos_licencia"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column("nombre", String(100))
    description: Mapped[str | None] = mapped_column("descripcion", Text)
    attachment_required: Mapped[bool] = mapped_column("requiere_adjunto", Boolean)
    active: Mapped[bool] = mapped_column("activo", Boolean)


class EmployeeSupervisor(Base):
    __tablename__ = "empleados_supervisores"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee2_id: Mapped[int] = mapped_column("empleado2_id", BigInteger)
    supervisor_employee2_id: Mapped[int] = mapped_column("supervisor_empleado2_id", BigInteger)
    active: Mapped[bool] = mapped_column("activo", Boolean)


class LeaveRequest(Base):
    __tablename__ = "licencias"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column("empleado_id", ForeignKey("rrhh.empleados.id"))
    type_id: Mapped[int] = mapped_column("tipo_licencia_id", ForeignKey("rrhh.tipos_licencia.id"))
    date_from: Mapped[date] = mapped_column("fecha_desde", Date)
    date_to: Mapped[date] = mapped_column("fecha_hasta", Date)
    days: Mapped[Decimal | None] = mapped_column("cantidad_dias", Numeric(10, 2))
    reason: Mapped[str | None] = mapped_column("motivo", Text)
    attachment: Mapped[str | None] = mapped_column("archivo_adjunto", Text)
    status: Mapped[str] = mapped_column("estado", String(50))
    resolved_by: Mapped[int | None] = mapped_column("aprobado_por", Integer)
    resolved_at: Mapped[datetime | None] = mapped_column("fecha_resolucion", DateTime)
    hr_observation: Mapped[str | None] = mapped_column("observacion_rrhh", Text)
    supervisor_status: Mapped[str] = mapped_column("estado_supervisor", String(30))
    supervisor_resolved_by: Mapped[int | None] = mapped_column("supervisor_resuelto_por", Integer)
    supervisor_resolved_at: Mapped[datetime | None] = mapped_column("fecha_resolucion_supervisor", DateTime)
    supervisor_observation: Mapped[str | None] = mapped_column("observacion_supervisor", Text)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)
    employee: Mapped[LegacyEmployee] = relationship(lazy="joined")
    leave_type: Mapped[LeaveType] = relationship(lazy="joined")
