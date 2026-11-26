from calendar import monthrange
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session
from app.core.security import Principal, current_principal
from app.database.session import get_session
from app.modules.auth.models import Role, User
from app.modules.communications.models import ImportantDate, News
from app.modules.documents.models import HrDocument, PayrollReceipt
from app.modules.licenses.models import LegacyEmployee, LeaveRequest
from app.modules.overtime.models import Overtime
from app.modules.self_service.daily_notifications import ensure_daily_notifications
from .schemas import BirthdayView, CalendarEvent, DashboardCounts, DashboardOverview

router=APIRouter(prefix="/dashboard",tags=["dashboard"]); MANAGEMENT={"administrador","recursos_humanos"}

def _next_birthday(born:date,today:date)->date:
    try: candidate=born.replace(year=today.year)
    except ValueError: candidate=date(today.year,2,28)
    if candidate<today:
        try:candidate=born.replace(year=today.year+1)
        except ValueError:candidate=date(today.year+1,2,28)
    return candidate

@router.get("",response_model=DashboardOverview)
def dashboard(year:int|None=Query(None,ge=2000,le=2200),month:int|None=Query(None,ge=1,le=12),principal:Principal=Depends(current_principal),session:Session=Depends(get_session)):
    today=date.today();ensure_daily_notifications(session,principal,today);year=year or today.year;month=month or today.month;management=principal.role in MANAGEMENT
    user=session.get(User,principal.user_id);employee=session.get(LegacyEmployee,principal.employee_id) if principal.employee_id else None;name=(employee.display_name.split()[0].title() if employee and employee.display_name else user.username if user else "Usuario")
    people=session.scalars(select(LegacyEmployee).where(LegacyEmployee.state=="Activo",LegacyEmployee.birth_date.is_not(None))).all();birthdays=[];calendar_events=[]
    for person in people:
        upcoming=_next_birthday(person.birth_date,today);days=(upcoming-today).days
        if days<=30:birthdays.append(BirthdayView(employee_name=person.display_name,date=upcoming,days=days,age=upcoming.year-person.birth_date.year))
        if person.birth_date.month==month:
            day=min(person.birth_date.day,monthrange(year,month)[1]);calendar_events.append(CalendarEvent(date=date(year,month,day),title=person.display_name,kind="birthday"))
    birthdays.sort(key=lambda item:(item.days,item.employee_name.casefold()))
    start=date(year,month,1);end=date(year,month,monthrange(year,month)[1]);holidays=session.scalars(select(ImportantDate).where(ImportantDate.date.between(start,end))).all();calendar_events.extend(CalendarEvent(date=item.date,title=item.description or "Fecha importante",kind="holiday") for item in holidays)
    news_statement=select(News).where(News.status=="Publicada",News.is_important_date.is_(True),News.important_date.between(start,end))
    if not management:
        news_statement=news_statement.where(News.visible_to_all.is_(True) if employee is None else or_(News.visible_to_all.is_(True),News.company_id==employee.company_id,News.sector_id==employee.sector_id))
    calendar_events.extend(CalendarEvent(date=item.important_date,title=item.title,kind="news") for item in session.scalars(news_statement).all())
    until=today+timedelta(days=120);upcoming=[CalendarEvent(date=item.date,title=item.description or "Fecha importante",kind="holiday") for item in session.scalars(select(ImportantDate).where(ImportantDate.date.between(today,until))).all()]
    future_news=select(News).where(News.status=="Publicada",News.is_important_date.is_(True),News.important_date.between(today,until))
    if not management:future_news=future_news.where(News.visible_to_all.is_(True) if employee is None else or_(News.visible_to_all.is_(True),News.company_id==employee.company_id,News.sector_id==employee.sector_id))
    upcoming.extend(CalendarEvent(date=item.important_date,title=item.title,kind="news") for item in session.scalars(future_news).all());upcoming=sorted(upcoming,key=lambda item:(item.date,item.kind))[:5]
    if management:
        counts=DashboardCounts(active_employees=session.scalar(select(func.count()).select_from(LegacyEmployee).where(LegacyEmployee.state=="Activo")) or 0,pending_licenses=session.scalar(select(func.count()).select_from(LeaveRequest).where(LeaveRequest.status=="Pendiente")) or 0,pending_overtime=session.scalar(select(func.count()).select_from(Overtime).where(Overtime.state=="Pendiente")) or 0,received_documents=session.scalar(select(func.count()).select_from(HrDocument).join(User,HrDocument.uploaded_by==User.id).join(Role,User.role_id==Role.id).where(HrDocument.state=="Activo",Role.name=="empleado")) or 0,pending_receipts=session.scalar(select(func.count()).select_from(PayrollReceipt).where(PayrollReceipt.state=="Pendiente")) or 0)
    else:
        eid=principal.employee_id
        counts=DashboardCounts(active_employees=None,pending_licenses=session.scalar(select(func.count()).select_from(LeaveRequest).where(LeaveRequest.employee_id==eid,LeaveRequest.status=="Pendiente")) or 0,pending_overtime=session.scalar(select(func.count()).select_from(Overtime).where(Overtime.employee_id==eid,Overtime.state=="Pendiente")) or 0,received_documents=session.scalar(select(func.count()).select_from(HrDocument).where(HrDocument.employee_id==eid,HrDocument.visible_to_employee.is_(True),HrDocument.state=="Activo")) or 0,pending_receipts=session.scalar(select(func.count()).select_from(PayrollReceipt).where(PayrollReceipt.employee_id==eid,PayrollReceipt.state=="Pendiente")) or 0)
    birthday_today=bool(employee and employee.birth_date and (employee.birth_date.month,employee.birth_date.day)==(today.month,today.day))
    return DashboardOverview(name=name,management=management,birthday_today=birthday_today,counts=counts,birthdays=birthdays,upcoming_events=upcoming,calendar_events=sorted(calendar_events,key=lambda item:item.date),year=year,month=month)
