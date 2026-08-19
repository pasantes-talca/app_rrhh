"""Sincroniza los accesos del portal con los empleados de la base de datos."""

from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from database.models import Empleado, Rol, Usuario


CLAVE_TEMPORAL = "Talca2026"


def es_recursos_humanos(empleado):
    """Determina el rol a partir del sector actual del empleado."""
    if not empleado.sector:
        return False
    sector = empleado.sector.nombre.strip().lower()
    return sector in {"rrhh", "recursos humanos", "recursos_humanos"}


def sincronizar_usuarios():
    app = create_app()
    with app.app_context():
        rol_empleado = Rol.query.filter_by(nombre="empleado").first()
        rol_rrhh = Rol.query.filter_by(nombre="recursos_humanos").first()
        if not rol_empleado or not rol_rrhh:
            raise RuntimeError("Faltan los roles 'empleado' o 'recursos_humanos'. Ejecutá init_db.py primero.")

        creados = actualizados = omitidos = 0
        empleados = Empleado.query.order_by(Empleado.id).all()

        for empleado in empleados:
            legajo = (empleado.legajo or "").strip()
            if not legajo:
                print(f"OMITIDO: {empleado.nombre_apellido} no tiene legajo")
                omitidos += 1
                continue

            rol = rol_rrhh if es_recursos_humanos(empleado) else rol_empleado
            usuario = Usuario.query.filter_by(empleado_id=empleado.id).first()
            usuario_mismo_legajo = Usuario.query.filter_by(usuario=legajo).first()

            if usuario_mismo_legajo and usuario_mismo_legajo.empleado_id != empleado.id:
                print(f"OMITIDO: el usuario {legajo} ya pertenece a otra persona")
                omitidos += 1
                continue

            if usuario is None:
                usuario = Usuario(empleado_id=empleado.id, usuario=legajo, rol_id=rol.id)
                db.session.add(usuario)
                creados += 1
            else:
                usuario.usuario = legajo
                usuario.rol_id = rol.id
                actualizados += 1

            usuario.correo = empleado.correo or None
            usuario.password_hash = generate_password_hash(CLAVE_TEMPORAL)
            usuario.activo = empleado.estado is None or empleado.estado.strip().lower() == "activo"
            print(f"OK: {legajo} - {empleado.nombre_apellido} ({rol.nombre})")

        db.session.commit()
        print(f"\nResultado: {creados} creados, {actualizados} actualizados, {omitidos} omitidos.")
        print("Contraseña temporal asignada: Talca2026")


if __name__ == "__main__":
    sincronizar_usuarios()
