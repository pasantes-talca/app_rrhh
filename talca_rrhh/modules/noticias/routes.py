import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from database.models import Noticia, Empresa, Sector
from .forms import NoticiaForm

noticias_bp = Blueprint('noticias', __name__, url_prefix='/noticias')

def check_admin_or_rrhh():
    return current_user.rol.nombre in ['administrador', 'recursos_humanos']

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
    form.empresa_id.choices = [(0, '--- Ninguna ---')] + [(e.id, e.nombre) for e in Empresa.query.filter_by(activo=True).all()]
    form.sector_id.choices = [(0, '--- Ninguno ---')] + [(s.id, s.nombre) for s in Sector.query.filter_by(activo=True).all()]
    
    if form.validate_on_submit():
        archivo_nombre = None
        if form.imagen.data:
            f = form.imagen.data
            filename = secure_filename(f.filename)
            upload_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), 'noticias')
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
            f.save(file_path)
            # Guardamos ruta relativa para usarla en web
            archivo_nombre = f"uploads/noticias/{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"

        noticia = Noticia(
            titulo=form.titulo.data,
            contenido=form.contenido.data,
            imagen=archivo_nombre,
            estado=form.estado.data,
            visible_todos=form.visible_todos.data,
            empresa_id=form.empresa_id.data if form.empresa_id.data != 0 else None,
            sector_id=form.sector_id.data if form.sector_id.data != 0 else None,
            publicado_por=current_user.id,
            fecha_publicacion=datetime.utcnow() if form.estado.data == 'Publicada' else None
        )
        
        try:
            db.session.add(noticia)
            db.session.commit()
            flash('Noticia guardada exitosamente.', 'success')
            return redirect(url_for('noticias.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'danger')
            
    return render_template('noticias/form.html', form=form, title='Nueva Noticia')

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
