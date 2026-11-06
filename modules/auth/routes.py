from pathlib import Path
from uuid import uuid4
from datetime import datetime

from flask import Blueprint, current_app, render_template, redirect, send_from_directory, session, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from extensions import db
from database.models import Empleado, Empresa, Jornada, Puesto, Sector, SesionUsuario, Usuario
from .forms import CambiarPasswordForm, LoginForm, PerfilForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        # Evita rechazos por espacios pegados accidentalmente al legajo/usuario.
        nombre_usuario = form.usuario.data.strip()
        user = Usuario.query.filter(func.lower(Usuario.usuario) == nombre_usuario.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.activo:
                flash('Su cuenta está inactiva. Contacte al administrador.', 'danger')
                return redirect(url_for('auth.login'))
                
            login_user(user)
            sesion_id = uuid4().hex
            session['sesion_id'] = sesion_id
            db.session.add(SesionUsuario(id=sesion_id, usuario_id=user.id,
                ip=request.headers.get('X-Forwarded-For', request.remote_addr),
                agente=request.headers.get('User-Agent'), iniciada_en=datetime.utcnow(), ultima_actividad=datetime.utcnow()))
            user.ultimo_acceso = datetime.utcnow()
            db.session.commit()
            flash('Inicio de sesión exitoso', 'success')
            if user.debe_cambiar_password:
                flash('Estás usando una contraseña temporal. Podés cambiarla desde Mi perfil.', 'warning')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    sesion_actual = SesionUsuario.query.get(session.get('sesion_id')) if session.get('sesion_id') else None
    if sesion_actual:
        sesion_actual.cerrada_en = datetime.utcnow()
        sesion_actual.motivo_cierre = 'Cierre de sesión del usuario'
        db.session.commit()
    logout_user()
    session.clear()
    flash('Ha cerrado sesión correctamente', 'success')
    return redirect(url_for('auth.login'))


def _directorio_fotos():
    base = Path(current_app.config['UPLOAD_FOLDER'])
    if not base.is_absolute():
        base = Path(current_app.root_path) / base
    destino = base / 'perfiles'
    destino.mkdir(parents=True, exist_ok=True)
    return destino


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    empleado = current_user.empleado
    empleado2 = current_user.empleado2
    form = PerfilForm()
    form.empresa_id.choices = [(0, 'Sin informar')] + [(item.id, item.nombre) for item in Empresa.query.filter_by(activo=True).order_by(Empresa.nombre).all()]
    form.sector_id.choices = [(0, 'Sin informar')] + [(item.id, item.nombre) for item in Sector.query.filter_by(activo=True).order_by(Sector.nombre).all()]
    form.puesto_id.choices = [(0, 'Sin informar')] + [(item.id, item.nombre) for item in Puesto.query.filter_by(activo=True).order_by(Puesto.nombre).all()]
    form.jornada_id.choices = [(0, 'Sin informar')] + [(item.id, item.nombre) for item in Jornada.query.filter_by(activo=True).order_by(Jornada.nombre).all()]
    form.supervisor_id.choices = [(0, 'Sin supervisor')] + [(item.id, item.nombre_apellido) for item in Empleado.query.filter(Empleado.id != (empleado.id if empleado else 0)).order_by(Empleado.nombre_apellido).all()]
    if request.method == 'GET':
        nombre_trilay = f'{empleado2.nombre or ""} {empleado2.apellido or ""}'.strip() if empleado2 else None
        form.nombre_apellido.data = current_user.nombre_mostrar or (empleado.nombre_apellido if empleado else nombre_trilay or current_user.usuario)
        form.correo.data = current_user.correo or (empleado.correo if empleado else (empleado2.correo if empleado2 else ''))
        if empleado:
            for campo in ('telefono', 'fecha_nacimiento', 'genero', 'domicilio', 'provincia', 'codigo_postal', 'licencia_conducir', 'dni', 'cuil', 'legajo', 'jornada_horas', 'fecha_ingreso', 'estado'):
                getattr(form, campo).data = getattr(empleado, campo)
            form.empresa_id.data = empleado.empresa_id or 0
            form.sector_id.data = empleado.sector_id or 0
            form.puesto_id.data = empleado.puesto_id or 0
            form.supervisor_id.data = empleado.supervisor_id or 0
            form.jornada_id.data = empleado.jornada_id or 0

    if form.validate_on_submit():
        correo = (form.correo.data or '').strip() or None
        repetido = Usuario.query.filter(Usuario.correo == correo, Usuario.id != current_user.id).first() if correo else None
        dni = (form.dni.data or '').strip() or None
        cuil = (form.cuil.data or '').strip() or None
        legajo = (form.legajo.data or '').strip() or None
        conflicto_dni = Empleado.query.filter(Empleado.dni == dni, Empleado.id != empleado.id).first() if empleado and dni else None
        conflicto_cuil = Empleado.query.filter(Empleado.cuil == cuil, Empleado.id != empleado.id).first() if empleado and cuil else None
        conflicto_legajo = Empleado.query.filter(Empleado.legajo == legajo, Empleado.id != empleado.id).first() if empleado and legajo else None
        conflicto_usuario = Usuario.query.filter(Usuario.usuario == legajo, Usuario.id != current_user.id).first() if empleado and legajo else None
        if repetido:
            form.correo.errors.append('Ese correo ya está asociado a otro usuario.')
        elif empleado and not dni:
            form.dni.errors.append('El DNI es obligatorio.')
        elif empleado and not legajo:
            form.legajo.errors.append('El legajo es obligatorio porque también es tu usuario de acceso.')
        elif conflicto_dni:
            form.dni.errors.append('Ese DNI ya pertenece a otro empleado.')
        elif conflicto_cuil:
            form.cuil.errors.append('Ese CUIL ya pertenece a otro empleado.')
        elif conflicto_legajo or conflicto_usuario:
            form.legajo.errors.append('Ese legajo ya está siendo utilizado.')
        else:
            foto_anterior = current_user.foto_perfil
            foto_nueva = None
            if form.foto.data:
                extension = secure_filename(form.foto.data.filename).rsplit('.', 1)[-1].lower()
                foto_nueva = f'{current_user.id}_{uuid4().hex}.{extension}'
                form.foto.data.save(_directorio_fotos() / foto_nueva)
            current_user.nombre_mostrar = form.nombre_apellido.data.strip()
            current_user.correo = correo
            if foto_nueva:
                current_user.foto_perfil = foto_nueva
            elif form.eliminar_foto.data:
                current_user.foto_perfil = None
            if empleado:
                empleado.nombre_apellido = form.nombre_apellido.data.strip()
                empleado.correo = correo
                for campo in ('telefono', 'fecha_nacimiento', 'genero', 'domicilio', 'provincia', 'codigo_postal', 'licencia_conducir', 'jornada_horas', 'fecha_ingreso', 'estado'):
                    valor = getattr(form, campo).data
                    setattr(empleado, campo, valor.strip() if isinstance(valor, str) else valor)
                empleado.dni = dni
                empleado.cuil = cuil
                empleado.legajo = legajo
                empleado.empresa_id = form.empresa_id.data or None
                empleado.sector_id = form.sector_id.data or None
                empleado.puesto_id = form.puesto_id.data or None
                empleado.supervisor_id = form.supervisor_id.data or None
                empleado.jornada_id = form.jornada_id.data or None
                if not empleado2:
                    current_user.usuario = legajo
            db.session.commit()
            if foto_anterior and foto_anterior != current_user.foto_perfil:
                anterior = _directorio_fotos() / Path(foto_anterior).name
                if anterior.is_file():
                    anterior.unlink()
            flash('Tu información personal se actualizó correctamente.', 'success')
            return redirect(url_for('auth.perfil'))
    return render_template('auth/perfil.html', form=form, empleado=empleado, empleado2=empleado2,
                           password_form=CambiarPasswordForm())


@auth_bp.route('/perfil/password', methods=['POST'])
@login_required
def cambiar_password():
    form = CambiarPasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, form.password_actual.data):
            flash('La contraseña actual no es correcta.', 'danger')
        elif check_password_hash(current_user.password_hash, form.password_nueva.data):
            flash('La nueva contraseña debe ser diferente de la actual.', 'warning')
        else:
            current_user.password_hash = generate_password_hash(form.password_nueva.data)
            current_user.debe_cambiar_password = False
            db.session.commit()
            flash('Tu contraseña se actualizó correctamente.', 'success')
            return redirect(url_for('auth.perfil'))
    else:
        for errors in form.errors.values():
            for error in errors:
                flash(error, 'danger')
    return redirect(url_for('auth.perfil'))


@auth_bp.route('/perfil/foto')
@login_required
def foto_perfil():
    if not current_user.foto_perfil:
        return redirect(url_for('static', filename='img/logo-talca.png'))
    return send_from_directory(_directorio_fotos(), Path(current_user.foto_perfil).name)
