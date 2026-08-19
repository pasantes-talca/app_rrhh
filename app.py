from flask import Flask, redirect, url_for, render_template
from flask_login import current_user
from config import Config
from extensions import db, login_manager
from database.models import Usuario

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Por favor, inicie sesión para acceder a esta página."

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Register blueprints
    from modules.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from modules.dashboard.routes import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from modules.empleados.routes import empleados_bp
    app.register_blueprint(empleados_bp)
    
    from modules.licencias.routes import licencias_bp
    app.register_blueprint(licencias_bp)
    
    from modules.horas_extra.routes import horas_extra_bp
    app.register_blueprint(horas_extra_bp)
    
    from modules.noticias.routes import noticias_bp
    app.register_blueprint(noticias_bp)
    
    from modules.documentos.routes import documentos_bp
    app.register_blueprint(documentos_bp)

    from modules.estructura.routes import estructura_bp
    app.register_blueprint(estructura_bp)

    from modules.sanciones.routes import sanciones_bp
    app.register_blueprint(sanciones_bp)

    from modules.notificaciones.routes import notificaciones_bp
    app.register_blueprint(notificaciones_bp)

    @app.context_processor
    def notificaciones_globales():
        if not current_user.is_authenticated:
            return {'notificaciones_no_leidas': 0, 'notificaciones_recientes': []}
        from database.models import Notificacion
        base = Notificacion.query.filter_by(usuario_id=current_user.id, leida=False)
        return {
            'notificaciones_no_leidas': base.count(),
            'notificaciones_recientes': base.order_by(Notificacion.creado_en.desc()).limit(5).all(),
        }
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
