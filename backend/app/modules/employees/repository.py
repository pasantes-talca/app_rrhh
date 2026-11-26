from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .models import EmployeeReadModel


class EmployeeRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_active(self, query: str, page: int, page_size: int):
        statement = select(EmployeeReadModel).where(
            EmployeeReadModel.presente_en_origen.is_(True)
        )
        if query:
            pattern = f"%{query.strip()}%"
            statement = statement.where(or_(
                EmployeeReadModel.nombre_completo.ilike(pattern),
                EmployeeReadModel.nombre.ilike(pattern),
                EmployeeReadModel.apellido.ilike(pattern),
                EmployeeReadModel.numero_legajo.ilike(pattern),
            ))
        count = select(func.count()).select_from(statement.subquery())
        total = self.session.scalar(count) or 0
        items = self.session.scalars(
            statement.order_by(EmployeeReadModel.apellido, EmployeeReadModel.nombre)
            .offset((page - 1) * page_size).limit(page_size)
        ).all()
        return items, total

