from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from database.models import Notificacion
from extensions import db

notificaciones_bp = Blueprint('notificaciones', __name__, url_prefix='/notificaciones')


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
