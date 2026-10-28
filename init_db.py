import os
from werkzeug.security import generate_password_hash
from app import create_app
from extensions import db
from sqlalchemy import text
from database.models import (
    Rol, Empresa, Sector, Puesto, Jornada, TipoLicencia, TipoDocumento, Usuario, Empleado
)

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database_and_schema(app):
    with app.app_context():
        db_name = app.config['DB_NAME']
        db_user = app.config['DB_USER']
        db_password = app.config['DB_PASSWORD']
        db_host = app.config['DB_HOST']
        db_port = app.config['DB_PORT']
        # The schema is hardcoded in models, so we create 'rrhh'
        db_schema = 'rrhh'
        
        try:
            # Conectar a postgres por defecto para crear la BD si no existe
            conn = psycopg2.connect(dbname='postgres', user=db_user, password=db_password, host=db_host, port=db_port)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
            if not cur.fetchone():
                print(f"Creando base de datos {db_name}...")
                cur.execute(f"CREATE DATABASE {db_name}")
            cur.close()
            conn.close()

            # Conectar a la nueva BD para crear el esquema
            conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {db_schema}")
            print(f"Esquema {db_schema} creado/verificado.")
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error al verificar la base de datos/esquema: {e}")

def init_db():
    app = create_app()
    # Asegurar que la DB y el esquema existan antes de que SQLAlchemy intente crear las tablas
    create_database_and_schema(app)
    
    with app.app_context():
        print("Creando tablas...")
        db.create_all()
        # db.create_all no agrega columnas a tablas existentes.
        db.session.execute(text("ALTER TABLE rrhh.usuarios ADD COLUMN IF NOT EXISTS nombre_mostrar VARCHAR(150)"))
        db.session.execute(text("ALTER TABLE rrhh.usuarios ADD COLUMN IF NOT EXISTS foto_perfil VARCHAR(255)"))
        db.session.execute(text("ALTER TABLE rrhh.usuarios ADD COLUMN IF NOT EXISTS cuenta_protegida BOOLEAN NOT NULL DEFAULT FALSE"))
        db.session.execute(text("""
            UPDATE rrhh.usuarios u SET cuenta_protegida = TRUE
            FROM rrhh.roles r WHERE u.rol_id = r.id AND r.nombre = 'administrador'
        """))
        db.session.commit()

        print("Insertando datos iniciales...")

        # 1. Roles
        roles_data = [
            {'nombre': 'administrador', 'descripcion': 'Acceso total al sistema'},
            {'nombre': 'recursos_humanos', 'descripcion': 'Gestión operativa de recursos humanos'},
            {'nombre': 'empleado', 'descripcion': 'Acceso limitado del empleado'}
        ]
        for r_data in roles_data:
            if not Rol.query.filter_by(nombre=r_data['nombre']).first():
                db.session.add(Rol(**r_data))

        # 2. Empresas
        empresas = ['Oeste', 'Consultora']
        for emp in empresas:
            if not Empresa.query.filter_by(nombre=emp).first():
                db.session.add(Empresa(nombre=emp))

        # 3. Sectores
        sectores = ['Soplado', 'Mantenimiento', 'Laboratorio', 'Administración', 
                    'Producción', 'Depósito', 'Calidad', 'Logística', 'RRHH']
        for sec in sectores:
            if not Sector.query.filter_by(nombre=sec).first():
                db.session.add(Sector(nombre=sec))

        # 4. Puestos
        puestos = ['Operario', 'Supervisor', 'Técnico de mantenimiento', 
                   'Analista de laboratorio', 'Administrativo', 'Encargado', 'Jefe de sector']
        for pue in puestos:
            if not Puesto.query.filter_by(nombre=pue).first():
                db.session.add(Puesto(nombre=pue))

        # 5. Jornadas
        jornadas = ['Turno mañana', 'Turno tarde', 'Turno noche', 'Turno rotativo', 
                    'Jornada administrativa', 'Media jornada']
        for jor in jornadas:
            if not Jornada.query.filter_by(nombre=jor).first():
                db.session.add(Jornada(nombre=jor))

        # 6. Tipos de Licencia
        tipos_licencia = [
            {'nombre': 'Vacaciones', 'descripcion': 'Licencia por vacaciones'},
            {'nombre': 'Enfermedad', 'descripcion': 'Licencia por enfermedad'},
            {'nombre': 'Accidente', 'descripcion': 'Licencia por accidente'},
            {'nombre': 'Maternidad', 'descripcion': 'Licencia por maternidad'},
            {'nombre': 'Paternidad', 'descripcion': 'Licencia por paternidad'},
            {'nombre': 'Día particular', 'descripcion': 'Día particular'},
            {'nombre': 'Estudio', 'descripcion': 'Licencia por estudio'},
            {'nombre': 'Fallecimiento familiar', 'descripcion': 'Licencia por fallecimiento familiar'},
            {'nombre': 'Mudanza', 'descripcion': 'Licencia por mudanza'},
            {'nombre': 'Licencia sin goce de sueldo', 'descripcion': 'Licencia sin goce de sueldo'},
            {'nombre': 'Otra', 'descripcion': 'Otro tipo de licencia'}
        ]
        for tl in tipos_licencia:
            if not TipoLicencia.query.filter_by(nombre=tl['nombre']).first():
                db.session.add(TipoLicencia(**tl))

        # 7. Tipos de Documentos
        tipos_doc = [
            {'nombre': 'Recibo de sueldo', 'descripcion': 'Recibo de sueldo del empleado'},
            {'nombre': 'Certificado laboral', 'descripcion': 'Certificado laboral'},
            {'nombre': 'Constancia de CUIL', 'descripcion': 'Constancia de CUIL'},
            {'nombre': 'DNI', 'descripcion': 'Documento Nacional de Identidad'},
            {'nombre': 'Contrato', 'descripcion': 'Contrato laboral'},
            {'nombre': 'Apto médico', 'descripcion': 'Apto médico'},
            {'nombre': 'Sanción', 'descripcion': 'Sanción disciplinaria'},
            {'nombre': 'Formulario interno', 'descripcion': 'Formulario interno de RRHH'},
            {'nombre': 'Certificado de capacitación', 'descripcion': 'Certificado de capacitación'},
            {'nombre': 'Otro', 'descripcion': 'Otro tipo de documento'}
        ]
        for td in tipos_doc:
            if not TipoDocumento.query.filter_by(nombre=td['nombre']).first():
                db.session.add(TipoDocumento(**td))

        db.session.commit()

        # Calendario base de feriados nacionales y provinciales de Mendoza.
        # Luego puede administrarse desde el panel de RR. HH.
        from modules.notificaciones.services import sincronizar_calendario_mendoza_2026
        sincronizar_calendario_mendoza_2026()

        # 8. Administrador inicial
        admin_rol = Rol.query.filter_by(nombre='administrador').first()
        if admin_rol:
            if not Usuario.query.filter_by(usuario='admin').first():
                # Crear un empleado ficticio para el admin o dejar empleado_id nulo
                # Como empleado_id es opcional según el modelo (nullable=True implícito)
                admin_user = Usuario(
                    rol_id=admin_rol.id,
                    usuario='admin',
                    correo='admin@talca.com',
                    password_hash=generate_password_hash('admin123')
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Usuario administrador creado (admin / admin123). ¡Recuerda cambiar la contraseña!")

        print("Inicialización completada.")

if __name__ == '__main__':
    init_db()
