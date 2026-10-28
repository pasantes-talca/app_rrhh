import calendar
from datetime import date, datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import extract, or_

from database.models import (
    DocumentoRRHH,
    Empleado,
    Feriado,
    HorasExtra,
    Licencia,
    Noticia,
    Notificacion,
    ReciboSueldo,
    SancionDisciplinaria,
    TareaChecklist,
    Usuario,
)
from extensions import db
from modules.notificaciones.services import es_cumpleanos_hoy

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def nombre_visible():
    if current_user.empleado and current_user.empleado.nombre_apellido:
        return current_user.empleado.nombre_apellido.split()[0].title()
    return current_user.usuario


def obtener_proximos_cumpleanos(hoy_fecha=None, limite_dias=30):
    hoy_fecha = hoy_fecha or date.today()
    proximos_cumpleanos = []
    empleados_con_fecha = Empleado.query.filter(
        Empleado.estado == 'Activo',
        Empleado.fecha_nacimiento.isnot(None),
    ).all()
    for empleado in empleados_con_fecha:
        try:
            proximo = empleado.fecha_nacimiento.replace(year=hoy_fecha.year)
        except ValueError:
            proximo = date(hoy_fecha.year, 2, 28)
        if proximo < hoy_fecha:
            try:
                proximo = empleado.fecha_nacimiento.replace(year=hoy_fecha.year + 1)
            except ValueError:
                proximo = date(hoy_fecha.year + 1, 2, 28)
        dias = (proximo - hoy_fecha).days
        if dias <= limite_dias:
            proximos_cumpleanos.append({
                'empleado': empleado,
                'fecha': proximo,
                'dias': dias,
                'edad': proximo.year - empleado.fecha_nacimiento.year,
            })
    proximos_cumpleanos.sort(key=lambda item: (item['dias'], item['empleado'].nombre_apellido))
    return proximos_cumpleanos


def obtener_calendario_dashboard():
    hoy = date.today()
    try:
        anio = int(request.args.get('anio', hoy.year))
        mes = int(request.args.get('mes', hoy.month))
        fecha_mes = date(anio, mes, 1)
    except (TypeError, ValueError):
        fecha_mes = date(hoy.year, hoy.month, 1)
    anterior = (fecha_mes - timedelta(days=1)).replace(day=1)
    if fecha_mes.month == 12:
        siguiente = date(fecha_mes.year + 1, 1, 1)
    else:
        siguiente = date(fecha_mes.year, fecha_mes.month + 1, 1)

    cumpleanos_por_dia = {}
    empleados = Empleado.query.filter(
        Empleado.estado == 'Activo', Empleado.fecha_nacimiento.isnot(None)
    ).all()
    for empleado in empleados:
        if empleado.fecha_nacimiento.month == fecha_mes.month:
            cumpleanos_por_dia.setdefault(empleado.fecha_nacimiento.day, []).append(
                empleado.nombre_apellido
            )
    feriados_por_dia = {
        feriado.fecha.day: feriado.descripcion
        for feriado in Feriado.query.filter(
            extract('year', Feriado.fecha) == fecha_mes.year,
            extract('month', Feriado.fecha) == fecha_mes.month,
        ).all()
    }
    noticias_por_dia = {}
    noticias_query = Noticia.query.filter(
        Noticia.estado == 'Publicada', Noticia.es_fecha_importante.is_(True),
        Noticia.fecha_importante.isnot(None),
        extract('year', Noticia.fecha_importante) == fecha_mes.year,
        extract('month', Noticia.fecha_importante) == fecha_mes.month,
    )
    if current_user.rol.nombre == 'empleado':
        if current_user.empleado:
            noticias_query = noticias_query.filter(or_(
                Noticia.visible_todos.is_(True),
                Noticia.empresa_id == current_user.empleado.empresa_id,
                Noticia.sector_id == current_user.empleado.sector_id,
            ))
        else:
            noticias_query = noticias_query.filter(Noticia.visible_todos.is_(True))
    for noticia in noticias_query.all():
        noticias_por_dia.setdefault(noticia.fecha_importante.day, []).append(noticia)
    semanas = []
    for semana in calendar.Calendar(firstweekday=0).monthdayscalendar(fecha_mes.year, fecha_mes.month):
        semanas.append([{
            'numero': dia,
            'cumpleanos': cumpleanos_por_dia.get(dia, []),
            'feriado': feriados_por_dia.get(dia),
            'noticias': noticias_por_dia.get(dia, []),
            'es_hoy': bool(dia and date(fecha_mes.year, fecha_mes.month, dia) == hoy),
        } if dia else None for dia in semana])
    return {
        'mes': fecha_mes.month, 'anio': fecha_mes.year,
        'nombre_mes': ('', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre')[fecha_mes.month],
        'semanas': semanas,
        'anterior': anterior, 'siguiente': siguiente,
    }


def obtener_proximas_fechas_importantes(limite_dias=120):
    hoy = date.today()
    hasta = hoy + timedelta(days=limite_dias)
    eventos = [{
        'fecha': item.fecha, 'titulo': item.descripcion, 'tipo': 'feriado', 'noticia': None,
        'dias': (item.fecha - hoy).days,
    } for item in Feriado.query.filter(Feriado.fecha.between(hoy, hasta)).all()]
    query = Noticia.query.filter(
        Noticia.estado == 'Publicada', Noticia.es_fecha_importante.is_(True),
        Noticia.fecha_importante.between(hoy, hasta),
    )
    if current_user.rol.nombre == 'empleado':
        if current_user.empleado:
            query = query.filter(or_(
                Noticia.visible_todos.is_(True),
                Noticia.empresa_id == current_user.empleado.empresa_id,
                Noticia.sector_id == current_user.empleado.sector_id,
            ))
        else:
            query = query.filter(Noticia.visible_todos.is_(True))
    eventos.extend({
        'fecha': noticia.fecha_importante, 'titulo': noticia.titulo,
        'tipo': 'noticia', 'noticia': noticia,
        'dias': (noticia.fecha_importante - hoy).days,
    } for noticia in query.all())
    return sorted(eventos, key=lambda item: (item['fecha'], item['tipo']))[:5]


def obtener_sanciones_activas(query, limite=None):
    """Excluye del dashboard las sanciones cuyo período ya finalizó."""
    hoy = date.today()
    query = query.filter(or_(
        SancionDisciplinaria.fecha_hasta.is_(None),
        SancionDisciplinaria.fecha_hasta >= hoy,
    )).order_by(
        SancionDisciplinaria.fecha_hasta.asc().nullslast(),
        SancionDisciplinaria.notificado_en.desc(),
    )
    if limite:
        query = query.limit(limite)
    sanciones = query.all()
    for sancion in sanciones:
        sancion.dias_restantes = (
            max((sancion.fecha_hasta - hoy).days, 0) if sancion.fecha_hasta else None
        )
    return sanciones


def dashboard_gestion(template):
    hoy_fecha = date.today()
    limite_anuncios = datetime.utcnow() - timedelta(days=7)
    proximos_cumpleanos = obtener_proximos_cumpleanos(hoy_fecha)

    documentos_empleados = (
        DocumentoRRHH.query
        .join(Usuario, DocumentoRRHH.cargado_por == Usuario.id)
        .join(Usuario.rol)
        .filter(DocumentoRRHH.estado == 'Activo')
        .filter_by(nombre='empleado')
    )
    datos = {
        'nombre': nombre_visible(),
        'hoy': datetime.now(),
        'empleados_activos': Empleado.query.filter_by(estado='Activo').count(),
        'licencias_pendientes': Licencia.query.filter_by(estado='Pendiente').count(),
        'horas_pendientes': HorasExtra.query.filter_by(estado='Pendiente').count(),
        'documentos_recibidos': documentos_empleados.count(),
        'ultimas_licencias': Licencia.query.filter_by(estado='Pendiente').order_by(Licencia.creado_en.desc()).limit(5).all(),
        'ultimas_horas': HorasExtra.query.filter_by(estado='Pendiente').order_by(
            HorasExtra.creado_en.desc()
        ).limit(5).all(),
        'ultimos_documentos': documentos_empleados.order_by(DocumentoRRHH.creado_en.desc()).limit(5).all(),
        'proximos_cumpleanos': proximos_cumpleanos,
        'empleados_sin_nacimiento': Empleado.query.filter(
            Empleado.estado == 'Activo',
            Empleado.fecha_nacimiento.is_(None),
        ).count(),
        'novedades_recientes': Noticia.query.filter_by(estado='Publicada').filter(
            Noticia.fecha_publicacion >= limite_anuncios
        ).order_by(
            Noticia.fecha_publicacion.desc()
        ).limit(5).all(),
        'tareas_checklist': TareaChecklist.query.filter_by(usuario_id=current_user.id).order_by(
            TareaChecklist.completada.asc(), TareaChecklist.creado_en.desc()
        ).all(),
        'fechas_importantes_hoy': Feriado.query.filter_by(fecha=hoy_fecha).all(),
        'calendario_dashboard': obtener_calendario_dashboard(),
        'proximas_fechas_importantes': obtener_proximas_fechas_importantes(),
        'sanciones_activas': obtener_sanciones_activas(
            SancionDisciplinaria.query.filter_by(estado='Notificada'), limite=5
        ),
        'recibos_pendientes': ReciboSueldo.query.filter_by(estado='Pendiente').count(),
    }
    return render_template(template, **datos)


def dashboard_empleado():
    empleado = current_user.empleado
    if not empleado:
        return render_template(
            'dashboard_empleado.html', nombre=nombre_visible(), hoy=datetime.now(),
            documentos_disponibles=0, licencias_pendientes=0,
            mis_licencias=[], ultimos_documentos=[], noticias=[],
            medidas_disciplinarias=[], es_cumpleanos=False,
            fechas_importantes_hoy=Feriado.query.filter_by(fecha=date.today()).all(),
            proximos_cumpleanos=obtener_proximos_cumpleanos(),
            tareas_checklist=TareaChecklist.query.filter_by(usuario_id=current_user.id).order_by(
                TareaChecklist.completada.asc(), TareaChecklist.creado_en.desc()).all(),
            calendario_dashboard=obtener_calendario_dashboard(),
            proximas_fechas_importantes=obtener_proximas_fechas_importantes(),
            recibos_pendientes_empleado=0,
        )

    limite_anuncios = datetime.utcnow() - timedelta(days=7)
    noticias_query = Noticia.query.filter_by(estado='Publicada').filter(
        Noticia.fecha_publicacion >= limite_anuncios
    ).filter(or_(
        Noticia.visible_todos.is_(True),
        Noticia.empresa_id == empleado.empresa_id,
        Noticia.sector_id == empleado.sector_id,
    ))
    sanciones_notificadas = db.session.query(Notificacion.referencia_id).filter(
        Notificacion.usuario_id == current_user.id,
        Notificacion.referencia_tipo == 'sancion',
    )
    return render_template(
        'dashboard_empleado.html',
        nombre=nombre_visible(),
        hoy=datetime.now(),
        es_cumpleanos=es_cumpleanos_hoy(empleado.fecha_nacimiento),
        fechas_importantes_hoy=Feriado.query.filter_by(fecha=date.today()).all(),
        proximos_cumpleanos=obtener_proximos_cumpleanos(),
        tareas_checklist=TareaChecklist.query.filter_by(usuario_id=current_user.id).order_by(
            TareaChecklist.completada.asc(), TareaChecklist.creado_en.desc()).all(),
        calendario_dashboard=obtener_calendario_dashboard(),
        proximas_fechas_importantes=obtener_proximas_fechas_importantes(),
        recibos_pendientes_empleado=ReciboSueldo.query.filter_by(
            empleado_id=empleado.id, estado='Pendiente'
        ).count(),
        documentos_disponibles=DocumentoRRHH.query.filter_by(
            empleado_id=empleado.id, visible_empleado=True, estado='Activo'
        ).count(),
        licencias_pendientes=Licencia.query.filter_by(
            empleado_id=empleado.id, estado='Pendiente'
        ).count(),
        medidas_disciplinarias=obtener_sanciones_activas(
            SancionDisciplinaria.query.filter_by(estado='Notificada').filter(or_(
                SancionDisciplinaria.empleado_id == empleado.id,
                SancionDisciplinaria.id.in_(sanciones_notificadas),
            )), limite=3
        ),
        mis_licencias=Licencia.query.filter_by(empleado_id=empleado.id).order_by(
            Licencia.creado_en.desc()
        ).limit(4).all(),
        ultimos_documentos=DocumentoRRHH.query.filter_by(
            empleado_id=empleado.id, visible_empleado=True, estado='Activo'
        ).order_by(DocumentoRRHH.creado_en.desc()).limit(4).all(),
        noticias=noticias_query.order_by(Noticia.fecha_publicacion.desc()).limit(2).all(),
    )


@dashboard_bp.route('/')
@login_required
def index():
    if current_user.rol.nombre == 'administrador':
        return dashboard_gestion('dashboard_admin.html')
    if current_user.rol.nombre == 'recursos_humanos':
        return dashboard_gestion('dashboard_rrhh.html')
    return dashboard_empleado()


def exigir_usuario_gestion():
    if current_user.rol.nombre not in ['administrador', 'recursos_humanos']:
        abort(403)


@dashboard_bp.route('/checklist/nueva', methods=['POST'])
@login_required
def checklist_nueva():
    descripcion = request.form.get('descripcion', '').strip()
    if not descripcion:
        flash('Escribí una tarea antes de agregarla.', 'warning')
    elif len(descripcion) > 250:
        flash('La tarea no puede superar los 250 caracteres.', 'warning')
    else:
        db.session.add(TareaChecklist(usuario_id=current_user.id, descripcion=descripcion))
        db.session.commit()
    return redirect(url_for('dashboard.index') + '#mi-checklist')


@dashboard_bp.route('/checklist/<int:id>/alternar', methods=['POST'])
@login_required
def checklist_alternar(id):
    tarea = TareaChecklist.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
    tarea.completada = not tarea.completada
    tarea.completado_en = datetime.utcnow() if tarea.completada else None
    db.session.commit()
    return redirect(url_for('dashboard.index') + '#mi-checklist')


@dashboard_bp.route('/checklist/<int:id>/eliminar', methods=['POST'])
@login_required
def checklist_eliminar(id):
    tarea = TareaChecklist.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
    db.session.delete(tarea)
    db.session.commit()
    return redirect(url_for('dashboard.index') + '#mi-checklist')
