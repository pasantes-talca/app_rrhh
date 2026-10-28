from datetime import date, datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from database.models import Feriado, Notificacion
from extensions import db

notificaciones_bp = Blueprint('notificaciones', __name__, url_prefix='/notificaciones')


def exigir_gestion():
    if current_user.rol.nombre not in ['administrador', 'recursos_humanos']:
        abort(403)


@notificaciones_bp.route('/fechas-importantes', methods=['GET', 'POST'])
@login_required
def fechas_importantes():
    exigir_gestion()
    if request.method == 'POST':
        descripcion = request.form.get('descripcion', '').strip()
        try:
            fecha = date.fromisoformat(request.form.get('fecha', ''))
        except ValueError:
            fecha = None
        if not fecha or not descripcion:
            flash('Completá la fecha y la descripción.', 'warning')
        elif Feriado.query.filter_by(fecha=fecha).first():
            flash('Ya existe una fecha importante para ese día.', 'warning')
        else:
            db.session.add(Feriado(fecha=fecha, descripcion=descripcion[:200]))
            db.session.commit()
            flash('Fecha importante agregada.', 'success')
        return redirect(url_for('notificaciones.fechas_importantes'))
    fechas = Feriado.query.order_by(Feriado.fecha.asc()).all()
    return render_template('notificaciones/fechas_importantes.html', fechas=fechas)


@notificaciones_bp.route('/fechas-importantes/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_fecha_importante(id):
    exigir_gestion()
    fecha = Feriado.query.get_or_404(id)
    db.session.delete(fecha)
    db.session.commit()
    flash('Fecha importante eliminada.', 'success')
    return redirect(url_for('notificaciones.fechas_importantes'))


@notificaciones_bp.route('/')
@login_required
def index():
    notificaciones = Notificacion.query.filter_by(usuario_id=current_user.id).order_by(
        Notificacion.creado_en.desc()
    ).all()
    return render_template('notificaciones/index.html', notificaciones=notificaciones)


@notificaciones_bp.route('/<int:id>/leer', methods=['POST'])
@login_required
def leer(id):
    notificacion = Notificacion.query.get_or_404(id)
    if notificacion.usuario_id != current_user.id:
        abort(403)
    if not notificacion.leida:
        notificacion.leida = True
        notificacion.leida_en = datetime.utcnow()
        db.session.commit()
    destinos = {
        'licencia': ('licencias.ver', {'id': notificacion.referencia_id}),
        'licencia_rrhh': ('licencias.ver', {'id': notificacion.referencia_id}),
        'documento': ('documentos.detalle', {'id': notificacion.referencia_id}),
        'documento_empleado': ('documentos.detalle', {'id': notificacion.referencia_id}),
        'noticia': ('noticias.muro', {}),
        'horas_extra': ('horas_extra.index', {}),
        'horas_extra_rrhh': ('horas_extra.index', {}),
        'recibo_sueldo': ('documentos.ver_recibo', {'id': notificacion.referencia_id}),
    }
    destino = destinos.get(notificacion.referencia_tipo)
    if destino:
        return redirect(url_for(destino[0], **destino[1]))
    return redirect(request.referrer or url_for('notificaciones.index'))


@notificaciones_bp.route('/leer-todas', methods=['POST'])
@login_required
def leer_todas():
    ahora = datetime.utcnow()
    Notificacion.query.filter_by(usuario_id=current_user.id, leida=False).update({
        Notificacion.leida: True,
        Notificacion.leida_en: ahora,
    }, synchronize_session=False)
    db.session.commit()
    flash('Notificaciones marcadas como leídas.', 'success')
    return redirect(url_for('notificaciones.index'))
