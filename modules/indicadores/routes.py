from datetime import date

from flask import Blueprint, abort, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import extract, func

from database.models import Ausencia, AusentismoEmpleado
from .services import MESES, resumen_ausentismo, resumen_tendencia, resumen_vacaciones


indicadores_bp = Blueprint('indicadores', __name__, url_prefix='/indicadores')
ROLES_AUTORIZADOS = {'gerencia', 'administrador'}


def exigir_acceso():
    if not current_user.rol or current_user.rol.nombre not in ROLES_AUTORIZADOS:
        abort(403)


def filtros():
    disponibles = [int(fila[0]) for fila in Ausencia.query.with_entities(
        extract('year', Ausencia.fecha_inicio)
    ).distinct().order_by(extract('year', Ausencia.fecha_inicio).desc()).all() if fila[0]]
    predeterminado = disponibles[0] if disponibles else date.today().year
    anio = request.args.get('anio', predeterminado, type=int)
    if anio not in disponibles and disponibles:
        anio = predeterminado
    mes = request.args.get('mes', 0, type=int)
    if mes not in range(13):
        mes = 0
    planta = request.args.get('planta', '').strip()
    plantas = [fila[0] for fila in AusentismoEmpleado.query.with_entities(
        AusentismoEmpleado.planta
    ).filter(AusentismoEmpleado.planta.isnot(None), AusentismoEmpleado.planta != '')
     .distinct().order_by(AusentismoEmpleado.planta).all()]
    return anio, mes, planta, disponibles, plantas


@indicadores_bp.route('/')
@login_required
def index():
    exigir_acceso()
    return render_template('indicadores/index.html')


@indicadores_bp.route('/ausentismo')
@login_required
def ausentismo():
    exigir_acceso()
    anio, mes, planta, anios, plantas = filtros()
    vista = request.args.get('vista', 'ausentismo')
    if vista not in ('ausentismo', 'tendencia', 'vacaciones'):
        vista = 'ausentismo'
    resumen = resumen_ausentismo(anio, mes, planta) if vista == 'ausentismo' else None
    tendencia = resumen_tendencia(anio, planta) if vista == 'tendencia' else None
    vacaciones = resumen_vacaciones(anio, mes, planta) if vista == 'vacaciones' else None
    return render_template('indicadores/ausentismo.html', vista=vista, anio=anio, mes=mes,
                           planta=planta, anios=anios, meses=MESES, plantas=plantas,
                           resumen=resumen, tendencia=tendencia, vacaciones=vacaciones)
