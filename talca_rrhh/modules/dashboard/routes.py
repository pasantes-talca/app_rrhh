from datetime import date, datetime

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_

from database.models import (
    DocumentoRRHH,
    Empleado,
    HorasExtra,
    Licencia,
    Noticia,
    Usuario,
)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def nombre_visible():
    if current_user.empleado and current_user.empleado.nombre_apellido:
        return current_user.empleado.nombre_apellido.split()[0].title()
    return current_user.usuario


def dashboard_gestion(template):
    hoy_fecha = date.today()
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
        if dias <= 30:
            proximos_cumpleanos.append({
                'empleado': empleado,
                'fecha': proximo,
                'dias': dias,
                'edad': proximo.year - empleado.fecha_nacimiento.year,
            })
    proximos_cumpleanos.sort(key=lambda item: (item['dias'], item['empleado'].nombre_apellido))

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
        'ultimos_documentos': documentos_empleados.order_by(DocumentoRRHH.creado_en.desc()).limit(5).all(),
        'proximos_cumpleanos': proximos_cumpleanos,
        'empleados_sin_nacimiento': Empleado.query.filter(
            Empleado.estado == 'Activo',
            Empleado.fecha_nacimiento.is_(None),
        ).count(),
        'novedades_recientes': Noticia.query.filter_by(estado='Publicada').order_by(
            Noticia.fecha_publicacion.desc()
        ).limit(5).all(),
    }
    return render_template(template, **datos)


def dashboard_empleado():
    empleado = current_user.empleado
    if not empleado:
        return render_template(
            'dashboard_empleado.html', nombre=nombre_visible(), hoy=datetime.now(),
            documentos_disponibles=0, licencias_pendientes=0,
            mis_licencias=[], ultimos_documentos=[], noticias=[]
        )

    noticias_query = Noticia.query.filter_by(estado='Publicada').filter(or_(
        Noticia.visible_todos.is_(True),
        Noticia.empresa_id == empleado.empresa_id,
        Noticia.sector_id == empleado.sector_id,
    ))
    return render_template(
        'dashboard_empleado.html',
        nombre=nombre_visible(),
        hoy=datetime.now(),
        documentos_disponibles=DocumentoRRHH.query.filter_by(
            empleado_id=empleado.id, visible_empleado=True, estado='Activo'
        ).count(),
        licencias_pendientes=Licencia.query.filter_by(
            empleado_id=empleado.id, estado='Pendiente'
        ).count(),
        mis_licencias=Licencia.query.filter_by(empleado_id=empleado.id).order_by(
            Licencia.creado_en.desc()
        ).limit(4).all(),
        ultimos_documentos=DocumentoRRHH.query.filter_by(
            empleado_id=empleado.id, visible_empleado=True, estado='Activo'
        ).order_by(DocumentoRRHH.creado_en.desc()).limit(4).all(),
        noticias=noticias_query.order_by(Noticia.fecha_publicacion.desc()).limit(3).all(),
    )


@dashboard_bp.route('/')
@login_required
def index():
    if current_user.rol.nombre == 'administrador':
        return dashboard_gestion('dashboard_admin.html')
    if current_user.rol.nombre == 'recursos_humanos':
        return dashboard_gestion('dashboard_rrhh.html')
    return dashboard_empleado()
