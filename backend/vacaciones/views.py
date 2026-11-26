from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from empleados.models import Empleado
from licencias.models import SolicitudLicencia

from .models import MovimientoVacaciones, SaldoVacaciones

MANAGEMENT_ROLES = {"administrador", "recursos_humanos", "gerencia"}


def seniority_months(start_date, year):
    if start_date is None:
        return None
    end = date(year, 12, 31)
    if start_date > end:
        return 0
    return (end.year - start_date.year) * 12 + end.month - start_date.month - (1 if end.day < start_date.day else 0)


def entitled_days(months):
    if months is None or months < 6:
        return None
    if months <= 60:
        return Decimal("14")
    if months <= 120:
        return Decimal("21")
    if months <= 240:
        return Decimal("28")
    return Decimal("35")


@api_view(["GET"])
def resumen(request):
    year = int(request.query_params.get("year", date.today().year))
    if request.user.empleado2_id is None:
        return Response({"detail": "user_has_no_employee2"}, status=status.HTTP_409_CONFLICT)
    try:
        employee = Empleado.objects.get(pk=request.user.empleado2_id)
    except Empleado.DoesNotExist:
        return Response({"detail": "employee_not_found"}, status=status.HTTP_404_NOT_FOUND)
    balance = SaldoVacaciones.objects.filter(empleado_id=employee.id, periodo=year).first()
    months = balance.antiguedad_meses if balance else seniority_months(employee.fecha_ingreso, year)
    entitlement = balance.dias_correspondientes if balance else entitled_days(months)
    requests = SolicitudLicencia.objects.none()
    if request.user.empleado_id:
        requests = SolicitudLicencia.objects.select_related("tipo_licencia").filter(
            empleado_id=request.user.empleado_id,
            fecha_desde__year=year,
            tipo_licencia__nombre__icontains="vac",
        )
    used = sum((item.cantidad_dias or Decimal("0") for item in requests if item.estado == "Aprobada"), Decimal("0"))
    reserved = sum((item.cantidad_dias or Decimal("0") for item in requests if item.estado == "Pendiente"), Decimal("0"))
    current = balance.saldo_disponible if balance else max(Decimal("0"), (entitlement or Decimal("0")) - used)
    return Response({
        "year": year,
        "employee_name": employee.display_name,
        "employee_number": employee.numero_legajo,
        "start_date": employee.fecha_ingreso,
        "seniority_months": months,
        "entitled_days": entitlement,
        "used_days": used,
        "reserved_days": reserved,
        "current_balance": current,
        "available_to_request": max(Decimal("0"), current - reserved),
        "source": balance.origen if balance else "CALCULO",
    })


@api_view(["GET"])
def calendario(request):
    year = int(request.query_params.get("year", date.today().year))
    month = int(request.query_params.get("month", date.today().month))
    management = request.user.rol.nombre in MANAGEMENT_ROLES
    if not management and request.user.empleado2_id is None:
        return Response({"detail": "user_has_no_employee2"}, status=status.HTTP_409_CONFLICT)
    first = date(year, month, 1)
    last = date(year, month, monthrange(year, month)[1])
    queryset = MovimientoVacaciones.objects.select_related("empleado").filter(
        fecha_desde__isnull=False,
        fecha_hasta__isnull=False,
        fecha_desde__lte=last,
        fecha_hasta__gte=first,
    )
    if not management:
        queryset = queryset.filter(empleado_id=request.user.empleado2_id)
    elif query := request.query_params.get("q", "").strip():
        queryset = queryset.filter(
            Q(empleado__nombre_completo__icontains=query)
            | Q(empleado__nombre__icontains=query)
            | Q(empleado__apellido__icontains=query)
            | Q(empleado__numero_legajo__icontains=query)
        )
    events = []
    for movement in queryset.order_by("fecha_desde"):
        visual_to = movement.fecha_hasta
        span = (movement.fecha_hasta - movement.fecha_desde).days + 1
        informed = int(movement.dias or 0)
        if span > 60 and 0 < informed <= 60:
            visual_to = movement.fecha_desde + timedelta(days=informed - 1)
        if movement.fecha_desde > last or visual_to < first:
            continue
        events.append({
            "key": f"movement-{movement.id}",
            "employee2_id": movement.empleado_id,
            "employee_name": movement.empleado.display_name,
            "employee_number": movement.empleado.numero_legajo,
            "date_from": movement.fecha_desde,
            "date_to": visual_to,
            "original_date_to": movement.fecha_hasta,
            "inconsistent_date": visual_to != movement.fecha_hasta,
            "days": movement.dias,
            "status": "Histórica",
            "kind": "historical",
            "detail": movement.observaciones or movement.detalle,
        })
    return Response({
        "year": year,
        "month": month,
        "management_view": management,
        "people_count": len({event["employee2_id"] for event in events}),
        "events": events,
    })
