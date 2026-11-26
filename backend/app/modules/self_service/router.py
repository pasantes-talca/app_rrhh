from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal, verify_csrf
from app.database.session import get_session
from .daily_notifications import ensure_daily_notifications
from .models import ChecklistTask, Notification
from .schemas import ChecklistCreate, ChecklistView, NotificationView

router = APIRouter(tags=["self-service"])


@router.get("/notifications", response_model=list[NotificationView])
def notifications(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    ensure_daily_notifications(session, principal)
    return session.scalars(select(Notification).where(Notification.user_id == principal.user_id).order_by(Notification.created_at.desc()).limit(100)).all()


@router.post("/notifications/{notification_id}/read", status_code=204)
def read_notification(notification_id: int, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    item = session.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == principal.user_id))
    if item is None:
        raise HTTPException(status_code=404, detail="notification_not_found")
    item.read = True
    item.read_at = datetime.utcnow()
    session.commit()


@router.post("/notifications/read-all", status_code=204)
def read_all_notifications(request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    session.execute(update(Notification).where(Notification.user_id == principal.user_id, Notification.read.is_(False)).values(read=True, read_at=datetime.utcnow()))
    session.commit()


@router.get("/checklist", response_model=list[ChecklistView])
def checklist(principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    return session.scalars(select(ChecklistTask).where(ChecklistTask.user_id == principal.user_id).order_by(ChecklistTask.completed, ChecklistTask.created_at.desc())).all()


@router.post("/checklist", response_model=ChecklistView, status_code=status.HTTP_201_CREATED)
def create_task(payload: ChecklistCreate, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    task = ChecklistTask(user_id=principal.user_id, description=payload.description.strip(), completed=False, created_at=datetime.utcnow())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.post("/checklist/{task_id}/toggle", response_model=ChecklistView)
def toggle_task(task_id: int, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    task = session.scalar(select(ChecklistTask).where(ChecklistTask.id == task_id, ChecklistTask.user_id == principal.user_id))
    if task is None:
        raise HTTPException(status_code=404, detail="task_not_found")
    task.completed = not task.completed
    task.completed_at = datetime.utcnow() if task.completed else None
    session.commit()
    session.refresh(task)
    return task


@router.delete("/checklist/{task_id}", status_code=204)
def delete_task(task_id: int, request: Request, principal: Principal = Depends(current_principal), session: Session = Depends(get_session)):
    verify_csrf(request)
    task = session.scalar(select(ChecklistTask).where(ChecklistTask.id == task_id, ChecklistTask.user_id == principal.user_id))
    if task is None:
        raise HTTPException(status_code=404, detail="task_not_found")
    session.delete(task)
    session.commit()
