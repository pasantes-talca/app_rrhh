from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    if current_user.rol.nombre == 'administrador':
        return render_template('dashboard_admin.html')
    elif current_user.rol.nombre == 'recursos_humanos':
        return render_template('dashboard_rrhh.html')
    else:
        return render_template('dashboard_empleado.html')
