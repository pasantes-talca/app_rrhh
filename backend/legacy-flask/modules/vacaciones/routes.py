import calendar
from datetime import date, timedelta
from decimal import Decimal

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from database.models import Empleado2, Licencia, Usuario, VacacionMovimiento, VacacionSaldo


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


def _mes_solicitado():
    hoy = date.today()
    try:
        anio = int(request.args.get('anio', hoy.year))
        mes = int(request.args.get('mes', hoy.month))
        if anio < 2000 or anio > 2100 or mes < 1 or mes > 12:
            raise ValueError
        return date(anio, mes, 1)
    except (TypeError, ValueError):
        return date(hoy.year, hoy.month, 1)


def _nombre_empleado2(empleado):
    return empleado.nombre_completo or f'{empleado.apellido or ""} {empleado.nombre or ""}'.strip() or 'Sin nombre'


def _eventos_calendario(fecha_mes, gestion, empleado2_id=None, busqueda=''):
    if fecha_mes.month == 12:
        siguiente_mes = date(fecha_mes.year + 1, 1, 1)
    else:
        siguiente_mes = date(fecha_mes.year, fecha_mes.month + 1, 1)
    fin_mes = siguiente_mes - timedelta(days=1)

    consulta = VacacionMovimiento.query.join(Empleado2).filter(
        VacacionMovimiento.fecha_desde.isnot(None),
        VacacionMovimiento.fecha_hasta.isnot(None),
        VacacionMovimiento.fecha_desde <= fin_mes,
        VacacionMovimiento.fecha_hasta >= fecha_mes,
    )
    if not gestion:
        consulta = consulta.filter(VacacionMovimiento.empleado2_id == empleado2_id)
    elif busqueda:
        termino = f'%{busqueda}%'
        consulta = consulta.filter(or_(
            Empleado2.nombre_completo.ilike(termino),
            Empleado2.nombre.ilike(termino),
            Empleado2.apellido.ilike(termino),
            Empleado2.numero_legajo.ilike(termino),
        ))

    eventos = []
    for movimiento in consulta.order_by(VacacionMovimiento.fecha_desde).all():
        fecha_hasta_visual = movimiento.fecha_hasta
        rango_dias = (movimiento.fecha_hasta - movimiento.fecha_desde).days + 1
        dias_informados = int(movimiento.dias or 0)
        if rango_dias > 60 and 0 < dias_informados <= 60:
            # Conserva el dato original en PostgreSQL, pero evita que una fecha
            # evidentemente inconsistente pinte meses completos en el calendario.
            fecha_hasta_visual = movimiento.fecha_desde + timedelta(days=dias_informados - 1)
        if movimiento.fecha_desde > fin_mes or fecha_hasta_visual < fecha_mes:
            continue
        eventos.append({
            'clave': f'mov-{movimiento.id}',
            'empleado2_id': movimiento.empleado2_id,
            'nombre': _nombre_empleado2(movimiento.empleado2),
            'legajo': movimiento.empleado2.numero_legajo,
            'desde': movimiento.fecha_desde,
            'hasta': fecha_hasta_visual,
            'hasta_original': movimiento.fecha_hasta,
            'fecha_inconsistente': fecha_hasta_visual != movimiento.fecha_hasta,
            'dias': movimiento.dias,
            'estado': 'Histórica',
            'clase': 'historica',
            'detalle': movimiento.observaciones or movimiento.detalle,
        })

    # Incluye solicitudes de vacaciones creadas desde el portal.
    licencias = Licencia.query.filter(
        Licencia.fecha_desde <= fin_mes,
        Licencia.fecha_hasta >= fecha_mes,
    ).order_by(Licencia.fecha_desde).all()
    licencias = [item for item in licencias if _es_vacacion(item)]
    empleados_ids = {item.empleado_id for item in licencias if item.empleado_id}
    usuarios_por_empleado = {
        usuario.empleado_id: usuario
        for usuario in Usuario.query.filter(
            Usuario.empleado_id.in_(empleados_ids), Usuario.empleado2_id.isnot(None)
        ).all()
    } if empleados_ids else {}
    for licencia in licencias:
        usuario = usuarios_por_empleado.get(licencia.empleado_id)
        empleado2 = usuario.empleado2 if usuario else None
        if not empleado2:
            continue
        if not gestion and empleado2.id != empleado2_id:
            continue
        if gestion and busqueda:
            texto = f'{_nombre_empleado2(empleado2)} {empleado2.numero_legajo or ""}'.lower()
            if busqueda.lower() not in texto:
                continue
        clase = {
            'Aprobada': 'aprobada', 'Rechazada': 'rechazada', 'Pendiente': 'pendiente'
        }.get(licencia.estado, 'pendiente')
        eventos.append({
            'clave': f'lic-{licencia.id}',
            'empleado2_id': empleado2.id,
            'nombre': _nombre_empleado2(empleado2),
            'legajo': empleado2.numero_legajo,
            'desde': licencia.fecha_desde,
            'hasta': licencia.fecha_hasta,
            'dias': licencia.cantidad_dias,
            'estado': licencia.estado,
            'clase': clase,
            'detalle': licencia.motivo,
        })
    return eventos


def _armar_calendario(fecha_mes, eventos):
    hoy = date.today()
    semanas = []
    for semana in calendar.Calendar(firstweekday=0).monthdatescalendar(fecha_mes.year, fecha_mes.month):
        dias = []
        for dia in semana:
            eventos_dia = [evento for evento in eventos if evento['desde'] <= dia <= evento['hasta']]
            dias.append({
                'fecha': dia,
                'numero': dia.day,
                'del_mes': dia.month == fecha_mes.month,
                'es_hoy': dia == hoy,
                'eventos': eventos_dia,
            })
        semanas.append(dias)
    return semanas


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


@vacaciones_bp.route('/calendario')
@login_required
def calendario_vacaciones():
    fecha_mes = _mes_solicitado()
    roles_gestion = {'administrador', 'recursos_humanos', 'gerencia'}
    gestion = current_user.rol.nombre in roles_gestion
    empleado2_id = current_user.empleado2_id
    busqueda = request.args.get('q', '').strip() if gestion else ''
    eventos = _eventos_calendario(fecha_mes, gestion, empleado2_id, busqueda)

    if fecha_mes.month == 1:
        anterior = date(fecha_mes.year - 1, 12, 1)
    else:
        anterior = date(fecha_mes.year, fecha_mes.month - 1, 1)
    if fecha_mes.month == 12:
        siguiente = date(fecha_mes.year + 1, 1, 1)
    else:
        siguiente = date(fecha_mes.year, fecha_mes.month + 1, 1)

    meses = ('', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre')
    personas = {evento['empleado2_id'] for evento in eventos}
    return render_template(
        'vacaciones/calendario.html',
        gestion=gestion,
        busqueda=busqueda,
        fecha_mes=fecha_mes,
        nombre_mes=meses[fecha_mes.month],
        anterior=anterior,
        siguiente=siguiente,
        semanas=_armar_calendario(fecha_mes, eventos),
        eventos=eventos,
        cantidad_personas=len(personas),
    )
