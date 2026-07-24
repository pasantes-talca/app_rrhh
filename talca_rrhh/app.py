from flask import Flask, redirect, url_for, render_template
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
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
