from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func, or_
from extensions import db
from database.models import Empleado, Empresa, Sector, Puesto, Jornada
from .forms import EmpleadoForm

empleados_bp = Blueprint('empleados', __name__, url_prefix='/empleados')

# Función helper para verificar roles
def check_admin_or_rrhh():
    return current_user.rol.nombre in ['administrador', 'recursos_humanos']

@empleados_bp.route('/')
@login_required
def index():
    if not check_admin_or_rrhh():
        flash('No tienes permisos para ver el listado de empleados.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    busqueda = request.args.get('q', '').strip()
    query = Empleado.query
    if busqueda:
        patron = f'%{busqueda}%'
        query = query.filter(or_(
            Empleado.nombre_apellido.ilike(patron),
            Empleado.legajo.ilike(patron),
            Empleado.dni.ilike(patron),
            Empleado.cuil.ilike(patron),
        ))

    empleados = query.order_by(func.lower(Empleado.nombre_apellido), Empleado.nombre_apellido).all()
    return render_template(
        'empleados/index.html',
        empleados=empleados,
        busqueda=busqueda,
        total_empleados=Empleado.query.count(),
    )

def poblar_opciones_formulario(form):
    form.empresa_id.choices = [(0, '--- Seleccionar ---')] + [(e.id, e.nombre) for e in Empresa.query.filter_by(activo=True).order_by(Empresa.nombre).all()]
    form.sector_id.choices = [(0, '--- Seleccionar ---')] + [(s.id, s.nombre) for s in Sector.query.filter_by(activo=True).order_by(Sector.nombre).all()]
    form.puesto_id.choices = [(0, '--- Seleccionar ---')] + [(p.id, p.nombre) for p in Puesto.query.filter_by(activo=True).order_by(Puesto.nombre).all()]
    form.jornada_id.choices = [(0, '--- Seleccionar ---')] + [(j.id, j.nombre) for j in Jornada.query.filter_by(activo=True).order_by(Jornada.nombre).all()]
    form.supervisor_id.choices = [(0, '--- Ninguno ---')] + [(emp.id, emp.nombre_apellido) for emp in Empleado.query.filter_by(estado='Activo').order_by(Empleado.nombre_apellido).all()]

@empleados_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if not check_admin_or_rrhh():
        flash('No tienes permisos para crear empleados.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    form = EmpleadoForm()
    poblar_opciones_formulario(form)
    
    if form.validate_on_submit():
        empleado = Empleado(
            nombre_apellido=form.nombre_apellido.data,
            dni=form.dni.data,
            cuil=form.cuil.data if form.cuil.data else None,
            fecha_nacimiento=form.fecha_nacimiento.data,
            genero=form.genero.data,
            telefono=form.telefono.data,
            correo=form.correo.data if form.correo.data else None,
            domicilio=form.domicilio.data,
            provincia=form.provincia.data,
            codigo_postal=form.codigo_postal.data,
            licencia_conducir=form.licencia_conducir.data,
            
            legajo=form.legajo.data if form.legajo.data else None,
            empresa_id=form.empresa_id.data if form.empresa_id.data != 0 else None,
            sector_id=form.sector_id.data if form.sector_id.data != 0 else None,
            puesto_id=form.puesto_id.data if form.puesto_id.data != 0 else None,
            supervisor_id=form.supervisor_id.data if form.supervisor_id.data != 0 else None,
            jornada_id=form.jornada_id.data if form.jornada_id.data != 0 else None,
            fecha_ingreso=form.fecha_ingreso.data,
            estado=form.estado.data
        )
        try:
            db.session.add(empleado)
            db.session.commit()
            flash('Empleado creado exitosamente.', 'success')
            return redirect(url_for('empleados.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear empleado: Verifica que el DNI o Legajo no estén duplicados.', 'danger')
            
    return render_template('empleados/form.html', form=form, title='Nuevo Empleado')

@empleados_bp.route('/<int:id>')
@login_required
def ver(id):
    if not check_admin_or_rrhh() and current_user.empleado_id != id:
        flash('No tienes permisos para ver la ficha de este empleado.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    empleado = Empleado.query.get_or_404(id)
    return render_template('empleados/view.html', empleado=empleado)

@empleados_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not check_admin_or_rrhh():
        flash('No tienes permisos para editar empleados.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    empleado = Empleado.query.get_or_404(id)
    form = EmpleadoForm(obj=empleado)
    poblar_opciones_formulario(form)
    
    if request.method == 'GET':
        form.empresa_id.data = empleado.empresa_id or 0
        form.sector_id.data = empleado.sector_id or 0
        form.puesto_id.data = empleado.puesto_id or 0
        form.supervisor_id.data = empleado.supervisor_id or 0
        form.jornada_id.data = empleado.jornada_id or 0
        
    if form.validate_on_submit():
        form.populate_obj(empleado)
        
        # Convert empty strings to None for unique fields
        empleado.cuil = form.cuil.data if form.cuil.data else None
        empleado.legajo = form.legajo.data if form.legajo.data else None
        empleado.correo = form.correo.data if form.correo.data else None

        # Adjust foreign keys where '0' means None
        empleado.empresa_id = form.empresa_id.data if form.empresa_id.data != 0 else None
        empleado.sector_id = form.sector_id.data if form.sector_id.data != 0 else None
        empleado.puesto_id = form.puesto_id.data if form.puesto_id.data != 0 else None
        empleado.supervisor_id = form.supervisor_id.data if form.supervisor_id.data != 0 else None
        empleado.jornada_id = form.jornada_id.data if form.jornada_id.data != 0 else None
        
        try:
            db.session.commit()
            flash('Empleado actualizado exitosamente.', 'success')
            return redirect(url_for('empleados.ver', id=empleado.id))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar empleado: Verifica campos únicos.', 'danger')
            
    return render_template('empleados/form.html', form=form, title='Editar Empleado')
