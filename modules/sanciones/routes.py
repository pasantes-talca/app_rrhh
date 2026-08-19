import os
from datetime import datetime
from uuid import uuid4

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from database.models import Empleado, Notificacion, SancionDisciplinaria, Usuario
from extensions import db
from .forms import SancionForm

sanciones_bp = Blueprint('sanciones', __name__, url_prefix='/sanciones')


def exigir_rrhh():
    if current_user.rol.nombre not in ['administrador', 'recursos_humanos']:
        abort(403)


def carpeta_sanciones():
    base = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.isabs(base):
        base = os.path.join(current_app.root_path, base)
    carpeta = os.path.join(base, 'sanciones_privadas')
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def poblar_empleados(form):
    form.empleado_id.choices = [
        (e.id, f'{e.legajo or "-"} - {e.nombre_apellido}')
        for e in Empleado.query.filter_by(estado='Activo').order_by(Empleado.nombre_apellido).all()
    ]


def guardar_archivo(archivo):
    original = secure_filename(archivo.filename)
    extension = os.path.splitext(original)[1].lower()
    nombre = f'{datetime.now():%Y%m%d%H%M%S}_{uuid4().hex[:10]}{extension}'
    archivo.save(os.path.join(carpeta_sanciones(), nombre))
    return original, nombre


def crear_notificacion(sancion):
    usuario = Usuario.query.filter_by(empleado_id=sancion.empleado_id, activo=True).first()
    if not usuario:
        return False
    existente = Notificacion.query.filter_by(
        usuario_id=usuario.id,
        referencia_tipo='sancion',
        referencia_id=sancion.id,
    ).first()
    if existente:
        return True
    mensaje = f'Se registró una medida de tipo {sancion.tipo} con fecha {sancion.fecha:%d/%m/%Y}. Motivo: {sancion.motivo}.'
    if sancion.tipo == 'Suspensión' and sancion.fecha_desde and sancion.fecha_hasta:
        mensaje += f' Período: {sancion.fecha_desde:%d/%m/%Y} al {sancion.fecha_hasta:%d/%m/%Y}.'
    db.session.add(Notificacion(
        usuario_id=usuario.id,
        titulo='Nueva medida disciplinaria notificada',
        mensaje=mensaje,
        tipo='sancion',
        referencia_tipo='sancion',
        referencia_id=sancion.id,
    ))
    return True


@sanciones_bp.route('/')
@login_required
def index():
    exigir_rrhh()
    q = request.args.get('q', '').strip()
    tipo = request.args.get('tipo', '')
    estado = request.args.get('estado', '')
    query = SancionDisciplinaria.query.join(Empleado)
    if q:
        patron = f'%{q}%'
        query = query.filter(or_(
            Empleado.nombre_apellido.ilike(patron), Empleado.legajo.ilike(patron),
            Empleado.dni.ilike(patron), SancionDisciplinaria.motivo.ilike(patron),
        ))
    if tipo:
        query = query.filter(SancionDisciplinaria.tipo == tipo)
    if estado:
        query = query.filter(SancionDisciplinaria.estado == estado)
    sanciones = query.order_by(SancionDisciplinaria.fecha.desc(), SancionDisciplinaria.creado_en.desc()).all()
    resumen = {
        'total': SancionDisciplinaria.query.count(),
        'borradores': SancionDisciplinaria.query.filter_by(estado='Borrador').count(),
        'notificadas': SancionDisciplinaria.query.filter_by(estado='Notificada').count(),
        'suspensiones': SancionDisciplinaria.query.filter_by(tipo='Suspensión').count(),
    }
    return render_template('sanciones/index.html', sanciones=sanciones, resumen=resumen, q=q, tipo=tipo, estado=estado)


@sanciones_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    exigir_rrhh()
    form = SancionForm()
    poblar_empleados(form)
    if form.validate_on_submit():
        original = ruta = None
        try:
            if form.archivo.data:
                original, ruta = guardar_archivo(form.archivo.data)
            sancion = SancionDisciplinaria(
                empleado_id=form.empleado_id.data, tipo=form.tipo.data, fecha=form.fecha.data,
                fecha_desde=form.fecha_desde.data if form.tipo.data == 'Suspensión' else None,
                fecha_hasta=form.fecha_hasta.data if form.tipo.data == 'Suspensión' else None,
                cantidad_dias=form.cantidad_dias.data if form.tipo.data == 'Suspensión' else None,
                motivo=form.motivo.data.strip(), descripcion=form.descripcion.data,
                observaciones=form.observaciones.data, nombre_archivo=original, ruta_archivo=ruta,
                estado=form.estado.data, creado_por=current_user.id,
                notificado_en=datetime.utcnow() if form.estado.data == 'Notificada' else None,
            )
            db.session.add(sancion)
            db.session.flush()
            usuario_notificado = True
            if sancion.estado == 'Notificada':
                usuario_notificado = crear_notificacion(sancion)
            db.session.commit()
            flash('Medida disciplinaria registrada.', 'success')
            if sancion.estado == 'Notificada' and not usuario_notificado:
                flash('La medida se guardó, pero el empleado no tiene un usuario activo para recibir la notificación.', 'warning')
            return redirect(url_for('sanciones.ver', id=sancion.id))
        except Exception:
            db.session.rollback()
            if ruta:
                archivo = os.path.join(carpeta_sanciones(), ruta)
                if os.path.isfile(archivo): os.remove(archivo)
            current_app.logger.exception('Error al guardar sanción')
            flash('No se pudo guardar la medida.', 'danger')
    return render_template('sanciones/form.html', form=form, titulo='Nueva medida disciplinaria')


@sanciones_bp.route('/<int:id>')
@login_required
def ver(id):
    exigir_rrhh()
    sancion = SancionDisciplinaria.query.get_or_404(id)
    return render_template('sanciones/ver.html', sancion=sancion)


@sanciones_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    exigir_rrhh()
    sancion = SancionDisciplinaria.query.get_or_404(id)
    form = SancionForm(obj=sancion)
    poblar_empleados(form)
    if form.validate_on_submit():
        ruta_anterior, ruta_nueva = sancion.ruta_archivo, None
        try:
            if form.archivo.data:
                sancion.nombre_archivo, ruta_nueva = guardar_archivo(form.archivo.data)
                sancion.ruta_archivo = ruta_nueva
            estado_anterior = sancion.estado
            sancion.empleado_id = form.empleado_id.data
            sancion.tipo, sancion.fecha = form.tipo.data, form.fecha.data
            sancion.fecha_desde = form.fecha_desde.data if form.tipo.data == 'Suspensión' else None
            sancion.fecha_hasta = form.fecha_hasta.data if form.tipo.data == 'Suspensión' else None
            sancion.cantidad_dias = form.cantidad_dias.data if form.tipo.data == 'Suspensión' else None
            sancion.motivo, sancion.descripcion = form.motivo.data.strip(), form.descripcion.data
            sancion.observaciones, sancion.estado = form.observaciones.data, form.estado.data
            if form.estado.data == 'Notificada' and estado_anterior != 'Notificada':
                sancion.notificado_en = datetime.utcnow()
            usuario_notificado = True
            if form.estado.data == 'Notificada':
                usuario_notificado = crear_notificacion(sancion)
            db.session.commit()
            if ruta_nueva and ruta_anterior:
                anterior = os.path.join(carpeta_sanciones(), ruta_anterior)
                if os.path.isfile(anterior): os.remove(anterior)
            flash('Medida actualizada.', 'success')
            if form.estado.data == 'Notificada' and not usuario_notificado:
                flash('El empleado no tiene un usuario activo para recibir la notificación.', 'warning')
            return redirect(url_for('sanciones.ver', id=sancion.id))
        except Exception:
            db.session.rollback()
            if ruta_nueva:
                nuevo = os.path.join(carpeta_sanciones(), ruta_nueva)
                if os.path.isfile(nuevo): os.remove(nuevo)
            current_app.logger.exception('Error al editar sanción')
            flash('No se pudieron guardar los cambios.', 'danger')
    return render_template('sanciones/form.html', form=form, titulo='Editar medida disciplinaria', sancion=sancion)


@sanciones_bp.route('/<int:id>/archivo')
@login_required
def descargar(id):
    exigir_rrhh()
    sancion = SancionDisciplinaria.query.get_or_404(id)
    if not sancion.ruta_archivo: abort(404)
    return send_from_directory(carpeta_sanciones(), sancion.ruta_archivo, as_attachment=True, download_name=sancion.nombre_archivo)
