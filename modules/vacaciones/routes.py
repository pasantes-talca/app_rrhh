from datetime import date
from decimal import Decimal

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from database.models import Licencia, VacacionMovimiento, VacacionSaldo


vacaciones_bp = Blueprint('vacaciones', __name__, url_prefix='/mis-vacaciones')


def _antiguedad_al_cierre(fecha_ingreso, anio):
    """Antigüedad cumplida al 31 de diciembre del año vacacional."""
    cierre = date(anio, 12, 31)
    if not fecha_ingreso or fecha_ingreso > cierre:
        return None
    return cierre.year - fecha_ingreso.year - (
        (cierre.month, cierre.day) < (fecha_ingreso.month, fecha_ingreso.day)
    )


def _meses_antiguedad_al_cierre(fecha_ingreso, anio):
    cierre = date(anio, 12, 31)
    if not fecha_ingreso or fecha_ingreso > cierre:
        return None
    meses = (cierre.year - fecha_ingreso.year) * 12 + cierre.month - fecha_ingreso.month
    return meses - (cierre.day < fecha_ingreso.day)


def _dias_por_antiguedad(meses_antiguedad):
    if meses_antiguedad is None or meses_antiguedad < 6:
        return None
    if meses_antiguedad <= 60:
        return 14
    if meses_antiguedad <= 120:
        return 21
    if meses_antiguedad <= 240:
        return 28
    return 35


def _es_vacacion(licencia):
    nombre = licencia.tipo_licencia.nombre if licencia.tipo_licencia else ''
    return 'vacacion' in nombre.lower().replace('ó', 'o')


@vacaciones_bp.route('/')
@login_required
def index():
    hoy = date.today()
    empleado = current_user.empleado
    empleado2 = current_user.empleado2
    fecha_ingreso = (
        empleado2.fecha_ingreso if empleado2 and empleado2.fecha_ingreso
        else empleado.fecha_ingreso if empleado else None
    )
    nombre = (
        empleado2.nombre_completo if empleado2 and empleado2.nombre_completo
        else f'{empleado2.apellido or ""} {empleado2.nombre or ""}'.strip() if empleado2
        else empleado.nombre_apellido if empleado else current_user.nombre_mostrar or current_user.usuario
    )
    legajo = (
        empleado2.numero_legajo if empleado2 and empleado2.numero_legajo
        else empleado.legajo if empleado else None
    )

    antiguedad = _antiguedad_al_cierre(fecha_ingreso, hoy.year)
    meses_antiguedad = _meses_antiguedad_al_cierre(fecha_ingreso, hoy.year)
    dias_correspondientes = _dias_por_antiguedad(meses_antiguedad)
    saldo_registrado = None
    historial_importado = []
    if empleado2:
        saldo_registrado = VacacionSaldo.query.filter_by(
            empleado2_id=empleado2.id, periodo=hoy.year
        ).first()
        historial_importado = VacacionMovimiento.query.filter_by(
            empleado2_id=empleado2.id, origen='EXCEL'
        ).order_by(VacacionMovimiento.fecha_desde.desc().nullslast()).limit(8).all()
    if saldo_registrado:
        antiguedad = (
            saldo_registrado.antiguedad_meses // 12
            if saldo_registrado.antiguedad_meses is not None else antiguedad
        )
        meses_antiguedad = saldo_registrado.antiguedad_meses
        dias_correspondientes = saldo_registrado.dias_correspondientes
    licencias = []
    if current_user.empleado_id:
        licencias = [
            item for item in Licencia.query.filter_by(empleado_id=current_user.empleado_id)
            .order_by(Licencia.fecha_desde.desc()).all()
            if _es_vacacion(item) and item.fecha_desde.year == hoy.year
        ]

    usados = sum(
        (Decimal(item.cantidad_dias or 0) for item in licencias if item.estado == 'Aprobada'),
        Decimal('0'),
    )
    reservados = sum(
        (Decimal(item.cantidad_dias or 0) for item in licencias if item.estado == 'Pendiente'),
        Decimal('0'),
    )
    if saldo_registrado:
        # El saldo persistido ya contiene los consumos del Excel y no debe descontarse dos veces.
        saldo = Decimal(saldo_registrado.saldo_disponible or 0)
    else:
        saldo = max(Decimal(dias_correspondientes or 0) - usados, Decimal('0'))
    disponible_solicitar = max(saldo - reservados, Decimal('0'))

    return render_template(
        'vacaciones/index.html',
        anio=hoy.year,
        nombre=nombre,
        legajo=legajo,
        fecha_ingreso=fecha_ingreso,
        antiguedad=antiguedad,
        meses_antiguedad=meses_antiguedad,
        dias_correspondientes=dias_correspondientes,
        dias_usados=usados,
        dias_reservados=reservados,
        saldo=saldo,
        disponible_solicitar=disponible_solicitar,
        movimientos=licencias,
        historial_importado=historial_importado,
        saldo_registrado=saldo_registrado,
    )
