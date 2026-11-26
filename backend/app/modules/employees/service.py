from .repository import EmployeeRepository


class EmployeeService:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    def list_active(self, query: str, page: int, page_size: int):
        rows, total = self.repository.list_active(query, page, page_size)
        items = [{
            "id": row.id,
            "numero_legajo": row.numero_legajo,
            "display_name": row.nombre_completo or f"{row.apellido or ''} {row.nombre or ''}".strip(),
            "company": row.empresa,
            "sector": row.sector,
            "position": row.puesto,
        } for row in rows]
        return items, total

