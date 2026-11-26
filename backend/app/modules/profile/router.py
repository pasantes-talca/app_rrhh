from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal, verify_csrf
from app.database.session import get_session
from app.modules.auth.models import User
from app.modules.employees.models import EmployeeReadModel
from app.modules.licenses.models import LegacyEmployee
from app.modules.overtime.models import Company, Sector
from app.shared.files import resolve_private_path, save_upload
from .models import Position, WorkSchedule
from .schemas import CatalogItem, ProfileCatalogs, ProfileUpdate, ProfileView

router = APIRouter(prefix="/profile", tags=["profile"])
PHOTO_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
EMPLOYEE_STATES = {"Activo", "Inactivo", "Baja", "Licencia", "Suspendido"}


def _clean(value: str | None) -> str | None:
    return value.strip() or None if value else None


def _view(user: User, employee: LegacyEmployee | None, employee2: EmployeeReadModel | None) -> ProfileView:
    fallback_name = " ".join(filter(None, [employee2.nombre, employee2.apellido])) if employee2 else user.username
    return ProfileView(username=user.username, display_name=user.display_name or (employee.display_name if employee else fallback_name), email=user.email or (employee.email if employee else employee2.correo if employee2 else None), has_photo=bool(user.profile_photo), employee_id=user.employee_id, source_employee2=employee2 is not None, phone=employee.phone if employee else employee2.telefono if employee2 else None, birth_date=employee.birth_date if employee else employee2.fecha_nacimiento if employee2 else None, gender=employee.gender if employee else employee2.sexo if employee2 else None, address=employee.address if employee else employee2.domicilio if employee2 else None, province=employee.province if employee else employee2.provincia if employee2 else None, postal_code=employee.postal_code if employee else employee2.codigo_postal if employee2 else None, driver_license=employee.driver_license if employee else employee2.licencia_conducir if employee2 else None, document_number=employee.document_number if employee else employee2.numero_documento if employee2 else None, cuil=employee.cuil if employee else employee2.cuil if employee2 else None, employee_number=employee.employee_number if employee else employee2.numero_legajo if employee2 else None, company_id=employee.company_id if employee else None, sector_id=employee.sector_id if employee else None, position_id=employee.position_id if employee else None, supervisor_id=employee.supervisor_id if employee else None, schedule_id=employee.schedule_id if employee else None, workday_hours=employee.workday_hours if employee else None, start_date=employee.start_date if employee else employee2.fecha_ingreso if employee2 else None, employee_state=employee.state if employee else None)


@router.get("", response_model=ProfileView)
def profile(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    user = session.get(User, principal.user_id)
    if user is None: raise HTTPException(status_code=404, detail="user_not_found")
    return _view(user, session.get(LegacyEmployee, user.employee_id) if user.employee_id else None, session.get(EmployeeReadModel, user.employee2_id) if user.employee2_id else None)


@router.get("/catalogs", response_model=ProfileCatalogs)
def catalogs(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    def items(model): return [CatalogItem(id=item.id, name=item.name) for item in session.scalars(select(model).where(model.active.is_(True)).order_by(model.name)).all()]
    supervisors = [CatalogItem(id=item.id, name=item.display_name) for item in session.scalars(select(LegacyEmployee).where(LegacyEmployee.id != (principal.employee_id or 0), LegacyEmployee.state == "Activo").order_by(LegacyEmployee.display_name)).all()]
    return ProfileCatalogs(companies=items(Company), sectors=items(Sector), positions=items(Position), schedules=items(WorkSchedule), supervisors=supervisors)


@router.put("", response_model=ProfileView)
def update_profile(payload: ProfileUpdate, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    user = session.get(User, principal.user_id); employee = session.get(LegacyEmployee, user.employee_id) if user and user.employee_id else None
    if user is None: raise HTTPException(status_code=404, detail="user_not_found")
    email = _clean(payload.email); document = _clean(payload.document_number); cuil = _clean(payload.cuil); number = _clean(payload.employee_number)
    if email and session.scalar(select(User.id).where(User.email == email, User.id != user.id)): raise HTTPException(status_code=409, detail="email_already_used")
    if employee:
        if not document: raise HTTPException(status_code=422, detail="document_number_required")
        if not number: raise HTTPException(status_code=422, detail="employee_number_required")
        duplicate = session.scalar(select(LegacyEmployee.id).where(LegacyEmployee.id != employee.id, or_(LegacyEmployee.document_number == document, LegacyEmployee.employee_number == number, LegacyEmployee.cuil == cuil if cuil else False)))
        if duplicate: raise HTTPException(status_code=409, detail="employee_identity_already_used")
        if payload.employee_state not in EMPLOYEE_STATES: raise HTTPException(status_code=422, detail="invalid_employee_state")
    user.display_name, user.email = payload.display_name.strip(), email
    if employee:
        employee.display_name, employee.email, employee.phone = user.display_name, email, _clean(payload.phone)
        employee.birth_date, employee.gender, employee.address = payload.birth_date, _clean(payload.gender), _clean(payload.address)
        employee.province, employee.postal_code, employee.driver_license = _clean(payload.province), _clean(payload.postal_code), _clean(payload.driver_license)
        employee.document_number, employee.cuil, employee.employee_number = document, cuil, number
        employee.company_id, employee.sector_id, employee.position_id = payload.company_id, payload.sector_id, payload.position_id
        employee.supervisor_id, employee.schedule_id, employee.workday_hours = payload.supervisor_id, payload.schedule_id, payload.workday_hours
        employee.start_date, employee.state = payload.start_date, payload.employee_state
        if not user.employee2_id: user.username = number
    session.commit()
    employee2 = session.get(EmployeeReadModel, user.employee2_id) if user.employee2_id else None
    return _view(user, employee, employee2)


@router.post("/photo", response_model=ProfileView)
async def upload_photo(request: Request, photo: UploadFile = File(), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); user = session.get(User, principal.user_id)
    if user is None: raise HTTPException(status_code=404, detail="user_not_found")
    path = await save_upload(photo, "profiles", PHOTO_TYPES); user.profile_photo = path; session.commit()
    return _view(user, session.get(LegacyEmployee, user.employee_id) if user.employee_id else None, session.get(EmployeeReadModel, user.employee2_id) if user.employee2_id else None)


@router.delete("/photo", status_code=204)
def delete_photo(request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); user = session.get(User, principal.user_id)
    if user is None: raise HTTPException(status_code=404, detail="user_not_found")
    user.profile_photo = None; session.commit()


@router.get("/photo")
def profile_photo(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    user = session.get(User, principal.user_id)
    if user is None or not user.profile_photo: raise HTTPException(status_code=404, detail="photo_not_found")
    path = user.profile_photo if "/" in user.profile_photo or "\\" in user.profile_photo else str(Path("profiles") / user.profile_photo)
    return FileResponse(resolve_private_path(path))
