import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from database.models import Licencia, TipoLicencia, Empleado
from .forms import LicenciaForm, ResolucionLicenciaForm

licencias_bp = Blueprint('licencias', __name__, url_prefix='/licencias')

def check_admin_or_rrhh():
    return current_user.rol.nombre in ['administrador', 'recursos_humanos']

@licencias_bp.route('/')
@login_required
def index():
    if check_admin_or_rrhh():
        # RRHH/Admin ven todas
        licencias = Licencia.query.order_by(Licencia.fecha_desde.desc()).all()
    else:
        # Empleado ve solo las suyas
        licencias = Licencia.query.filter_by(empleado_id=current_user.empleado_id).order_by(Licencia.fecha_desde.desc()).all()
    return render_template('licencias/index.html', licencias=licencias)

@licencias_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if not current_user.empleado_id and not check_admin_or_rrhh():
        flash('Tu usuario no está asociado a un empleado.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    form = LicenciaForm()
    form.tipo_licencia_id.choices = [(t.id, t.nombre) for t in TipoLicencia.query.filter_by(activo=True).all()]
    
    if form.validate_on_submit():
        archivo_nombre = None
        if form.archivo_adjunto.data:
            f = form.archivo_adjunto.data
            filename = secure_filename(f.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'licencias')
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
            f.save(file_path)
            archivo_nombre = file_path

        # Si RRHH carga, podría elegir a quién cargarle (por simplicidad aquí el usuario carga la suya)
        # Si queremos que RRHH le cargue a otros, necesitamos un selector de empleado en el form.
        # Asumiremos que el usuario carga SU licencia.
        emp_id = current_user.empleado_id
        if not emp_id and check_admin_or_rrhh():
            # Fallback para el admin initial: si admin no tiene empleado, tomamos el primero de prueba.
            emp = Empleado.query.first()
            if emp:
                emp_id = emp.id
            else:
                flash('No hay empleados creados en el sistema.', 'danger')
                return redirect(url_for('licencias.index'))

        licencia = Licencia(
            empleado_id=emp_id,
            tipo_licencia_id=form.tipo_licencia_id.data,
            fecha_desde=form.fecha_desde.data,
            fecha_hasta=form.fecha_hasta.data,
            cantidad_dias=form.cantidad_dias.data,
            motivo=form.motivo.data,
            archivo_adjunto=archivo_nombre,
            estado='Pendiente'
        )
        try:
            db.session.add(licencia)
            db.session.commit()
            flash('Solicitud de licencia enviada correctamente.', 'success')
            return redirect(url_for('licencias.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al solicitar licencia: {e}', 'danger')
            
    return render_template('licencias/form.html', form=form)

@licencias_bp.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def ver(id):
    licencia = Licencia.query.get_or_404(id)
    
    # Validar permisos
    if not check_admin_or_rrhh() and licencia.empleado_id != current_user.empleado_id:
        flash('No tienes permisos para ver esta licencia.', 'danger')
        return redirect(url_for('licencias.index'))
        
    form = ResolucionLicenciaForm()
    
    if request.method == 'POST' and check_admin_or_rrhh() and licencia.estado == 'Pendiente':
        if form.validate_on_submit():
            licencia.estado = form.estado.data
            licencia.observacion_rrhh = form.observacion_rrhh.data
            licencia.aprobado_por = current_user.id
            licencia.fecha_resolucion = datetime.utcnow()
            try:
                db.session.commit()
                flash(f'Licencia {form.estado.data.lower()} exitosamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error al actualizar licencia.', 'danger')
            return redirect(url_for('licencias.ver', id=licencia.id))
            
    return render_template('licencias/view.html', licencia=licencia, form=form, can_resolve=(check_admin_or_rrhh() and licencia.estado == 'Pendiente'))
