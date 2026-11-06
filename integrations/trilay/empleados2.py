import hashlib
import json
from datetime import datetime
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert
from werkzeug.security import generate_password_hash

from database.models import Empleado, Empleado2, Rol, Usuario
from extensions import db


# Lista explicita: nunca SELECT *. Se omiten credenciales, autenticacion, IP,
# sueldo, cuentas, bancos, tarjetas y campos tecnicos o de liquidacion.
SOURCE_COLUMNS = {
    "codUsuario": "cod_usuario",
    "telefono": "telefono",
    "telefono1": "telefono_alternativo",
    "telefono2": "telefono_otro",
    "email": "correo",
    "email1": "correo_alternativo",
    "tipoDoc": "tipo_documento",
    "numeroDoc": "numero_documento",
    "sexo": "sexo",
    "idUsuario": "id_usuario",
    "Nivel": "nivel",
    "NumeroNivel": "numero_nivel",
    "nombre": "nombre",
    "apellido": "apellido",
    "codJerarquiaSuperior": "codigo_jerarquia_superior",
    "nroLegajo": "numero_legajo",
    "estadoSalud": "estado_salud",
    "codDatoEmpleado": "codigo_dato_empleado",
    "cuil": "cuil",
    "nroJubilacion": "numero_jubilacion",
    "foto": "foto",
    "estado": "estado",
    "razon": "razon",
    "nacionalidad": "nacionalidad",
    "fechanacimiento": "fecha_nacimiento",
    "fechaingreso": "fecha_ingreso",
    "fechaegreso": "fecha_egreso",
    "codestadocivil": "codigo_estado_civil",
    "calle": "calle",
    "casaNro": "numero_casa",
    "departamentoNro": "numero_departamento",
    "manzana": "manzana",
    "barrio": "barrio",
    "torre": "torre",
    "piso": "piso",
    "pais": "pais",
    "localidad": "localidad",
    "provincia": "provincia",
    "telefonolaboral": "telefono_laboral",
    "horasextras": "horas_extra",
    "horasNormales": "horas_normales",
    "codJerarquia": "codigo_jerarquia",
    "codPais": "codigo_pais",
    "codtipodoc": "codigo_tipo_documento",
    "nombredoc": "nombre_documento",
    "curp": "curp",
    "nrosegurosocial": "numero_seguro_social",
    "fechaefectivo": "fecha_efectivizacion",
    "codLocalidad": "codigo_localidad",
    "codProvincia": "codigo_provincia",
    "JerarquiaPadre": "jerarquia_padre",
}

DATE_FIELDS = {"fecha_nacimiento", "fecha_ingreso", "fecha_egreso", "fecha_efectivizacion"}
TEMPORARY_PASSWORD = "Talca2026"


def _source_engine(config):
    connection = (
        f'DRIVER={{{config["TRILAY_SQLSERVER_DRIVER"]}}};'
        f'SERVER={config["TRILAY_SQLSERVER_HOST"]},{config["TRILAY_SQLSERVER_PORT"]};'
        f'DATABASE={config["TRILAY_SQLSERVER_DATABASE"]};'
        f'UID={config["TRILAY_SQLSERVER_USER"]};PWD={config["TRILAY_SQLSERVER_PASSWORD"]};'
        f'Encrypt={config["TRILAY_SQLSERVER_ENCRYPT"]};'
        f'TrustServerCertificate={config["TRILAY_SQLSERVER_TRUST_CERTIFICATE"]};'
        'ApplicationIntent=ReadOnly;'
    )
    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={quote_plus(connection)}",
        pool_pre_ping=True,
        connect_args={"timeout": 15},
    )


def _text(value, maximum=None):
    if value is None:
        return None
    cleaned = " ".join(str(value).strip().split())
    if not cleaned:
        return None
    return cleaned[:maximum] if maximum else cleaned


def _date(value):
    value = _text(value)
    if not value:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _normalize(row):
    result = {target: row.get(source) for source, target in SOURCE_COLUMNS.items()}
    if result["id_usuario"] is None:
        raise ValueError("Registro sin idUsuario")
    for field in DATE_FIELDS:
        result[field] = _date(result[field])
    for field, value in tuple(result.items()):
        if field not in DATE_FIELDS and isinstance(value, str):
            result[field] = _text(value)
    fingerprint_payload = json.dumps(result, default=str, sort_keys=True, ensure_ascii=False)
    result["huella_origen"] = hashlib.sha256(fingerprint_payload.encode("utf-8")).hexdigest()
    return result


def fetch_trilay(config):
    columns = ", ".join(f"[{column}]" for column in SOURCE_COLUMNS)
    statement = text(f"SELECT {columns} FROM [dbo].[Usuario]")
    engine = _source_engine(config)
    try:
        with engine.connect() as connection:
            return [_normalize(dict(row)) for row in connection.execute(statement).mappings()]
    finally:
        engine.dispose()


def sync_empleados2(config):
    records = fetch_trilay(config)
    now = datetime.utcnow()
    table = Empleado2.__table__
    source_ids = [record["id_usuario"] for record in records]
    inserted_or_updated = 0
    unchanged = 0

    # El advisory lock evita dos workers simultaneos.
    locked = db.session.execute(text("SELECT pg_try_advisory_lock(72420262)")).scalar()
    if not locked:
        raise RuntimeError("Ya existe una sincronizacion de empleados2 en curso")
    try:
        current = {row.id_usuario: row.huella_origen for row in Empleado2.query.filter(Empleado2.id_usuario.isnot(None)).all()}
        for record in records:
            if current.get(record["id_usuario"]) == record["huella_origen"]:
                unchanged += 1
                continue
            payload = {**record, "presente_en_origen": True, "ultima_sincronizacion": now}
            statement = insert(table).values(**payload)
            update_values = {
                column: getattr(statement.excluded, column)
                for column in payload
                if column != "id_usuario"
            }
            db.session.execute(statement.on_conflict_do_update(
                index_elements=[table.c.id_usuario], set_=update_values,
            ))
            inserted_or_updated += 1
        if source_ids:
            Empleado2.query.filter(Empleado2.id_usuario.isnot(None), ~Empleado2.id_usuario.in_(source_ids)).update(
                {Empleado2.presente_en_origen: False}, synchronize_session=False,
            )
        db.session.flush()
        account_result = ensure_employee2_accounts()
        db.session.commit()
        return {
            "consultados": len(records),
            "insertados_o_actualizados": inserted_or_updated,
            "sin_cambios": unchanged,
            **account_result,
        }
    except Exception:
        db.session.rollback()
        raise
    finally:
        db.session.execute(text("SELECT pg_advisory_unlock(72420262)"))
        db.session.commit()


def ensure_employee2_accounts(reset_new_links=True):
    """Crea o vincula cuentas de empleado sin alterar cuentas administrativas/RR. HH."""
    role = Rol.query.filter_by(nombre="empleado").one()
    employee_rows = Empleado.query.all()
    identity_maps = {}
    for source_field, local_field in (("numero_documento", "dni"), ("cuil", "cuil"), ("numero_legajo", "legajo")):
        values = {}
        for employee in employee_rows:
            value = _text(getattr(employee, local_field))
            if value:
                values.setdefault(value, set()).add(employee.id)
        identity_maps[source_field] = values

    employee_users = {
        user.empleado_id: user for user in Usuario.query.filter(
            Usuario.rol_id == role.id, Usuario.empleado_id.isnot(None)
        ).all()
    }
    by_employee2 = {user.empleado2_id: user for user in Usuario.query.filter(Usuario.empleado2_id.isnot(None)).all()}
    for linked_user in by_employee2.values():
        if linked_user.empleado_id:
            employee_users.pop(linked_user.empleado_id, None)
    usernames = {user.usuario.lower(): user.id for user in Usuario.query.all()}
    created = linked = renamed = 0

    for source_employee in Empleado2.query.filter_by(presente_en_origen=True).all():
        username = _text(source_employee.cod_usuario)
        if not username:
            continue
        user = by_employee2.get(source_employee.id)
        if user is None:
            candidates = set()
            for source_field in ("numero_documento", "cuil", "numero_legajo"):
                value = _text(getattr(source_employee, source_field))
                if value:
                    candidates.update(identity_maps[source_field].get(value, set()))
            user = employee_users.get(next(iter(candidates))) if len(candidates) == 1 else None
            if user:
                employee_users.pop(user.empleado_id, None)
                user.empleado2_id = source_employee.id
                by_employee2[source_employee.id] = user
                linked += 1
            else:
                user = Usuario(
                    empleado2_id=source_employee.id,
                    rol_id=role.id,
                    usuario=username,
                    nombre_mostrar=f'{source_employee.nombre or ""} {source_employee.apellido or ""}'.strip() or username,
                    password_hash=generate_password_hash(TEMPORARY_PASSWORD),
                    debe_cambiar_password=True,
                    activo=True,
                )
                db.session.add(user)
                db.session.flush()
                by_employee2[source_employee.id] = user
                usernames[username.lower()] = user.id
                created += 1
                continue
            if reset_new_links:
                user.password_hash = generate_password_hash(TEMPORARY_PASSWORD)
                user.debe_cambiar_password = True

        owner_id = usernames.get(username.lower())
        if owner_id in (None, user.id) and user.usuario != username:
            usernames.pop(user.usuario.lower(), None)
            user.usuario = username
            usernames[username.lower()] = user.id
            renamed += 1
        if not user.nombre_mostrar:
            user.nombre_mostrar = f'{source_employee.nombre or ""} {source_employee.apellido or ""}'.strip() or username

    return {"cuentas_creadas": created, "cuentas_vinculadas": linked, "usuarios_actualizados": renamed}
