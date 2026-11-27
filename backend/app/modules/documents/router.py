from datetime import datetime
import os
from hashlib import sha256
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal, verify_csrf
from app.database.session import get_session
from app.modules.auth.models import Role, User
from app.modules.licenses.models import LegacyEmployee
from app.modules.self_service.models import Notification
from app.shared.files import resolve_private_path, save_upload
from .models import DocumentType, HrDocument, PayrollReceipt
from .schemas import DocumentTypeView, DocumentView, EmployeeFolder, ReceiptResponse, ReceiptSummary, ReceiptView

router = APIRouter(prefix="/documents", tags=["documents"])
MANAGEMENT_ROLES = {"administrador", "recursos_humanos"}
DOCUMENT_TYPES = frozenset({"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation", "text/plain", "image/jpeg", "image/png", "image/gif", "image/webp"})
PDF_TYPES = frozenset({"application/pdf"})


def _management(principal: Principal) -> None:
    if principal.role not in MANAGEMENT_ROLES:
        raise HTTPException(status_code=403, detail="permission_denied")


def _source(item: HrDocument) -> str:
    return "employee" if item.uploader.role.name == "empleado" else "hr"


def _document_view(item: HrDocument) -> DocumentView:
    return DocumentView(id=item.id, employee_id=item.employee_id, employee_name=item.employee.display_name if item.employee else None, employee_number=item.employee.employee_number if item.employee else None, type_id=item.type_id, type_name=item.document_type.name, name=item.name, original_filename=item.original_filename, visible_to_employee=item.visible_to_employee, observations=item.observations, state=item.state, source=_source(item), created_at=item.created_at)


def _receipt_view(item: PayrollReceipt) -> ReceiptView:
    return ReceiptView(id=item.id, employee_id=item.employee_id, employee_name=item.employee.display_name, employee_number=item.employee.employee_number, period=item.period, deadline=item.deadline, state=item.state, viewed_at=item.viewed_at, responded_at=item.responded_at, response=item.response, employee_observation=item.employee_observation, original_filename=item.document.original_filename, file_hash=item.file_hash, created_at=item.created_at)


def _can_access(item: HrDocument, principal: Principal) -> bool:
    return principal.role in MANAGEMENT_ROLES or item.uploaded_by == principal.user_id or bool(principal.employee_id == item.employee_id and item.visible_to_employee and item.state == "Activo")


def _notify_hr(session: Session, principal: Principal, item: HrDocument) -> None:
    users = session.scalars(select(User).join(Role).where(Role.name.in_(MANAGEMENT_ROLES), User.active.is_(True), User.id != principal.user_id)).all()
    for user in users:
        session.add(Notification(user_id=user.id, title="Documento recibido de un empleado", message=f"{item.employee.display_name} enviÃ³ el documento: {item.name}.", kind="documento", reference_type="documento_empleado", reference_id=item.id, read=False, created_at=datetime.utcnow()))


def _notify_employee(session: Session, item: HrDocument, title: str, message: str, reference_type: str = "documento", reference_id: int | None = None) -> None:
    user = session.scalar(select(User).where(User.employee_id == item.employee_id, User.active.is_(True)))
    if user:
        session.add(Notification(user_id=user.id, title=title, message=message, kind="documento", reference_type=reference_type, reference_id=reference_id or item.id, read=False, created_at=datetime.utcnow()))


@router.get("/types", response_model=list[DocumentTypeView])
def document_types(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    return session.scalars(select(DocumentType).where(DocumentType.active.is_(True)).order_by(DocumentType.name)).all()


@router.get("", response_model=list[DocumentView])
def documents(q: str = "", state: str = "Activo", private_only: bool = False, employee_id: int | None = None, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    statement = select(HrDocument)
    if principal.role in MANAGEMENT_ROLES:
        if private_only:
            statement = statement.join(HrDocument.uploader).join(User.role).where(Role.name.in_(MANAGEMENT_ROLES), HrDocument.visible_to_employee.is_(False))
        if employee_id:
            statement = statement.where(HrDocument.employee_id == employee_id)
    else:
        if principal.employee_id is None:
            return []
        statement = statement.where(HrDocument.employee_id == principal.employee_id, or_(HrDocument.uploaded_by == principal.user_id, (HrDocument.visible_to_employee.is_(True) & (HrDocument.state == "Activo"))))
    if state in {"Activo", "Archivado"}:
        statement = statement.where(HrDocument.state == state)
    if q.strip():
        pattern = f"%{q.strip()}%"
        statement = statement.outerjoin(HrDocument.employee).where(or_(HrDocument.name.ilike(pattern), HrDocument.original_filename.ilike(pattern), LegacyEmployee.display_name.ilike(pattern), LegacyEmployee.employee_number.ilike(pattern)))
    return [_document_view(item) for item in session.scalars(statement.order_by(HrDocument.created_at.desc())).unique().all()]


@router.get("/folders", response_model=list[EmployeeFolder])
def folders(q: str = "", principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    _management(principal)
    employee_sent = func.count(case((Role.name == "empleado", 1)))
    shared = func.count(case((Role.name.in_(MANAGEMENT_ROLES), 1)))
    statement = select(LegacyEmployee.id, LegacyEmployee.display_name, LegacyEmployee.employee_number, employee_sent, shared, func.count(HrDocument.id), func.max(HrDocument.created_at)).join(HrDocument, HrDocument.employee_id == LegacyEmployee.id).join(User, HrDocument.uploaded_by == User.id).join(Role, User.role_id == Role.id).where(or_(Role.name == "empleado", HrDocument.visible_to_employee.is_(True)))
    if q.strip():
        pattern = f"%{q.strip()}%"
        statement = statement.where(or_(LegacyEmployee.display_name.ilike(pattern), LegacyEmployee.employee_number.ilike(pattern), LegacyEmployee.document_number.ilike(pattern)))
    rows = session.execute(statement.group_by(LegacyEmployee.id).order_by(func.lower(LegacyEmployee.display_name))).all()
    return [EmployeeFolder(employee_id=row[0], employee_name=row[1], employee_number=row[2], employee_sent=row[3], shared_by_hr=row[4], total=row[5], last_document_at=row[6]) for row in rows]


@router.post("", response_model=DocumentView, status_code=201)
async def upload_document(request: Request, type_id: int = Form(), name: str = Form(min_length=1, max_length=200), employee_id: int | None = Form(None), visible_to_employee: bool = Form(False), observations: str | None = Form(None), attachment: UploadFile = File(), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    if session.get(DocumentType, type_id) is None:
        raise HTTPException(status_code=422, detail="invalid_document_type")
    if principal.role in MANAGEMENT_ROLES:
        if employee_id is not None and session.get(LegacyEmployee, employee_id) is None:
            raise HTTPException(status_code=404, detail="employee_not_found")
        target_employee, visible = employee_id, bool(employee_id and visible_to_employee)
    else:
        if principal.employee_id is None:
            raise HTTPException(status_code=422, detail="employee_profile_required")
        target_employee, visible = principal.employee_id, False
    path = await save_upload(attachment, "documents_private", DOCUMENT_TYPES)
    item = HrDocument(employee_id=target_employee, type_id=type_id, name=name.strip(), original_filename=attachment.filename, file_path=path, visible_to_employee=visible, observations=observations, state="Activo", uploaded_by=principal.user_id, created_at=datetime.utcnow())
    session.add(item); session.flush()
    if principal.role in MANAGEMENT_ROLES and visible:
        _notify_employee(session, item, "Nuevo documento disponible", f"RR. HH. compartiÃ³ el documento: {item.name}.")
    elif principal.role not in MANAGEMENT_ROLES:
        _notify_hr(session, principal, item)
    session.commit(); session.refresh(item)
    return _document_view(item)


@router.patch("/items/{document_id}/state", response_model=DocumentView)
def document_state(document_id: int, request: Request, state: str, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); _management(principal)
    if state not in {"Activo", "Archivado"}:
        raise HTTPException(status_code=422, detail="invalid_document_state")
    item = session.get(HrDocument, document_id)
    if item is None: raise HTTPException(status_code=404, detail="document_not_found")
    item.state = state; session.commit(); session.refresh(item)
    return _document_view(item)


@router.put("/items/{document_id}", response_model=DocumentView)
async def update_document(
    document_id: int,
    request: Request,
    type_id: int = Form(),
    name: str = Form(min_length=1, max_length=200),
    employee_id: int | None = Form(None),
    visible_to_employee: bool = Form(False),
    observations: str | None = Form(None),
    attachment: UploadFile | None = File(None),
    principal: Principal = Depends(current_principal),
    session: Session = Depends(get_session),
):
    verify_csrf(request); _management(principal)
    item = session.get(HrDocument, document_id)
    if item is None:
        raise HTTPException(status_code=404, detail="document_not_found")
    if session.get(DocumentType, type_id) is None:
        raise HTTPException(status_code=422, detail="invalid_document_type")
    if employee_id is not None and session.get(LegacyEmployee, employee_id) is None:
        raise HTTPException(status_code=404, detail="employee_not_found")
    previous_visible = item.visible_to_employee
    replacement_path = None
    if attachment and attachment.filename:
        replacement_path = await save_upload(attachment, "documents_private", DOCUMENT_TYPES)
        item.file_path = replacement_path
        item.original_filename = attachment.filename
    item.type_id = type_id
    item.name = name.strip()
    item.employee_id = employee_id
    item.visible_to_employee = bool(employee_id and visible_to_employee)
    item.observations = observations.strip() if observations and observations.strip() else None
    if item.visible_to_employee and not previous_visible:
        _notify_employee(session, item, "Nuevo documento disponible", f"RR. HH. compartió el documento: {item.name}.")
    session.commit(); session.refresh(item)
    return _document_view(item)


@router.get("/files/{document_id}")
def document_file(document_id: int, download: bool = False, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    item = session.get(HrDocument, document_id)
    if item is None or not _can_access(item, principal): raise HTTPException(status_code=404, detail="document_not_found")
    path = item.file_path if "/" in item.file_path or "\\" in item.file_path else str(Path("documents_private") / item.file_path)
    return FileResponse(resolve_private_path(path), filename=item.original_filename if download else None)


@router.get("/receipts/list", response_model=ReceiptSummary)
def receipts(state: str = "", principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    statement = select(PayrollReceipt)
    if principal.role not in MANAGEMENT_ROLES:
        if principal.employee_id is None: return ReceiptSummary(total=0, pending=0, compliant=0, non_compliant=0, items=[])
        statement = statement.where(PayrollReceipt.employee_id == principal.employee_id)
    if state in {"Pendiente", "Conforme", "Disconforme"}: statement = statement.where(PayrollReceipt.state == state)
    items = session.scalars(statement.order_by(PayrollReceipt.period.desc())).unique().all()
    all_states = [row[0] for row in session.execute(select(PayrollReceipt.state).where(PayrollReceipt.employee_id == principal.employee_id)).all()] if principal.role not in MANAGEMENT_ROLES and principal.employee_id else [row[0] for row in session.execute(select(PayrollReceipt.state)).all()]
    return ReceiptSummary(total=len(all_states), pending=all_states.count("Pendiente"), compliant=all_states.count("Conforme"), non_compliant=all_states.count("Disconforme"), items=[_receipt_view(item) for item in items])


@router.post("/receipts", response_model=ReceiptView, status_code=status.HTTP_201_CREATED)
async def publish_receipt(request: Request, employee_id: int = Form(), period: str = Form(pattern=r"^\d{4}-(0[1-9]|1[0-2])$"), deadline: str | None = Form(None), observations: str | None = Form(None), attachment: UploadFile = File(), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request); _management(principal)
    if session.get(LegacyEmployee, employee_id) is None: raise HTTPException(status_code=404, detail="employee_not_found")
    if session.scalar(select(PayrollReceipt).where(PayrollReceipt.employee_id == employee_id, PayrollReceipt.period == period)): raise HTTPException(status_code=409, detail="receipt_period_exists")
    path = await save_upload(attachment, "documents_private", PDF_TYPES)
    physical = resolve_private_path(path)
    digest = sha256(physical.read_bytes()).hexdigest()
    doc_type = session.scalar(select(DocumentType).where(func.lower(DocumentType.name) == "recibo de sueldo"))
    if doc_type is None:
        doc_type = DocumentType(name="Recibo de sueldo", description="Recibo de haberes del empleado", active=True); session.add(doc_type); session.flush()
    readable = f"{period[5:7]}/{period[:4]}"
    document = HrDocument(employee_id=employee_id, type_id=doc_type.id, name=f"Recibo de sueldo - {readable}", original_filename=attachment.filename, file_path=path, visible_to_employee=True, observations=observations, state="Activo", uploaded_by=principal.user_id, created_at=datetime.utcnow())
    session.add(document); session.flush()
    parsed_deadline = datetime.strptime(deadline, "%Y-%m-%d").date() if deadline else None
    item = PayrollReceipt(document_id=document.id, employee_id=employee_id, period=period, deadline=parsed_deadline, state="Pendiente", file_hash=digest, published_by=principal.user_id, created_at=datetime.utcnow())
    session.add(item); session.flush()
    _notify_employee(session, document, "Nuevo recibo de sueldo", f"Tu recibo del perÃ­odo {readable} estÃ¡ disponible para revisar y confirmar.", "recibo_sueldo", item.id)
    session.commit(); session.refresh(item)
    return _receipt_view(item)


@router.post("/receipts/{receipt_id}/view", response_model=ReceiptView)
def mark_receipt_viewed(receipt_id: int, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    item = session.get(PayrollReceipt, receipt_id)
    if item is None or principal.employee_id != item.employee_id: raise HTTPException(status_code=404, detail="receipt_not_found")
    item.viewed_at = item.viewed_at or datetime.utcnow(); session.commit(); session.refresh(item)
    return _receipt_view(item)


@router.post("/receipts/{receipt_id}/respond", response_model=ReceiptView)
def respond_receipt(receipt_id: int, payload: ReceiptResponse, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    if os.environ.get('RECEIPT_PASSKEY_ENABLED', 'false').lower() == 'true':
        raise HTTPException(status_code=403, detail='receipt_passkey_required_use_stable_portal')
    item = session.get(PayrollReceipt, receipt_id)
    if item is None or principal.employee_id != item.employee_id: raise HTTPException(status_code=404, detail="receipt_not_found")
    if item.state != "Pendiente": raise HTTPException(status_code=409, detail="receipt_already_answered")
    if payload.response not in {"Conforme", "Disconforme"}: raise HTTPException(status_code=422, detail="invalid_receipt_response")
    if payload.response == "Disconforme" and not (payload.observation or "").strip(): raise HTTPException(status_code=422, detail="observation_required")
    now = datetime.utcnow(); item.state = payload.response; item.response = payload.response; item.employee_observation = (payload.observation or "").strip() or None; item.responded_at = now; item.viewed_at = item.viewed_at or now; item.response_ip = (request.headers.get("X-Forwarded-For") or (request.client.host if request.client else ""))[:64]; item.user_agent = request.headers.get("User-Agent", "")[:1000]
    users = session.scalars(select(User).join(Role).where(Role.name.in_(MANAGEMENT_ROLES), User.active.is_(True), User.id != principal.user_id)).all()
    for user in users: session.add(Notification(user_id=user.id, title=f"Recibo {payload.response.lower()}", message=f"{item.employee.display_name} respondiÃ³ el recibo del perÃ­odo {item.period}.", kind="recibo", reference_type="recibo_sueldo", reference_id=item.id, read=False, created_at=now))
    session.commit(); session.refresh(item)
    return _receipt_view(item)


@router.get("/receipts/{receipt_id}/file")
def receipt_file(receipt_id: int, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    item = session.get(PayrollReceipt, receipt_id)
    if item is None or (principal.role not in MANAGEMENT_ROLES and principal.employee_id != item.employee_id): raise HTTPException(status_code=404, detail="receipt_not_found")
    if principal.employee_id == item.employee_id and item.viewed_at is None:
        item.viewed_at = datetime.utcnow(); session.commit()
    path = item.document.file_path if "/" in item.document.file_path or "\\" in item.document.file_path else str(Path("documents_private") / item.document.file_path)
    return FileResponse(resolve_private_path(path), filename=item.document.original_filename)
