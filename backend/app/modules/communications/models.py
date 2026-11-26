from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class News(Base):
    __tablename__ = "noticias"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column("titulo", String(200))
    content: Mapped[str] = mapped_column("contenido", Text)
    image: Mapped[str | None] = mapped_column("imagen", Text)
    status: Mapped[str] = mapped_column("estado", String(50))
    visible_to_all: Mapped[bool] = mapped_column("visible_todos", Boolean)
    is_important_date: Mapped[bool] = mapped_column("es_fecha_importante", Boolean)
    important_date: Mapped[date | None] = mapped_column("fecha_importante", Date)
    company_id: Mapped[int | None] = mapped_column("empresa_id", Integer)
    sector_id: Mapped[int | None] = mapped_column("sector_id", Integer)
    published_by: Mapped[int | None] = mapped_column("publicado_por", Integer)
    published_at: Mapped[datetime | None] = mapped_column("fecha_publicacion", DateTime)
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)


class ImportantDate(Base):
    __tablename__ = "feriados"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column("fecha", Date)
    description: Mapped[str | None] = mapped_column("descripcion", String(200))
    created_at: Mapped[datetime] = mapped_column("creado_en", DateTime)
