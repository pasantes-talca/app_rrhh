import os
from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from database.models import Empleado, EmpleadoSupervisor, Licencia, TipoLicencia, Usuario
from extensions import db
from modules.notificaciones.services import notificar_empleado, notificar_rrhh, notificar_usuario
from .forms import LicenciaForm, ResolucionLicenciaForm

licencias_bp = Blueprint('licencias', __name__, url_prefix='/licencias')

def check_admin_or_rrhh():
    return current_user.rol.nombre in ['administrador', 'recursos_humanos']

def es_vacacion(tipo):
    return bool(tipo and 'vacacion' in tipo.nombre.lower().replace('ó', 'o'))

def empleados2_supervisados():
    if not current_user.empleado2_id:
        return set()
    return {r.empleado2_id for r in EmpleadoSupervisor.query.filter_by(
        supervisor_empleado2_id=current_user.empleado2_id, activo=True).all()}

def usuario_solicitante(licencia):
    return Usuario.query.filter_by(empleado_id=licencia.empleado_id, activo=True).first()

def puede_supervisar(licencia):
    solicitante = usuario_solicitante(licencia)
    return bool(solicitante and solicitante.empleado2_id in empleados2_supervisados())

@licencias_bp.route('/')
@login_required
def index():
    supervisados = empleados2_supervisados()
    if check_admin_or_rrhh():
        licencias = Licencia.query.order_by(Licencia.fecha_desde.desc()).all()
    else:
        empleados_ids = [u.empleado_id for u in Usuario.query.filter(
            Usuario.empleado2_id.in_(supervisados), Usuario.empleado_id.isnot(None)
        ).all()] if supervisados else []
        licencias = Licencia.query.filter(or_(
            Licencia.empleado_id == current_user.empleado_id,
            Licencia.empleado_id.in_(empleados_ids),
        )).order_by(Licencia.fecha_desde.desc()).all()
    return render_template('licencias/index.html', licencias=licencias, supervisados=supervisados)

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
            archivo = form.archivo_adjunto.data
            nombre = secure_filename(archivo.filename)
            carpeta = os.path.join(current_app.config['UPLOAD_FOLDER'], 'licencias')
            os.makedirs(carpeta, exist_ok=True)
            archivo_nombre = os.path.join(carpeta, f"{datetime.now():%Y%m%d%H%M%S}_{nombre}")
            archivo.save(archivo_nombre)
        emp_id = current_user.empleado_id
        if not emp_id and check_admin_or_rrhh():
            empleado = Empleado.query.first()
            if not empleado:
                flash('No hay empleados creados en el sistema.', 'danger')
                return redirect(url_for('licencias.index'))
            emp_id = empleado.id
        tipo = db.session.get(TipoLicencia, form.tipo_licencia_id.data)
        vacaciones = es_vacacion(tipo)
        relaciones = EmpleadoSupervisor.query.filter_by(
            empleado2_id=current_user.empleado2_id, activo=True
        ).all() if vacaciones and current_user.empleado2_id else []
        licencia = Licencia(
            empleado_id=emp_id, tipo_licencia_id=form.tipo_licencia_id.data,
            fecha_desde=form.fecha_desde.data, fecha_hasta=form.fecha_hasta.data,
            cantidad_dias=form.cantidad_dias.data, motivo=form.motivo.data,
            archivo_adjunto=archivo_nombre, estado='Pendiente',
            estado_supervisor='Pendiente' if vacaciones and relaciones else ('Sin asignar' if vacaciones else 'No requerido'),
        )
        try:
            db.session.add(licencia); db.session.flush()
            nombre_empleado = licencia.empleado.nombre_apellido if licencia.empleado else 'Un empleado'
            mensaje = f'{nombre_empleado} solicitó vacaciones del {licencia.fecha_desde:%d/%m/%Y} al {licencia.fecha_hasta:%d/%m/%Y}.'
            if vacaciones and relaciones:
                ids = {r.supervisor_empleado2_id for r in relaciones}
                for usuario in Usuario.query.filter(Usuario.empleado2_id.in_(ids), Usuario.activo.is_(True)).all():
                    notificar_usuario(usuario.id, 'Vacaciones pendientes de tu aprobación', mensaje,
                                      'licencia', 'licencia_supervisor', licencia.id)
            elif vacaciones:
                notificar_rrhh('Solicitud de vacaciones sin supervisor asignado', mensaje,
                               'licencia', 'licencia_sin_supervisor', licencia.id)
            else:
                notificar_rrhh('Nueva solicitud de licencia', mensaje, 'licencia',
                               'licencia_rrhh', licencia.id, excluir_usuario_id=current_user.id)
            db.session.commit()
            flash('Solicitud enviada a tu supervisor.' if vacaciones and relaciones else 'Solicitud enviada correctamente.', 'success')
            return redirect(url_for('licencias.index'))
        except Exception as exc:
            db.session.rollback(); flash(f'Error al solicitar licencia: {exc}', 'danger')
    return render_template('licencias/form.html', form=form)

@licencias_bp.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def ver(id):
    licencia = Licencia.query.get_or_404(id)
    supervisor_autorizado = puede_supervisar(licencia)
    if not check_admin_or_rrhh() and licencia.empleado_id != current_user.empleado_id and not supervisor_autorizado:
        flash('No tenés permisos para ver esta licencia.', 'danger')
        return redirect(url_for('licencias.index'))
    form = ResolucionLicenciaForm()
    puede_rrhh = check_admin_or_rrhh() and licencia.estado == 'Pendiente' and licencia.estado_supervisor in ('Aprobada', 'No requerido')
    if request.method == 'POST' and puede_rrhh and form.validate_on_submit():
        licencia.estado = form.estado.data
        licencia.observacion_rrhh = form.observacion_rrhh.data
        licencia.aprobado_por = current_user.id
        licencia.fecha_resolucion = datetime.utcnow()
        try:
            notificar_empleado(licencia.empleado_id, f'Licencia {licencia.estado.lower()}',
                f'Tu solicitud del {licencia.fecha_desde:%d/%m/%Y} al {licencia.fecha_hasta:%d/%m/%Y} fue {licencia.estado.lower()} por RR. HH.',
                'licencia', 'licencia', licencia.id)
            db.session.commit(); flash(f'Licencia {licencia.estado.lower()} exitosamente.', 'success')
        except Exception:
            db.session.rollback(); flash('Error al actualizar licencia.', 'danger')
        return redirect(url_for('licencias.ver', id=id))
    return render_template('licencias/view.html', licencia=licencia, form=form,
                           can_resolve=puede_rrhh,
                           can_supervise=(supervisor_autorizado and licencia.estado == 'Pendiente' and licencia.estado_supervisor == 'Pendiente'))

@licencias_bp.route('/<int:id>/resolver-supervisor', methods=['POST'])
@login_required
def resolver_supervisor(id):
    licencia = Licencia.query.get_or_404(id)
    if not puede_supervisar(licencia) or licencia.estado != 'Pendiente' or licencia.estado_supervisor != 'Pendiente':
        flash('La solicitud no está disponible para tu aprobación.', 'danger')
        return redirect(url_for('licencias.index'))
    accion = request.form.get('accion')
    if accion not in ('Aprobada', 'Rechazada'):
        flash('Resolución inválida.', 'danger')
        return redirect(url_for('licencias.ver', id=id))
    licencia.estado_supervisor = accion
    licencia.supervisor_resuelto_por = current_user.id
    licencia.fecha_resolucion_supervisor = datetime.utcnow()
    licencia.observacion_supervisor = request.form.get('observacion', '').strip() or None
    if accion == 'Aprobada':
        notificar_rrhh('Vacaciones aprobadas por supervisión',
            f'{licencia.empleado.nombre_apellido} tiene una solicitud aprobada por {current_user.nombre_mostrar or current_user.usuario}, pendiente de resolución final.',
            'licencia', 'licencia_rrhh', licencia.id)
        mensaje = 'Tu supervisor aprobó la solicitud. Ahora será revisada por RR. HH.'
    else:
        licencia.estado = 'Rechazada'; licencia.fecha_resolucion = datetime.utcnow()
        mensaje = 'Tu solicitud de vacaciones fue rechazada por supervisión.'
    notificar_empleado(licencia.empleado_id, 'Actualización de vacaciones', mensaje,
                       'licencia', 'licencia_supervisor_resultado', licencia.id)
    db.session.commit()
    flash('La solicitud fue aprobada y enviada a RR. HH.' if accion == 'Aprobada' else 'La solicitud fue rechazada.', 'success')
    return redirect(url_for('licencias.ver', id=id))
