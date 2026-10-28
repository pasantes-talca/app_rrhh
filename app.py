from datetime import datetime, timedelta
from flask import Flask, redirect, request, session, url_for
from flask_login import current_user, logout_user
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

    from modules.administracion.routes import administracion_bp
    app.register_blueprint(administracion_bp)

    @app.before_request
    def controles_acceso_y_sesion():
        if not current_user.is_authenticated:
            return None
        from database.models import ConfiguracionSistema, SesionUsuario
        from modules.administracion.security import MODULOS, accion_endpoint, tiene_permiso
        sesion_id = session.get('sesion_id')
        sesion_actual = SesionUsuario.query.get(sesion_id) if sesion_id else None
        if sesion_actual and sesion_actual.cerrada_en:
            logout_user(); session.clear()
            return redirect(url_for('auth.login'))
        if sesion_actual:
            limite = ConfiguracionSistema.query.get('session_max_minutes')
            minutos = int(limite.valor) if limite else 480
            if datetime.utcnow() - sesion_actual.ultima_actividad > timedelta(minutes=minutos):
                sesion_actual.cerrada_en = datetime.utcnow(); sesion_actual.motivo_cierre = 'Sesión vencida'
                db.session.commit(); logout_user(); session.clear()
                return redirect(url_for('auth.login'))
            sesion_actual.ultima_actividad = datetime.utcnow()
            db.session.commit()
        modulo = request.blueprint
        if modulo in MODULOS and not tiene_permiso(current_user, modulo, accion_endpoint(request.endpoint, request.method)):
            from flask import abort
            abort(403)

    @app.after_request
    def registrar_auditoria(response):
        if current_user.is_authenticated and request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            try:
                from database.models import Auditoria
                from modules.administracion.security import accion_endpoint
                ocultos = {'password', 'confirmar', 'csrf_token'}
                datos = ', '.join(f'{k}={v}' for k, v in request.form.items() if k not in ocultos)[:1500]
                db.session.add(Auditoria(usuario_id=current_user.id, usuario_nombre=current_user.usuario,
                    modulo=request.blueprint or 'sistema', accion=accion_endpoint(request.endpoint, request.method),
                    endpoint=request.endpoint, metodo=request.method, detalle=datos or None,
                    ip=request.headers.get('X-Forwarded-For', request.remote_addr), estado_http=response.status_code))
                db.session.commit()
            except Exception:
                db.session.rollback()
        return response

    @app.errorhandler(500)
    def registrar_error_interno(error):
        try:
            db.session.rollback()
            from database.models import ErrorSistema
            db.session.add(ErrorSistema(codigo=500, endpoint=request.endpoint, metodo=request.method,
                mensaje=str(getattr(error, 'original_exception', error))[:4000],
                usuario_id=current_user.id if current_user.is_authenticated else None,
                ip=request.headers.get('X-Forwarded-For', request.remote_addr)))
            db.session.commit()
        except Exception:
            db.session.rollback()
        return ('Ocurrió un error interno. La incidencia fue registrada para su revisión.', 500)

    @app.context_processor
    def notificaciones_globales():
        if not current_user.is_authenticated:
            return {'notificaciones_no_leidas': 0, 'notificaciones_recientes': []}
        from modules.notificaciones.services import (
            generar_notificaciones_cumpleanos,
            generar_notificaciones_fechas_importantes,
        )
        generar_notificaciones_cumpleanos()
        generar_notificaciones_fechas_importantes()
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
