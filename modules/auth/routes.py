from pathlib import Path
from uuid import uuid4
from datetime import datetime

from flask import Blueprint, current_app, render_template, redirect, send_from_directory, session, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from extensions import db
from database.models import SesionUsuario, Usuario
from .forms import LoginForm, PerfilForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        # Evita rechazos por espacios pegados accidentalmente al legajo/usuario.
        nombre_usuario = form.usuario.data.strip()
        user = Usuario.query.filter_by(usuario=nombre_usuario).first()
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
    form = PerfilForm()
    if request.method == 'GET':
        form.nombre_apellido.data = current_user.nombre_mostrar or (empleado.nombre_apellido if empleado else current_user.usuario)
        form.correo.data = current_user.correo or (empleado.correo if empleado else '')
        if empleado:
            for campo in ('telefono', 'fecha_nacimiento', 'genero', 'domicilio', 'provincia', 'codigo_postal', 'licencia_conducir'):
                getattr(form, campo).data = getattr(empleado, campo)

    if form.validate_on_submit():
        correo = (form.correo.data or '').strip() or None
        repetido = Usuario.query.filter(Usuario.correo == correo, Usuario.id != current_user.id).first() if correo else None
        if repetido:
            form.correo.errors.append('Ese correo ya está asociado a otro usuario.')
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
                for campo in ('telefono', 'fecha_nacimiento', 'genero', 'domicilio', 'provincia', 'codigo_postal', 'licencia_conducir'):
                    valor = getattr(form, campo).data
                    setattr(empleado, campo, valor.strip() if isinstance(valor, str) else valor)
            db.session.commit()
            if foto_anterior and foto_anterior != current_user.foto_perfil:
                anterior = _directorio_fotos() / Path(foto_anterior).name
                if anterior.is_file():
                    anterior.unlink()
            flash('Tu información personal se actualizó correctamente.', 'success')
            return redirect(url_for('auth.perfil'))
    return render_template('auth/perfil.html', form=form, empleado=empleado)


@auth_bp.route('/perfil/foto')
@login_required
def foto_perfil():
    if not current_user.foto_perfil:
        return redirect(url_for('static', filename='img/logo-talca.png'))
    return send_from_directory(_directorio_fotos(), Path(current_user.foto_perfil).name)
