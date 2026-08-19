from collections import OrderedDict

from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from database.models import Empleado, Empresa, Sector

estructura_bp = Blueprint('estructura', __name__, url_prefix='/estructura')


@estructura_bp.route('/')
@login_required
def index():
    busqueda = request.args.get('q', '').strip()
    empresa_id = request.args.get('empresa_id', type=int)
    sector_id = request.args.get('sector_id', type=int)

    query = Empleado.query.options(
        joinedload(Empleado.empresa),
        joinedload(Empleado.sector),
        joinedload(Empleado.puesto),
        joinedload(Empleado.supervisor),
    ).filter(Empleado.estado == 'Activo')

    if busqueda:
        patron = f'%{busqueda}%'
        query = query.filter(or_(
            Empleado.nombre_apellido.ilike(patron),
            Empleado.legajo.ilike(patron),
            Empleado.dni.ilike(patron),
        ))
    if empresa_id:
        query = query.filter(Empleado.empresa_id == empresa_id)
    if sector_id:
        query = query.filter(Empleado.sector_id == sector_id)

    empleados = query.order_by(func.lower(Empleado.nombre_apellido)).all()

    grupos = {}
    for empleado in empleados:
        empresa_nombre = empleado.empresa.nombre if empleado.empresa else 'Sin empresa asignada'
        sector_nombre = empleado.sector.nombre if empleado.sector else 'Sin sector asignado'
        grupos.setdefault(empresa_nombre, {}).setdefault(sector_nombre, []).append(empleado)

    estructura = OrderedDict()
    for empresa_nombre in sorted(grupos, key=str.casefold):
        estructura[empresa_nombre] = OrderedDict(
            (sector, grupos[empresa_nombre][sector])
            for sector in sorted(grupos[empresa_nombre], key=str.casefold)
        )

    total_activos = Empleado.query.filter_by(estado='Activo').count()
    resumen = {
        'empleados': total_activos,
        'empresas': Empleado.query.filter(
            Empleado.estado == 'Activo', Empleado.empresa_id.isnot(None)
        ).with_entities(Empleado.empresa_id).distinct().count(),
        'sectores': Empleado.query.filter(
            Empleado.estado == 'Activo', Empleado.sector_id.isnot(None)
        ).with_entities(Empleado.sector_id).distinct().count(),
        'sin_puesto': Empleado.query.filter(
            Empleado.estado == 'Activo', Empleado.puesto_id.is_(None)
        ).count(),
        'sin_supervisor': Empleado.query.filter(
            Empleado.estado == 'Activo', Empleado.supervisor_id.is_(None)
        ).count(),
    }

    return render_template(
        'estructura/index.html', estructura=estructura, resumen=resumen,
        empresas=Empresa.query.filter_by(activo=True).order_by(Empresa.nombre).all(),
        sectores=Sector.query.filter_by(activo=True).order_by(Sector.nombre).all(),
        busqueda=busqueda, empresa_id=empresa_id, sector_id=sector_id,
        resultados=len(empleados),
    )
