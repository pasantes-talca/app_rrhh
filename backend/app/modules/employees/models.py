from datetime import date

from sqlalchemy import BigInteger, Boolean, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class EmployeeReadModel(Base):
    __tablename__ = "empleados2"
    __table_args__ = {"schema": "rrhh"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_usuario: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    numero_legajo: Mapped[str | None] = mapped_column(String(100))
    numero_documento: Mapped[str | None] = mapped_column(String(100))
    nombre: Mapped[str | None] = mapped_column(String(150))
    apellido: Mapped[str | None] = mapped_column(String(150))
    nombre_completo: Mapped[str | None] = mapped_column(String(350))
    empresa: Mapped[str | None] = mapped_column(String(150))
    sector: Mapped[str | None] = mapped_column(String(150))
    puesto: Mapped[str | None] = mapped_column(String(150))
    fecha_ingreso: Mapped[date | None] = mapped_column(Date)
    presente_en_origen: Mapped[bool] = mapped_column(Boolean, default=False)
    correo: Mapped[str | None] = mapped_column(String(120))
    telefono: Mapped[str | None] = mapped_column(String(100))
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date)
    sexo: Mapped[str | None] = mapped_column(String(50))
    domicilio: Mapped[str | None] = mapped_column(String(300))
    provincia: Mapped[str | None] = mapped_column(String(100))
    codigo_postal: Mapped[str | None] = mapped_column(String(20))
    cuil: Mapped[str | None] = mapped_column(String(100))
    licencia_conducir: Mapped[str | None] = mapped_column(String(100))

