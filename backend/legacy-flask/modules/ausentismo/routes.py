from datetime import date, datetime

from flask import Blueprint, abort, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from database.models import Ausencia, Empleado2, TipoAusencia


ausentismo_bp = Blueprint('ausentismo', __name__, url_prefix='/ausentismo')
ROLES_AUTORIZADOS = {'recursos_humanos', 'gerencia', 'administrador'}


def _exigir_acceso():
    if not current_user.rol or current_user.rol.nombre not in ROLES_AUTORIZADOS:
        abort(403)


def _fecha_arg(nombre, predeterminada=None):
    valor = request.args.get(nombre, '').strip()
    if not valor:
        return predeterminada
    try:
        return datetime.strptime(valor, '%Y-%m-%d').date()
    except ValueError:
        return predeterminada


@ausentismo_bp.route('/')
@login_required
def index():
    _exigir_acceso()
    hoy = date.today()
    desde = _fecha_arg('desde', date(hoy.year, 1, 1))
    hasta = _fecha_arg('hasta', date(hoy.year, 12, 31))
    if hasta < desde:
        desde, hasta = hasta, desde
    q = request.args.get('q', '').strip()
    tipo = request.args.get('tipo', type=int)
    planta = request.args.get('planta', '').strip()

    consulta = Ausencia.query.outerjoin(Empleado2).join(TipoAusencia).filter(
        Ausencia.fecha_inicio <= hasta,
        Ausencia.fecha_fin >= desde,
    )
    if q:
        patron = f'%{q}%'
        consulta = consulta.filter(or_(
            Empleado2.nombre_completo.ilike(patron),
            Empleado2.nombre.ilike(patron),
            Empleado2.apellido.ilike(patron),
            Empleado2.numero_legajo.ilike(patron),
            Ausencia.nombre_origen.ilike(patron),
        ))
    if tipo:
        consulta = consulta.filter(Ausencia.tipo_codigo == tipo)
    if planta:
        consulta = consulta.filter(Ausencia.planta_origen == planta)

    total_registros = consulta.count()
    total_personas = consulta.with_entities(func.count(func.distinct(Ausencia.legajo_origen))).scalar() or 0
    total_dias = consulta.with_entities(func.coalesce(func.sum(Ausencia.dias_calendario), 0)).scalar() or 0
    pagina = request.args.get('page', 1, type=int)
    paginacion = consulta.order_by(Ausencia.fecha_inicio.desc(), Ausencia.id.desc()).paginate(
        page=max(pagina, 1), per_page=30, error_out=False
    )
    tipos = TipoAusencia.query.order_by(TipoAusencia.descripcion).all()
    plantas = [fila[0] for fila in (
        Ausencia.query.with_entities(Ausencia.planta_origen).filter(
            Ausencia.planta_origen.isnot(None), Ausencia.planta_origen != ''
        ).distinct().order_by(Ausencia.planta_origen).all()
    )]
    return render_template(
        'ausentismo/index.html', ausencias=paginacion.items, paginacion=paginacion,
        tipos=tipos, plantas=plantas, q=q, tipo=tipo, planta=planta,
        desde=desde, hasta=hasta, total_registros=total_registros,
        total_personas=total_personas, total_dias=total_dias,
    )
