from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal, verify_csrf
from app.database.session import get_session
from app.modules.auth.models import User
from app.modules.licenses.models import LegacyEmployee
from app.modules.self_service.models import Notification
from app.shared.files import resolve_private_path, save_upload
from .models import ImportantDate, News
from .schemas import ImportantDateCreate, ImportantDateView, NewsView

router = APIRouter(tags=["communications"])
MANAGEMENT_ROLES = {"administrador", "recursos_humanos"}
IMAGE_TYPES = frozenset({"image/jpeg", "image/png", "image/webp", "image/gif"})


def _require_management(principal: Principal) -> None:
    if principal.role not in MANAGEMENT_ROLES:
        raise HTTPException(status_code=403, detail="permission_denied")


def _can_view(news: News, principal: Principal, session: Session) -> bool:
    if principal.role in MANAGEMENT_ROLES:
        return True
    if news.status != "Publicada" or principal.employee_id is None:
        return False
    employee = session.get(LegacyEmployee, principal.employee_id)
    return bool(employee and (news.visible_to_all or news.company_id == employee.company_id or news.sector_id == employee.sector_id))


def _view(news: News) -> NewsView:
    return NewsView(id=news.id, title=news.title, content=news.content, has_image=bool(news.image), visible_to_all=news.visible_to_all, is_important_date=news.is_important_date, important_date=news.important_date, company_id=news.company_id, sector_id=news.sector_id, published_at=news.published_at)


def _recipients(news: News, session: Session):
    statement = select(User).where(User.active.is_(True))
    if not news.visible_to_all:
        conditions = []
        if news.company_id:
            conditions.append(LegacyEmployee.company_id == news.company_id)
        if news.sector_id:
            conditions.append(LegacyEmployee.sector_id == news.sector_id)
        if not conditions:
            return []
        statement = statement.join(LegacyEmployee, User.employee_id == LegacyEmployee.id).where(or_(*conditions))
    return session.scalars(statement).all()


def _notify_news(news: News, principal: Principal, session: Session) -> None:
    message = " ".join(news.content.split())
    message = message if len(message) <= 180 else message[:177] + "..."
    for user in _recipients(news, session):
        if user.id == principal.user_id:
            continue
        existing = session.scalar(select(Notification).where(Notification.user_id == user.id, Notification.reference_type == "noticia", Notification.reference_id == news.id))
        if existing is None:
            session.add(Notification(user_id=user.id, title=news.title, message=message, kind="noticia", reference_type="noticia", reference_id=news.id, read=False, created_at=datetime.utcnow()))


@router.get("/news", response_model=list[NewsView])
def news_feed(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    statement = select(News).where(News.status == "Publicada")
    if principal.role not in MANAGEMENT_ROLES:
        employee = session.get(LegacyEmployee, principal.employee_id) if principal.employee_id else None
        if employee is None:
            return []
        statement = statement.where(or_(News.visible_to_all.is_(True), News.company_id == employee.company_id, News.sector_id == employee.sector_id))
    return [_view(item) for item in session.scalars(statement.order_by(News.published_at.desc())).all()]


@router.get("/news/featured", response_model=list[NewsView])
def featured_news(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    limit_date = datetime.utcnow() - timedelta(days=7)
    items = news_feed(principal, session)
    return [item for item in items if item.published_at and item.published_at >= limit_date][:3]


@router.post("/news", response_model=NewsView, status_code=status.HTTP_201_CREATED)
async def create_news(request: Request, title: str = Form(min_length=1, max_length=200), content: str = Form(min_length=1), visible_to_all: bool = Form(True), is_important_date: bool = Form(False), important_date: date | None = Form(None), company_id: int | None = Form(None), sector_id: int | None = Form(None), image: UploadFile | None = File(None), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    _require_management(principal)
    if is_important_date and important_date is None:
        raise HTTPException(status_code=422, detail="important_date_required")
    image_path = await save_upload(image, "news", IMAGE_TYPES) if image else None
    item = News(title=title.strip(), content=content.strip(), image=image_path, status="Publicada", visible_to_all=visible_to_all, is_important_date=is_important_date, important_date=important_date if is_important_date else None, company_id=company_id, sector_id=sector_id, published_by=principal.user_id, published_at=datetime.utcnow(), created_at=datetime.utcnow())
    session.add(item)
    session.flush()
    _notify_news(item, principal, session)
    session.commit()
    session.refresh(item)
    return _view(item)


@router.put("/news/{news_id}", response_model=NewsView)
async def update_news(news_id: int, request: Request, title: str = Form(min_length=1, max_length=200), content: str = Form(min_length=1), visible_to_all: bool = Form(True), is_important_date: bool = Form(False), important_date: date | None = Form(None), company_id: int | None = Form(None), sector_id: int | None = Form(None), image: UploadFile | None = File(None), principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    _require_management(principal)
    item = session.get(News, news_id)
    if item is None:
        raise HTTPException(status_code=404, detail="news_not_found")
    if is_important_date and important_date is None:
        raise HTTPException(status_code=422, detail="important_date_required")
    item.title, item.content, item.visible_to_all = title.strip(), content.strip(), visible_to_all
    item.is_important_date, item.important_date = is_important_date, important_date if is_important_date else None
    item.company_id, item.sector_id, item.status = company_id, sector_id, "Publicada"
    if image:
        item.image = await save_upload(image, "news", IMAGE_TYPES)
    _notify_news(item, principal, session)
    session.commit()
    session.refresh(item)
    return _view(item)


@router.delete("/news/{news_id}", status_code=204)
def delete_news(news_id: int, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    _require_management(principal)
    item = session.get(News, news_id)
    if item is None:
        raise HTTPException(status_code=404, detail="news_not_found")
    session.delete(item)
    session.commit()


@router.get("/news/{news_id}/image")
def news_image(news_id: int, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    item = session.get(News, news_id)
    if item is None or not item.image:
        raise HTTPException(status_code=404, detail="image_not_found")
    if not _can_view(item, principal, session):
        raise HTTPException(status_code=403, detail="permission_denied")
    return FileResponse(resolve_private_path(item.image))


@router.get("/important-dates", response_model=list[ImportantDateView])
def important_dates(_: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    return session.scalars(select(ImportantDate).order_by(ImportantDate.date)).all()


@router.post("/important-dates", response_model=ImportantDateView, status_code=201)
def create_important_date(payload: ImportantDateCreate, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    _require_management(principal)
    if session.scalar(select(ImportantDate).where(ImportantDate.date == payload.date)):
        raise HTTPException(status_code=409, detail="important_date_already_exists")
    item = ImportantDate(date=payload.date, description=payload.description.strip()[:200], created_at=datetime.utcnow())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/important-dates/{date_id}", status_code=204)
def delete_important_date(date_id: int, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    _require_management(principal)
    item = session.get(ImportantDate, date_id)
    if item is None:
        raise HTTPException(status_code=404, detail="important_date_not_found")
    session.delete(item)
    session.commit()
