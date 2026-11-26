from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Position(Base):
    __tablename__ = "puestos"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column("nombre", String(100))
    active: Mapped[bool] = mapped_column("activo", Boolean)


class WorkSchedule(Base):
    __tablename__ = "jornadas"
    __table_args__ = {"schema": "rrhh"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column("nombre", String(100))
    active: Mapped[bool] = mapped_column("activo", Boolean)
