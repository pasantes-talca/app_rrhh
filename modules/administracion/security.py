from functools import wraps
from flask import abort
from flask_login import current_user

MODULOS = {
    'dashboard': 'Panel de control', 'empleados': 'Empleados', 'licencias': 'Licencias',
    'horas_extra': 'Horas extra', 'sanciones': 'Sanciones', 'noticias': 'Noticias',
    'documentos': 'Documentos', 'estructura': 'Estructura', 'notificaciones': 'Notificaciones',
}
ACCIONES = ('consultar', 'crear', 'editar', 'anular', 'exportar', 'configurar')


def es_administrador():
    return current_user.is_authenticated and current_user.rol and current_user.rol.nombre == 'administrador'


def solo_administrador(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not es_administrador():
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def accion_endpoint(endpoint, method):
    nombre = (endpoint or '').split('.')[-1]
    if nombre in ('exportar', 'descargar'):
        return 'exportar'
    if method == 'DELETE' or nombre in ('eliminar', 'vaciar', 'cambiar_estado'):
        return 'anular'
    if method in ('POST', 'PUT', 'PATCH'):
        return 'editar' if nombre in ('editar', 'resolver', 'ver') else 'crear'
    return 'consultar'


def tiene_permiso(usuario, modulo, accion):
    if usuario.rol and usuario.rol.nombre == 'administrador':
        return True
    # Sin configuración individual se conservan los permisos de rol existentes.
    if not usuario.permisos:
        return True
    permiso = next((p for p in usuario.permisos if p.modulo == modulo and p.accion == accion), None)
    return bool(permiso and permiso.permitido)
