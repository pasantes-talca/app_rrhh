from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.modules.auth.models import User
from app.modules.licenses.models import LegacyEmployee


class DocumentType(Base):
    __tablename__ = "tipos_documento"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column("nombre", String(100))
    description: Mapped[str | None] = mapped_column("descripcion", Text)
    active: Mapped[bool] = mapped_column("activo", Boolean)


class HrDocument(Base):
    __tablename__ = "documentos_rrhh"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int | None] = mapped_column("empleado_id", ForeignKey("rrhh.empleados.id"))
    type_id: Mapped[int] = mapped_column("tipo_documento_id", ForeignKey("rrhh.tipos_documento.id"))
    name: Mapped[str] = mapped_column("nombre_documento", String(200))
    original_filename: Mapped[str | None] = mapped_column("nombre_archivo", String(255))
    file_path: Mapped[str] = mapped_column("ruta_archivo", Text)
    visible_to_employee: Mapped[bool] = mapped_column("visible_empleado", Boolean)
    observations: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str] = mapped_column("estado", String(50))
    uploaded_by: Mapped[int] = mapped_column("cargado_por", ForeignKey("rrhh.usuarios.id"))
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)
    employee: Mapped[LegacyEmployee | None] = relationship(lazy="joined")
    document_type: Mapped[DocumentType] = relationship(lazy="joined")
    uploader: Mapped[User] = relationship(lazy="joined")


class PayrollReceipt(Base):
    __tablename__ = "recibos_sueldo"
    __table_args__ = (UniqueConstraint("empleado_id", "periodo", name="uq_recibo_empleado_periodo"), {"schema": "rrhh"})
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column("documento_id", ForeignKey("rrhh.documentos_rrhh.id"), unique=True)
    employee_id: Mapped[int] = mapped_column("empleado_id", ForeignKey("rrhh.empleados.id"))
    period: Mapped[str] = mapped_column("periodo", String(7))
    deadline: Mapped[date | None] = mapped_column("fecha_limite", Date)
    state: Mapped[str] = mapped_column("estado", String(30))
    viewed_at: Mapped[datetime | None] = mapped_column("visualizado_en", DateTime)
    responded_at: Mapped[datetime | None] = mapped_column("respondido_en", DateTime)
    response: Mapped[str | None] = mapped_column(String(20))
    employee_observation: Mapped[str | None] = mapped_column("observacion_empleado", Text)
    file_hash: Mapped[str] = mapped_column("hash_archivo", String(64))
    response_ip: Mapped[str | None] = mapped_column("ip_respuesta", String(64))
    user_agent: Mapped[str | None] = mapped_column("agente_usuario", Text)
    published_by: Mapped[int] = mapped_column("publicado_por", ForeignKey("rrhh.usuarios.id"))
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)
    document: Mapped[HrDocument] = relationship(lazy="joined")
    employee: Mapped[LegacyEmployee] = relationship(lazy="joined")

