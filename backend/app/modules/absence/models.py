from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class AbsenceType(Base):
    __tablename__ = "tipos_ausencia"
    __table_args__ = {"schema": "rrhh"}
    code: Mapped[int] = mapped_column("codigo", Integer, primary_key=True)
    category: Mapped[str] = mapped_column("categoria", String(100))
    description: Mapped[str] = mapped_column("descripcion", String(200))
    productivity_impact: Mapped[str | None] = mapped_column("impacto_productividad", String(100))


class AbsenceEmployee(Base):
    __tablename__ = "ausentismo_empleados"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee2_id: Mapped[int | None] = mapped_column("empleado2_id", BigInteger)
    employee_number: Mapped[str] = mapped_column("legajo", String(100))
    name: Mapped[str] = mapped_column("nombre", String(350))
    area: Mapped[str | None] = mapped_column(String(150))
    plant: Mapped[str | None] = mapped_column("planta", String(150))
    start_date: Mapped[date | None] = mapped_column("fecha_ingreso", Date)
    end_date: Mapped[date | None] = mapped_column("fecha_baja", Date)


class Absence(Base):
    __tablename__ = "ausencias"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee2_id: Mapped[int | None] = mapped_column("empleado2_id", BigInteger)
    type_code: Mapped[int] = mapped_column("tipo_codigo", ForeignKey("rrhh.tipos_ausencia.codigo"))
    date_from: Mapped[date] = mapped_column("fecha_inicio", Date)
    date_to: Mapped[date] = mapped_column("fecha_fin", Date)
    calendar_days: Mapped[int] = mapped_column("dias_calendario", Integer)
    source_employee_number: Mapped[str] = mapped_column("legajo_origen", String(100))
    source_name: Mapped[str | None] = mapped_column("nombre_origen", String(350))
    source_area: Mapped[str | None] = mapped_column("area_origen", String(150))
    source_plant: Mapped[str | None] = mapped_column("planta_origen", String(150))
    source_description: Mapped[str | None] = mapped_column("tipo_descripcion_origen", String(200))
    source: Mapped[str] = mapped_column("origen", String(30))
    source_reference: Mapped[str] = mapped_column("referencia_origen", String(150))
    source_file: Mapped[str | None] = mapped_column("archivo_origen", String(255))
    import_observations: Mapped[str | None] = mapped_column("observaciones_importacion", Text)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)
    absence_type: Mapped[AbsenceType] = relationship(lazy="joined")
