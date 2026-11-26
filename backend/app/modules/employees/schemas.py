from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EmployeeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_number: str | None = Field(alias="numero_legajo")
    display_name: str
    company: str | None
    sector: str | None
    position: str | None


class EmployeePage(BaseModel):
    items: list[EmployeeSummary]
    total: int
    page: int
    page_size: int


class EmployeeDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero_legajo: str | None
    numero_documento: str | None
    nombre: str | None
    apellido: str | None
    nombre_completo: str | None
    empresa: str | None
    sector: str | None
    puesto: str | None
    fecha_ingreso: date | None
    correo: str | None
    telefono: str | None
    fecha_nacimiento: date | None
    sexo: str | None
    domicilio: str | None
    provincia: str | None
    codigo_postal: str | None
    cuil: str | None
    licencia_conducir: str | None

