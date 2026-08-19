import os
from datetime import datetime
from uuid import uuid4

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from sqlalchemy import func, or_
from werkzeug.utils import secure_filename

from extensions import db
from database.models import DocumentoRRHH, Empleado, TipoDocumento, Usuario, Rol
from .forms import DocumentoForm, DocumentoEditarForm, DocumentoEmpleadoForm

documentos_bp = Blueprint('documentos', __name__, url_prefix='/documentos')


def check_admin_or_rrhh():
    return current_user.rol.nombre in ['administrador', 'recursos_humanos']


def carpeta_documentos():
    carpeta = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.isabs(carpeta):
        carpeta = os.path.join(current_app.root_path, carpeta)
    carpeta = os.path.join(carpeta, 'documentos_privados')
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def opciones_formulario(form):
    if hasattr(form, 'empleado_id'):
        form.empleado_id.choices = [(0, 'Documentación interna de RR. HH. (sin empleado)')] + [(e.id, f"{e.legajo or '-'} - {e.nombre_apellido}") for e in Empleado.query.filter_by(estado='Activo').order_by(Empleado.nombre_apellido).all()]
    form.tipo_documento_id.choices = [(t.id, t.nombre) for t in TipoDocumento.query.filter_by(activo=True).order_by(TipoDocumento.nombre).all()]


def guardar_archivo(archivo):
    original = secure_filename(archivo.filename)
    extension = os.path.splitext(original)[1].lower()
    nombre_seguro = f"{datetime.now():%Y%m%d%H%M%S}_{uuid4().hex[:10]}{extension}"
    archivo.save(os.path.join(carpeta_documentos(), nombre_seguro))
    return original, nombre_seguro


def puede_acceder(doc):
    return check_admin_or_rrhh() or doc.cargado_por == current_user.id or (
        current_user.empleado and doc.empleado_id == current_user.empleado.id
        and doc.visible_empleado and doc.estado == 'Activo'
    )


@documentos_bp.route('/')
@login_required
def index():
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.index'))

    busqueda = request.args.get('q', '').strip()
    empleado_id = request.args.get('empleado_id', type=int)
    tipo_id = request.args.get('tipo_id', type=int)
    visibilidad = request.args.get('visibilidad', '')
    origen = request.args.get('origen', '')
    estado = request.args.get('estado', 'Activo')
    pagina = request.args.get('page', 1, type=int)

    query = DocumentoRRHH.query.join(Empleado, DocumentoRRHH.empleado_id == Empleado.id, isouter=True)
    if busqueda:
        patron = f"%{busqueda}%"
        query = query.filter(or_(DocumentoRRHH.nombre_documento.ilike(patron), DocumentoRRHH.nombre_archivo.ilike(patron), Empleado.nombre_apellido.ilike(patron), Empleado.legajo.ilike(patron)))
    if empleado_id:
        query = query.filter(DocumentoRRHH.empleado_id == empleado_id)
    if tipo_id:
        query = query.filter(DocumentoRRHH.tipo_documento_id == tipo_id)
    if visibilidad == 'empleado':
        query = query.filter(DocumentoRRHH.visible_empleado.is_(True))
    elif visibilidad == 'privado':
        query = query.filter(DocumentoRRHH.visible_empleado.is_(False))
    if origen == 'interno':
        query = query.filter(DocumentoRRHH.empleado_id.is_(None))
    elif origen == 'empleado':
        query = query.join(DocumentoRRHH.cargador).join(Usuario.rol).filter(Rol.nombre == 'empleado')
    elif origen == 'rrhh':
        query = query.join(DocumentoRRHH.cargador).join(Usuario.rol).filter(Rol.nombre.in_(['administrador', 'recursos_humanos']))
    if estado in ('Activo', 'Archivado'):
        query = query.filter(DocumentoRRHH.estado == estado)

    paginacion = query.order_by(DocumentoRRHH.creado_en.desc()).paginate(page=pagina, per_page=20, error_out=False)
    empleados = Empleado.query.filter_by(estado='Activo').order_by(Empleado.nombre_apellido).all()
    tipos = TipoDocumento.query.filter_by(activo=True).order_by(TipoDocumento.nombre).all()
    resumen = {
        'activos': DocumentoRRHH.query.filter_by(estado='Activo').count(),
        'compartidos': DocumentoRRHH.query.filter_by(estado='Activo', visible_empleado=True).count(),
        'privados': DocumentoRRHH.query.filter_by(estado='Activo', visible_empleado=False).count(),
        'archivados': DocumentoRRHH.query.filter_by(estado='Archivado').count(),
    }
    return render_template('documentos/index.html', documentos=paginacion.items, paginacion=paginacion, empleados=empleados, tipos=tipos, resumen=resumen)


@documentos_bp.route('/recibidos')
@login_required
def recibidos():
    if not check_admin_or_rrhh():
        abort(403)
    busqueda = request.args.get('q', '').strip()
    query = (
        db.session.query(
            Empleado,
            func.count(DocumentoRRHH.id).label('cantidad_documentos'),
            func.max(DocumentoRRHH.creado_en).label('ultimo_envio'),
        )
        .join(DocumentoRRHH, DocumentoRRHH.empleado_id == Empleado.id)
        .join(Usuario, DocumentoRRHH.cargado_por == Usuario.id)
        .join(Rol, Usuario.rol_id == Rol.id)
        .filter(Rol.nombre == 'empleado')
    )
    if busqueda:
        patron = f'%{busqueda}%'
        query = query.filter(or_(Empleado.nombre_apellido.ilike(patron), Empleado.legajo.ilike(patron), Empleado.dni.ilike(patron)))
    carpetas = query.group_by(Empleado.id).order_by(func.lower(Empleado.nombre_apellido)).all()
    return render_template(
        'documentos/recibidos.html', carpetas=carpetas,
        total_documentos=sum(cantidad for _, cantidad, _ in carpetas),
        busqueda=busqueda,
    )


@documentos_bp.route('/subir', methods=['GET', 'POST'])
@login_required
def subir():
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.index'))
    form = DocumentoForm()
    opciones_formulario(form)
    if form.validate_on_submit():
        original = ruta = None
        try:
            original, ruta = guardar_archivo(form.archivo.data)
            doc = DocumentoRRHH(empleado_id=form.empleado_id.data or None, tipo_documento_id=form.tipo_documento_id.data, nombre_documento=form.nombre_documento.data.strip(), nombre_archivo=original, ruta_archivo=ruta, visible_empleado=(form.visible_empleado.data if form.empleado_id.data else False), observaciones=form.observaciones.data, estado='Activo', cargado_por=current_user.id)
            db.session.add(doc)
            db.session.commit()
            flash('Documento subido y asignado correctamente.', 'success')
            return redirect(url_for('documentos.detalle', id=doc.id))
        except Exception:
            db.session.rollback()
            if ruta:
                ruta_fisica = os.path.join(carpeta_documentos(), ruta)
                if os.path.exists(ruta_fisica): os.remove(ruta_fisica)
            current_app.logger.exception('Error al subir documento')
            flash('No se pudo guardar el documento. Intentalo nuevamente.', 'danger')
    return render_template('documentos/subir.html', form=form)


@documentos_bp.route('/enviar', methods=['GET', 'POST'])
@login_required
def enviar_rrhh():
    if check_admin_or_rrhh():
        return redirect(url_for('documentos.subir'))
    if not current_user.empleado:
        flash('Tu usuario no tiene una ficha de empleado asociada.', 'warning')
        return redirect(url_for('dashboard.index'))
    form = DocumentoEmpleadoForm()
    opciones_formulario(form)
    if form.validate_on_submit():
        original = ruta = None
        try:
            original, ruta = guardar_archivo(form.archivo.data)
            doc = DocumentoRRHH(
                empleado_id=current_user.empleado.id,
                tipo_documento_id=form.tipo_documento_id.data,
                nombre_documento=form.nombre_documento.data.strip(),
                nombre_archivo=original,
                ruta_archivo=ruta,
                visible_empleado=False,
                observaciones=form.observaciones.data,
                estado='Activo',
                cargado_por=current_user.id,
            )
            db.session.add(doc)
            db.session.commit()
            flash('Documento enviado a Recursos Humanos correctamente.', 'success')
            return redirect(url_for('documentos.envios'))
        except Exception:
            db.session.rollback()
            if ruta:
                archivo = os.path.join(carpeta_documentos(), ruta)
                if os.path.isfile(archivo): os.remove(archivo)
            current_app.logger.exception('Error al enviar documento a RRHH')
            flash('No se pudo enviar el documento.', 'danger')
    return render_template('documentos/enviar.html', form=form)


@documentos_bp.route('/mis-envios')
@login_required
def envios():
    if not current_user.empleado:
        flash('Tu usuario no tiene una ficha de empleado asociada.', 'warning')
        return redirect(url_for('dashboard.index'))
    documentos = DocumentoRRHH.query.filter_by(empleado_id=current_user.empleado.id, cargado_por=current_user.id).order_by(DocumentoRRHH.creado_en.desc()).all()
    return render_template('documentos/envios.html', documentos=documentos)


@documentos_bp.route('/<int:id>')
@login_required
def detalle(id):
    doc = DocumentoRRHH.query.get_or_404(id)
    if not puede_acceder(doc): abort(403)
    existe_archivo = os.path.isfile(os.path.join(carpeta_documentos(), doc.ruta_archivo))
    return render_template('documentos/detalle.html', doc=doc, existe_archivo=existe_archivo)


@documentos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not check_admin_or_rrhh(): abort(403)
    doc = DocumentoRRHH.query.get_or_404(id)
    form = DocumentoEditarForm(obj=doc)
    opciones_formulario(form)
    if form.validate_on_submit():
        ruta_anterior = doc.ruta_archivo
        ruta_nueva = None
        try:
            if form.archivo.data:
                doc.nombre_archivo, ruta_nueva = guardar_archivo(form.archivo.data)
                doc.ruta_archivo = ruta_nueva
            doc.empleado_id = form.empleado_id.data or None
            doc.tipo_documento_id = form.tipo_documento_id.data
            doc.nombre_documento = form.nombre_documento.data.strip()
            doc.visible_empleado = form.visible_empleado.data if form.empleado_id.data else False
            doc.observaciones = form.observaciones.data
            db.session.commit()
            if ruta_nueva:
                anterior = os.path.join(carpeta_documentos(), ruta_anterior)
                if os.path.isfile(anterior): os.remove(anterior)
            flash('Documento actualizado correctamente.', 'success')
            return redirect(url_for('documentos.detalle', id=doc.id))
        except Exception:
            db.session.rollback()
            if ruta_nueva:
                nuevo = os.path.join(carpeta_documentos(), ruta_nueva)
                if os.path.isfile(nuevo): os.remove(nuevo)
            current_app.logger.exception('Error al editar documento')
            flash('No se pudieron guardar los cambios.', 'danger')
    return render_template('documentos/editar.html', form=form, doc=doc)


@documentos_bp.route('/<int:id>/archivo')
@login_required
def ver_archivo(id):
    doc = DocumentoRRHH.query.get_or_404(id)
    if not puede_acceder(doc): abort(403)
    return send_from_directory(carpeta_documentos(), doc.ruta_archivo, as_attachment=False, download_name=doc.nombre_archivo)


@documentos_bp.route('/descargar/<int:id>')
@login_required
def descargar(id):
    doc = DocumentoRRHH.query.get_or_404(id)
    if not puede_acceder(doc): abort(403)
    return send_from_directory(carpeta_documentos(), doc.ruta_archivo, as_attachment=True, download_name=doc.nombre_archivo)


@documentos_bp.route('/mis-documentos')
@login_required
def mis_documentos():
    if not current_user.empleado:
        flash('No tenés una ficha de empleado asociada.', 'warning')
        return redirect(url_for('dashboard.index'))
    documentos = DocumentoRRHH.query.filter_by(empleado_id=current_user.empleado.id, visible_empleado=True, estado='Activo').order_by(DocumentoRRHH.creado_en.desc()).all()
    return render_template('documentos/mis_documentos.html', documentos=documentos)


@documentos_bp.route('/<int:id>/estado', methods=['POST'])
@login_required
def cambiar_estado(id):
    if not check_admin_or_rrhh(): abort(403)
    doc = DocumentoRRHH.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')
    if nuevo_estado not in ('Activo', 'Archivado'): abort(400)
    doc.estado = nuevo_estado
    db.session.commit()
    flash('Documento restaurado.' if nuevo_estado == 'Activo' else 'Documento archivado.', 'success')
    return redirect(request.referrer or url_for('documentos.index'))


@documentos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    if not check_admin_or_rrhh(): abort(403)
    doc = DocumentoRRHH.query.get_or_404(id)
    if doc.estado != 'Archivado':
        flash('Primero archivá el documento antes de eliminarlo permanentemente.', 'warning')
        return redirect(url_for('documentos.detalle', id=id))
    try:
        ruta = os.path.join(carpeta_documentos(), doc.ruta_archivo)
        db.session.delete(doc)
        db.session.commit()
        if os.path.isfile(ruta): os.remove(ruta)
        flash('Documento eliminado permanentemente.', 'success')
    except Exception:
        db.session.rollback()
        current_app.logger.exception('Error al eliminar documento')
        flash('No se pudo eliminar el documento.', 'danger')
    return redirect(url_for('documentos.index', estado='Archivado'))
