from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import Principal, require_permission
from app.database.session import build_session_factory
from .models import EmployeeReadModel
from .repository import EmployeeRepository
from .schemas import EmployeeDetail, EmployeePage
from .service import EmployeeService


router = APIRouter(prefix="/employees", tags=["employees"])


def database_session():
    session = build_session_factory()()
    try:
        yield session
    finally:
        session.close()


@router.get("", response_model=EmployeePage)
def list_employees(
    q: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    session: Session = Depends(database_session),
    principal: Principal = Depends(require_permission("employees:read")),
):
    items, total = EmployeeService(EmployeeRepository(session)).list_active(q, page, page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{employee_id}", response_model=EmployeeDetail)
def employee_detail(
    employee_id: int,
    session: Session = Depends(database_session),
    principal: Principal = Depends(require_permission("employees:read")),
):
    item = session.get(EmployeeReadModel, employee_id)
    if item is None:
        raise HTTPException(status_code=404, detail="employee_not_found")
    return item

