import os
from datetime import datetime
from flask import Blueprint, abort, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from database.models import Noticia, Empresa, Sector
from modules.notificaciones.services import notificar_noticia
from .forms import NoticiaForm

noticias_bp = Blueprint('noticias', __name__, url_prefix='/noticias')


def configurar_opciones(form):
    form.empresa_id.choices = [(0, '--- Ninguna ---')] + [(e.id, e.nombre) for e in Empresa.query.filter_by(activo=True).all()]
    form.sector_id.choices = [(0, '--- Ninguno ---')] + [(s.id, s.nombre) for s in Sector.query.filter_by(activo=True).all()]


def guardar_adjunto(archivo):
    if not archivo:
        return None
    filename = secure_filename(archivo.filename)
    upload_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), 'noticias')
    os.makedirs(upload_path, exist_ok=True)
    nombre_guardado = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
    file_path = os.path.join(upload_path, nombre_guardado)
    archivo.save(file_path)
    return os.path.relpath(file_path, current_app.root_path)

def check_admin_or_rrhh():
    return current_user.rol.nombre in ['administrador', 'recursos_humanos']


def puede_ver_noticia(noticia):
    if check_admin_or_rrhh():
        return True
    empleado = current_user.empleado
    return bool(empleado and (
        noticia.visible_todos
        or noticia.empresa_id == empleado.empresa_id
        or noticia.sector_id == empleado.sector_id
    ))


@noticias_bp.route('/<int:id>/imagen')
@login_required
def imagen(id):
    noticia = Noticia.query.get_or_404(id)
    if noticia.estado != 'Publicada' or not puede_ver_noticia(noticia):
        abort(403)
    if not noticia.imagen:
        abort(404)
    ruta = noticia.imagen
    if not os.path.isabs(ruta):
        ruta = os.path.join(current_app.root_path, ruta)
    ruta = os.path.abspath(ruta)
    carpeta_permitida = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.isabs(carpeta_permitida):
        carpeta_permitida = os.path.join(current_app.root_path, carpeta_permitida)
    carpeta_permitida = os.path.abspath(carpeta_permitida)
    if os.path.commonpath([ruta, carpeta_permitida]) != carpeta_permitida or not os.path.isfile(ruta):
        abort(404)
    descargar = request.args.get('descargar', type=int) == 1
    return send_from_directory(
        os.path.dirname(ruta), os.path.basename(ruta),
        as_attachment=descargar, download_name=os.path.basename(ruta),
    )

@noticias_bp.route('/')
@login_required
def index():
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    noticias = Noticia.query.order_by(Noticia.creado_en.desc()).all()
    return render_template('noticias/index.html', noticias=noticias)

@noticias_bp.route('/muro')
@login_required
def muro():
    # Filtrar noticias publicadas y que sean visibles para todos o coincidan con empresa/sector del empleado
    query = Noticia.query.filter_by(estado='Publicada')
    
    if not check_admin_or_rrhh() and current_user.empleado:
        emp_id = current_user.empleado.empresa_id
        sec_id = current_user.empleado.sector_id
        
        # Filtro compuesto: visibles_todos = True OR empresa=emp_id OR sector=sec_id
        from sqlalchemy import or_
        query = query.filter(or_(
            Noticia.visible_todos == True,
            Noticia.empresa_id == emp_id,
            Noticia.sector_id == sec_id
        ))
        
    noticias = query.order_by(Noticia.fecha_publicacion.desc()).all()
    return render_template('noticias/muro.html', noticias=noticias)

@noticias_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.index'))

    form = NoticiaForm()
    configurar_opciones(form)
    
    if form.validate_on_submit():
        if form.es_fecha_importante.data and not form.fecha_importante.data:
            form.fecha_importante.errors.append('Elegí la fecha que se mostrará en el calendario.')
            return render_template('noticias/form.html', form=form, title='Nueva Noticia')
        archivo_nombre = guardar_adjunto(form.imagen.data)

        noticia = Noticia(
            titulo=form.titulo.data,
            contenido=form.contenido.data,
            imagen=archivo_nombre,
            estado='Publicada',
            visible_todos=form.visible_todos.data,
            es_fecha_importante=form.es_fecha_importante.data,
            fecha_importante=form.fecha_importante.data if form.es_fecha_importante.data else None,
            empresa_id=form.empresa_id.data if form.empresa_id.data != 0 else None,
            sector_id=form.sector_id.data if form.sector_id.data != 0 else None,
            publicado_por=current_user.id,
            fecha_publicacion=datetime.utcnow()
        )
        
        try:
            db.session.add(noticia)
            db.session.flush()
            notificar_noticia(noticia, excluir_usuario_id=current_user.id)
            db.session.commit()
            flash('Noticia publicada exitosamente.', 'success')
            return redirect(url_for('noticias.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'danger')
            
    return render_template('noticias/form.html', form=form, title='Nueva Noticia')


@noticias_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.index'))
    noticia = Noticia.query.get_or_404(id)
    form = NoticiaForm(obj=noticia)
    configurar_opciones(form)
    if request.method == 'GET':
        form.empresa_id.data = noticia.empresa_id or 0
        form.sector_id.data = noticia.sector_id or 0
    if form.validate_on_submit():
        if form.es_fecha_importante.data and not form.fecha_importante.data:
            form.fecha_importante.errors.append('Elegí la fecha que se mostrará en el calendario.')
            return render_template('noticias/form.html', form=form, title='Editar noticia', noticia=noticia)
        noticia.titulo = form.titulo.data
        noticia.contenido = form.contenido.data
        noticia.visible_todos = form.visible_todos.data
        noticia.es_fecha_importante = form.es_fecha_importante.data
        noticia.fecha_importante = form.fecha_importante.data if form.es_fecha_importante.data else None
        noticia.empresa_id = form.empresa_id.data or None
        noticia.sector_id = form.sector_id.data or None
        noticia.estado = 'Publicada'
        noticia.fecha_publicacion = noticia.fecha_publicacion or datetime.utcnow()
        if form.imagen.data:
            noticia.imagen = guardar_adjunto(form.imagen.data)
        try:
            notificar_noticia(noticia, excluir_usuario_id=current_user.id)
            db.session.commit()
            flash('Noticia actualizada exitosamente.', 'success')
            return redirect(url_for('noticias.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')
    return render_template('noticias/form.html', form=form, title='Editar noticia', noticia=noticia)

@noticias_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    noticia = Noticia.query.get_or_404(id)
    try:
        db.session.delete(noticia)
        db.session.commit()
        flash('Noticia eliminada.', 'success')
    except:
        db.session.rollback()
        flash('Error al eliminar.', 'danger')
        
    return redirect(url_for('noticias.index'))
