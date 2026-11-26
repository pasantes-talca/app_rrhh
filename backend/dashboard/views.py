from calendar import monthrange
from datetime import date, timedelta

from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response


MANAGEMENT_ROLES = {"administrador", "recursos_humanos"}


def _scalar(sql, params=()):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()
    return int(row[0] or 0)


def _next_birthday(born, today):
    try:
        candidate = born.replace(year=today.year)
    except ValueError:
        candidate = date(today.year, 2, 28)
    if candidate < today:
        try:
            candidate = born.replace(year=today.year + 1)
        except ValueError:
            candidate = date(today.year + 1, 2, 28)
    return candidate


@api_view(["GET"])
def resumen(request):
    today = date.today()
    year = min(max(int(request.query_params.get("year", today.year)), 2000), 2200)
    month = min(max(int(request.query_params.get("month", today.month)), 1), 12)
    management = request.user.rol.nombre in MANAGEMENT_ROLES
    employee_id = request.user.empleado_id
    name = (request.user.nombre_mostrar or request.user.usuario or "Usuario").split()[0].title()

    if management:
        counts = {
            "active_employees": _scalar("SELECT count(*) FROM rrhh.empleados WHERE estado = %s", ["Activo"]),
            "pending_licenses": _scalar("SELECT count(*) FROM rrhh.licencias WHERE estado = %s", ["Pendiente"]),
            "pending_overtime": _scalar("SELECT count(*) FROM rrhh.horas_extra WHERE estado = %s", ["Pendiente"]),
            "received_documents": _scalar("SELECT count(*) FROM rrhh.documentos_rrhh WHERE estado = %s", ["Activo"]),
            "pending_receipts": _scalar("SELECT count(*) FROM rrhh.recibos_sueldo WHERE estado = %s", ["Pendiente"]),
        }
    else:
        counts = {
            "active_employees": None,
            "pending_licenses": _scalar("SELECT count(*) FROM rrhh.licencias WHERE empleado_id = %s AND estado = %s", [employee_id, "Pendiente"]) if employee_id else 0,
            "pending_overtime": _scalar("SELECT count(*) FROM rrhh.horas_extra WHERE empleado_id = %s AND estado = %s", [employee_id, "Pendiente"]) if employee_id else 0,
            "received_documents": _scalar("SELECT count(*) FROM rrhh.documentos_rrhh WHERE empleado_id = %s AND visible_empleado IS TRUE AND estado = %s", [employee_id, "Activo"]) if employee_id else 0,
            "pending_receipts": _scalar("SELECT count(*) FROM rrhh.recibos_sueldo WHERE empleado_id = %s AND estado = %s", [employee_id, "Pendiente"]) if employee_id else 0,
        }

    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre_apellido, fecha_nacimiento FROM rrhh.empleados WHERE estado = %s AND fecha_nacimiento IS NOT NULL", ["Activo"])
        people = cursor.fetchall()
        cursor.execute("SELECT fecha, COALESCE(descripcion, %s) FROM rrhh.feriados WHERE fecha BETWEEN %s AND %s ORDER BY fecha", ["Fecha importante", today, today + timedelta(days=120)])
        important_dates = cursor.fetchall()

    birthdays = []
    calendar_events = []
    for employee_name, born in people:
        upcoming = _next_birthday(born, today)
        days = (upcoming - today).days
        if days <= 30:
            birthdays.append({"employee_name": employee_name, "date": upcoming, "days": days, "age": upcoming.year - born.year})
        if born.month == month:
            day = min(born.day, monthrange(year, month)[1])
            calendar_events.append({"date": date(year, month, day), "title": employee_name, "kind": "birthday"})
    birthdays.sort(key=lambda item: (item["days"], item["employee_name"].casefold()))

    upcoming_events = []
    for event_date, title in important_dates:
        event = {"date": event_date, "title": title, "kind": "holiday"}
        upcoming_events.append(event)
        if event_date.year == year and event_date.month == month:
            calendar_events.append(event)

    birthday_today = False
    if employee_id:
        with connection.cursor() as cursor:
            cursor.execute("SELECT fecha_nacimiento FROM rrhh.empleados WHERE id = %s", [employee_id])
            row = cursor.fetchone()
        birthday_today = bool(row and row[0] and (row[0].month, row[0].day) == (today.month, today.day))

    return Response({
        "name": name,
        "management": management,
        "birthday_today": birthday_today,
        "counts": counts,
        "birthdays": birthdays,
        "upcoming_events": upcoming_events[:5],
        "calendar_events": sorted(calendar_events, key=lambda item: item["date"]),
        "year": year,
        "month": month,
    })
