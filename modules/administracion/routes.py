import csv
import io
import platform
import time
from datetime import datetime, timedelta

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required
from sqlalchemy import func, text
from werkzeug.security import generate_password_hash

from extensions import db
from database.models import (Auditoria, ConfiguracionSistema, Empleado, ErrorSistema,
    PermisoUsuario, Rol, SesionUsuario, Usuario)
from .forms import PasswordAdminForm, RevisionErrorForm, SeguridadForm, UsuarioAdminForm
from .security import ACCIONES, MODULOS, solo_administrador

administracion_bp = Blueprint('administracion', __name__, url_prefix='/administracion')


def _config(clave, defecto):
    item = ConfiguracionSistema.query.get(clave)
    return item.valor if item else str(defecto)


def _opciones_usuario(form):
    form.empleado_id.choices = [(0, 'Sin empleado asociado')] + [(e.id, f'{e.nombre_apellido} · {e.legajo or "sin legajo"}') for e in Empleado.query.order_by(Empleado.nombre_apellido).all()]
    form.rol_id.choices = [(r.id, r.nombre.replace('_', ' ').title()) for r in Rol.query.filter(Rol.nombre.in_(['empleado', 'recursos_humanos'])).order_by(Rol.nombre).all()]


def _editable(usuario):
    return usuario.id != current_user.id and not usuario.cuenta_protegida and (not usuario.rol or usuario.rol.nombre != 'administrador')


@administracion_bp.route('/')
@login_required
@solo_administrador
def index():
    desde = datetime.utcnow() - timedelta(days=30)
    resumen_modulos = db.session.query(Auditoria.modulo, func.count(Auditoria.id)).filter(Auditoria.creado_en >= desde).group_by(Auditoria.modulo).order_by(func.count(Auditoria.id).desc()).limit(8).all()
    return render_template('administracion/index.html',
        usuarios=Usuario.query.count(), activos=Usuario.query.filter_by(activo=True).count(),
        operaciones=Auditoria.query.filter(Auditoria.creado_en >= desde).count(),
        errores=ErrorSistema.query.filter_by(revisado=False).count(),
        sesiones=SesionUsuario.query.filter_by(cerrada_en=None).count(),
        actividad=Auditoria.query.order_by(Auditoria.creado_en.desc()).limit(10).all(),
        resumen_modulos=resumen_modulos)


@administracion_bp.route('/usuarios')
@login_required
@solo_administrador
def usuarios():
    q = request.args.get('q', '').strip()
    consulta = Usuario.query
    if q:
        consulta = consulta.filter(db.or_(Usuario.usuario.ilike(f'%{q}%'), Usuario.nombre_mostrar.ilike(f'%{q}%'), Usuario.correo.ilike(f'%{q}%')))
    return render_template('administracion/usuarios.html', usuarios=consulta.order_by(Usuario.usuario).all(), q=q)


@administracion_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@solo_administrador
def usuario_nuevo():
    form = UsuarioAdminForm()
    _opciones_usuario(form)
    minimo = int(_config('password_min_length', 8))
    if form.validate_on_submit():
        if not form.password.data or len(form.password.data) < minimo:
            form.password.errors.append(f'La contraseña debe tener al menos {minimo} caracteres.')
        elif Usuario.query.filter_by(usuario=form.usuario.data.strip()).first():
            form.usuario.errors.append('Ese nombre de usuario ya existe.')
        else:
            usuario = Usuario(usuario=form.usuario.data.strip(), nombre_mostrar=form.nombre_mostrar.data.strip(),
                correo=(form.correo.data or '').strip() or None, empleado_id=form.empleado_id.data or None,
                rol_id=form.rol_id.data, password_hash=generate_password_hash(form.password.data), activo=form.activo.data,
                cuenta_protegida=False)
            db.session.add(usuario); db.session.commit()
            flash('Usuario creado correctamente.', 'success')
            return redirect(url_for('administracion.usuarios'))
    return render_template('administracion/usuario_form.html', form=form, titulo='Crear usuario', minimo=minimo, edicion=False)


@administracion_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@solo_administrador
def usuario_editar(id):
    usuario = Usuario.query.get_or_404(id)
    if not _editable(usuario): abort(403)
    form = UsuarioAdminForm(obj=usuario); _opciones_usuario(form)
    if request.method == 'GET': form.empleado_id.data = usuario.empleado_id or 0
    if form.validate_on_submit():
        repetido = Usuario.query.filter(Usuario.usuario == form.usuario.data.strip(), Usuario.id != usuario.id).first()
        if repetido: form.usuario.errors.append('Ese nombre de usuario ya existe.')
        else:
            usuario.usuario=form.usuario.data.strip(); usuario.nombre_mostrar=form.nombre_mostrar.data.strip()
            usuario.correo=(form.correo.data or '').strip() or None; usuario.empleado_id=form.empleado_id.data or None
            usuario.rol_id=form.rol_id.data; usuario.activo=form.activo.data
            db.session.commit(); flash('Usuario actualizado.', 'success'); return redirect(url_for('administracion.usuarios'))
    return render_template('administracion/usuario_form.html', form=form, titulo='Editar usuario', minimo=int(_config('password_min_length', 8)), edicion=True, usuario=usuario)


@administracion_bp.post('/usuarios/<int:id>/estado')
@login_required
@solo_administrador
def usuario_estado(id):
    usuario = Usuario.query.get_or_404(id)
    if not _editable(usuario): abort(403)
    usuario.activo = not usuario.activo
    if not usuario.activo:
        for sesion in SesionUsuario.query.filter_by(usuario_id=usuario.id, cerrada_en=None):
            sesion.cerrada_en=datetime.utcnow(); sesion.cerrada_por=current_user.id; sesion.motivo_cierre='Cuenta desactivada'
    db.session.commit(); flash('Estado de la cuenta actualizado.', 'success')
    return redirect(url_for('administracion.usuarios'))


@administracion_bp.route('/usuarios/<int:id>/password', methods=['GET', 'POST'])
@login_required
@solo_administrador
def usuario_password(id):
    usuario = Usuario.query.get_or_404(id)
    if not _editable(usuario): abort(403)
    form=PasswordAdminForm(); minimo=int(_config('password_min_length', 8))
    if form.validate_on_submit():
        if len(form.password.data) < minimo: form.password.errors.append(f'Debe tener al menos {minimo} caracteres.')
        else:
            usuario.password_hash=generate_password_hash(form.password.data); db.session.commit()
            flash('Contraseña restablecida. La contraseña anterior nunca fue visualizada.', 'success'); return redirect(url_for('administracion.usuarios'))
    return render_template('administracion/password.html', form=form, usuario=usuario, minimo=minimo)


@administracion_bp.route('/usuarios/<int:id>/permisos', methods=['GET', 'POST'])
@login_required
@solo_administrador
def permisos(id):
    usuario=Usuario.query.get_or_404(id)
    if not _editable(usuario): abort(403)
    if request.method == 'POST':
        PermisoUsuario.query.filter_by(usuario_id=usuario.id).delete()
        # Marcador para diferenciar "sin configuración" de "sin permisos".
        db.session.add(PermisoUsuario(usuario_id=usuario.id, modulo='_config', accion='_configured', permitido=True, asignado_por=current_user.id))
        for modulo in MODULOS:
            for accion in ACCIONES:
                if request.form.get(f'{modulo}:{accion}'):
                    db.session.add(PermisoUsuario(usuario_id=usuario.id, modulo=modulo, accion=accion, permitido=True, asignado_por=current_user.id))
        db.session.commit(); flash('Permisos actualizados.', 'success'); return redirect(url_for('administracion.usuarios'))
    actuales={(p.modulo,p.accion) for p in usuario.permisos if p.permitido}
    return render_template('administracion/permisos.html', usuario=usuario, modulos=MODULOS, acciones=ACCIONES, actuales=actuales)


@administracion_bp.route('/auditoria')
@login_required
@solo_administrador
def auditoria():
    consulta=Auditoria.query
    modulo=request.args.get('modulo',''); usuario=request.args.get('usuario',''); accion=request.args.get('accion','')
    if modulo: consulta=consulta.filter_by(modulo=modulo)
    if accion: consulta=consulta.filter_by(accion=accion)
    if usuario: consulta=consulta.filter(Auditoria.usuario_nombre.ilike(f'%{usuario}%'))
    registros=consulta.order_by(Auditoria.creado_en.desc()).limit(500).all()
    if request.args.get('exportar') == 'csv':
        salida=io.StringIO(); writer=csv.writer(salida); writer.writerow(['Fecha','Usuario','Módulo','Acción','Método','Detalle','IP','Estado'])
        for a in registros: writer.writerow([a.creado_en.isoformat(' '),a.usuario_nombre,a.modulo,a.accion,a.metodo,a.detalle,a.ip,a.estado_http])
        return Response('\ufeff'+salida.getvalue(), mimetype='text/csv', headers={'Content-Disposition':'attachment; filename=auditoria.csv'})
    return render_template('administracion/auditoria.html', registros=registros, modulos=MODULOS)


@administracion_bp.route('/reportes')
@login_required
@solo_administrador
def reportes():
    filas = db.session.query(Auditoria.usuario_nombre, Auditoria.modulo, Auditoria.accion, func.count(Auditoria.id).label('total')).group_by(Auditoria.usuario_nombre, Auditoria.modulo, Auditoria.accion).order_by(func.count(Auditoria.id).desc()).all()
    if request.args.get('exportar') == 'csv':
        salida=io.StringIO(); writer=csv.writer(salida); writer.writerow(['Usuario','Módulo','Acción','Cantidad'])
        writer.writerows(filas)
        return Response('\ufeff'+salida.getvalue(), mimetype='text/csv', headers={'Content-Disposition':'attachment; filename=reporte_actividad.csv'})
    return render_template('administracion/reportes.html', filas=filas)


@administracion_bp.route('/errores')
@login_required
@solo_administrador
def errores():
    return render_template('administracion/errores.html', errores=ErrorSistema.query.order_by(ErrorSistema.creado_en.desc()).limit(300).all())


@administracion_bp.route('/errores/<int:id>/revisar', methods=['GET','POST'])
@login_required
@solo_administrador
def error_revisar(id):
    error=ErrorSistema.query.get_or_404(id); form=RevisionErrorForm()
    if form.validate_on_submit():
        error.revisado=True; error.revisado_por=current_user.id; error.revisado_en=datetime.utcnow(); error.motivo_revision=form.motivo.data
        db.session.commit(); flash('Incidencia marcada como revisada.', 'success'); return redirect(url_for('administracion.errores'))
    return render_template('administracion/error_revisar.html', error=error, form=form)


@administracion_bp.route('/seguridad', methods=['GET','POST'])
@login_required
@solo_administrador
def seguridad():
    form=SeguridadForm()
    if request.method=='GET': form.longitud_minima.data=int(_config('password_min_length',8)); form.duracion_sesion.data=int(_config('session_max_minutes',480))
    if form.validate_on_submit():
        for clave,valor,descripcion in [('password_min_length',form.longitud_minima.data,'Longitud mínima de nuevas contraseñas'),('session_max_minutes',form.duracion_sesion.data,'Duración máxima de sesión en minutos')]:
            item=ConfiguracionSistema.query.get(clave) or ConfiguracionSistema(clave=clave,valor=str(valor)); item.valor=str(valor); item.descripcion=descripcion; item.actualizado_por=current_user.id; db.session.add(item)
        db.session.commit(); flash('Configuración de seguridad actualizada.', 'success'); return redirect(url_for('administracion.seguridad'))
    sesiones=SesionUsuario.query.filter_by(cerrada_en=None).order_by(SesionUsuario.ultima_actividad.desc()).all()
    return render_template('administracion/seguridad.html', form=form, sesiones=sesiones)


@administracion_bp.post('/sesiones/<string:id>/cerrar')
@login_required
@solo_administrador
def cerrar_sesion(id):
    sesion=SesionUsuario.query.get_or_404(id)
    if sesion.usuario_id == current_user.id or sesion.usuario.cuenta_protegida: abort(403)
    sesion.cerrada_en=datetime.utcnow(); sesion.cerrada_por=current_user.id; sesion.motivo_cierre='Cierre administrativo'; db.session.commit()
    flash('Sesión cerrada.', 'success'); return redirect(url_for('administracion.seguridad'))


@administracion_bp.route('/sistema')
@login_required
@solo_administrador
def sistema():
    inicio=time.perf_counter(); version_db=db.session.execute(text('select version()')).scalar(); db.session.execute(text('select 1')); latencia=round((time.perf_counter()-inicio)*1000,2)
    uri=current_app.config['SQLALCHEMY_DATABASE_URI']; host=current_app.config.get('DB_HOST'); nombre=current_app.config.get('DB_NAME')
    controles={'secret_configurada': current_app.config.get('SECRET_KEY') not in (None,'default_secret_key'), 'debug_desactivado': not current_app.debug, 'csrf_activo': True}
    return render_template('administracion/sistema.html', latencia=latencia, version_db=version_db, host=host, nombre=nombre, schema='rrhh', python=platform.python_version(), flask_version=platform.python_implementation(), controles=controles)
