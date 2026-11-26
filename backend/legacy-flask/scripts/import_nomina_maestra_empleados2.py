import argparse
import hashlib
import json
import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from openpyxl import load_workbook

from app import create_app
from database.models import Empleado2
from extensions import db


FIELD_MAP = {
    "nombre completo": "nombre_completo", "nombre": "nombre", "apellido": "apellido",
    "dni": "numero_documento", "cuil": "cuil", "sexo o genero": "sexo",
    "nacionalidad": "nacionalidad", "fecha de nacimiento": "fecha_nacimiento",
    "estado civil": "codigo_estado_civil", "nivel de estudios": "nivel_estudios",
    "grupo sanguineo": "grupo_sanguineo", "pasaporte": "pasaporte",
    "telefono principal": "telefono", "telefono alternativo 1": "telefono_alternativo",
    "telefono alternativo 2": "telefono_otro", "telefono laboral": "telefono_laboral",
    "correo electronico principal": "correo", "correo electronico alternativo": "correo_alternativo",
    "domicilio o direccion": "domicilio", "barrio": "barrio", "departamento": "numero_departamento",
    "manzana": "manzana", "torre": "torre", "piso": "piso", "pais": "pais",
    "provincia": "provincia", "localidad": "localidad", "codigo postal": "codigo_postal",
    "numero de legajo": "numero_legajo", "fecha de ingreso": "fecha_ingreso",
    "fecha de egreso": "fecha_egreso", "fecha de efectivizacion": "fecha_efectivizacion",
    "antiguedad registrada": "antiguedad_registrada", "categoria laboral": "categoria_laboral",
    "codigo de categoria": "codigo_categoria", "contrato": "contrato",
    "jornada laboral": "jornada_laboral", "horas de jornada": "horas_jornada",
    "horas normales": "horas_normales", "horas extras": "horas_extra",
    "situacion laboral": "situacion_laboral", "estado del empleado": "estado",
    "empresa": "empresa", "departamento o area": "departamento_area", "sector": "sector",
    "puesto": "puesto", "rol": "rol_laboral", "supervisor": "supervisor",
    "ubicacion principal": "ubicacion_principal", "gremio": "gremio",
    "movilidad del empleado": "movilidad_empleado", "licencia de conducir": "licencia_conducir",
    "sueldo": "sueldo", "banco": "banco", "cuenta bancaria": "cuenta_bancaria",
    "cbu": "cbu", "alias bancario": "alias_bancario", "moneda": "moneda",
    "forma de pago": "forma_pago", "obra social": "obra_social",
    "indicador de jubilado": "indicador_jubilado",
    "nombre del contacto de emergencia": "contacto_emergencia_nombre",
    "telefono del contacto de emergencia": "contacto_emergencia_telefono",
    "correo electronico del contacto de emergencia": "contacto_emergencia_correo",
    "dni del contacto de emergencia": "contacto_emergencia_dni", "marcacion web": "marcacion_web",
    "acceso a plataforma web": "acceso_plataforma_web", "id del usuario en trilay": "id_usuario",
    "id de datoempleado en trilay": "codigo_dato_empleado",
    "id del empleado en postgresql": "id_empleado_postgresql",
    "codigo de usuario trilay": "cod_usuario", "fuentes en las que aparece el empleado": "fuentes_origen",
    "cantidad de fuentes coincidentes": "cantidad_fuentes",
    "referencia de las filas originales": "nomina_referencia",
    "estado de vinculacion": "estado_vinculacion",
    "cantidad de conflictos de datos": "cantidad_conflictos",
    "observaciones de integracion": "observaciones_integracion",
}
DATE_FIELDS = {"fecha_nacimiento", "fecha_ingreso", "fecha_egreso", "fecha_efectivizacion"}
INTEGER_FIELDS = {"codigo_estado_civil", "estado", "id_usuario", "codigo_dato_empleado", "id_empleado_postgresql", "cantidad_fuentes", "cantidad_conflictos"}
DECIMAL_FIELDS = {"horas_jornada", "horas_normales", "horas_extra", "sueldo"}
BOOLEAN_FIELDS = {"indicador_jubilado", "marcacion_web", "acceso_plataforma_web"}


def normalize_header(value):
    value = "".join(c for c in unicodedata.normalize("NFD", str(value)) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def clean_text(value):
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    result = str(value).strip()
    return result or None


def clean_date(value):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None


def clean_integer(value):
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def clean_decimal(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


def clean_boolean(value):
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "si", "sí", "s", "yes"}


def prefer_trilay_value(value):
    """En conflictos consolidados elige el valor del segmento cuya fuente incluye Trilay."""
    if not isinstance(value, str) or "trilay" not in value.lower():
        return value
    for segment in value.split(";"):
        if ":" not in segment:
            continue
        sources, source_value = segment.split(":", 1)
        if "trilay" in sources.lower():
            return source_value.strip() or None
    return value


def converted(field, value):
    value = prefer_trilay_value(value)
    if field in DATE_FIELDS:
        return clean_date(value)
    if field in INTEGER_FIELDS:
        return clean_integer(value)
    if field in DECIMAL_FIELDS:
        return clean_decimal(value)
    if field in BOOLEAN_FIELDS:
        return clean_boolean(value)
    return clean_text(value)


def import_workbook(path):
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet_name = next((name for name in workbook.sheetnames if name.strip().lower() == "empleados por dni"), None)
    if not sheet_name:
        raise ValueError("No se encontro la hoja empleados por dni")
    sheet = workbook[sheet_name]
    source_headers = [cell.value for cell in sheet[1]]
    mapped_headers = {}
    for index, header in enumerate(source_headers):
        normalized = normalize_header(header or "")
        if normalized in FIELD_MAP:
            mapped_headers[index] = FIELD_MAP[normalized]
    missing = set(FIELD_MAP.values()) - set(mapped_headers.values())
    if missing:
        raise ValueError(f"Faltan columnas esperadas: {', '.join(sorted(missing))}")

    created = updated = skipped = 0
    now = datetime.utcnow()
    for row_number, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        if not any(value is not None and str(value).strip() for value in row):
            continue
        payload = {field: converted(field, row[index]) for index, field in mapped_headers.items()}
        reference = payload.get("nomina_referencia")
        if not reference:
            skipped += 1
            continue
        employee = None
        if payload.get("id_usuario") is not None:
            employee = Empleado2.query.filter_by(id_usuario=payload["id_usuario"]).first()
        if employee is None:
            employee = Empleado2.query.filter_by(nomina_referencia=reference).first()
        is_new = employee is None
        if is_new:
            employee = Empleado2(
                huella_origen=hashlib.sha256(reference.encode("utf-8")).hexdigest(),
                presente_en_origen=payload.get("id_usuario") is not None,
                ultima_sincronizacion=now,
            )
            db.session.add(employee)
        for field, value in payload.items():
            setattr(employee, field, value)
        employee.nombre_completo = employee.nombre_completo or f'{employee.nombre or ""} {employee.apellido or ""}'.strip() or None
        employee.origen_nomina = True
        employee.nomina_actualizada_en = now
        # Fuerza a la proxima consulta de Trilay a refrescar sus campos autorizados.
        employee.huella_origen = hashlib.sha256(json.dumps(payload, default=str, sort_keys=True).encode("utf-8")).hexdigest()
        if payload.get("id_usuario") is None:
            employee.presente_en_origen = False
        created += is_new
        updated += not is_new
        if row_number % 100 == 0:
            db.session.flush()
    db.session.commit()
    return {"creados": created, "actualizados": updated, "omitidos": skipped}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archivo")
    args = parser.parse_args()
    app = create_app()
    with app.app_context():
        try:
            print(import_workbook(args.archivo))
        except Exception:
            db.session.rollback()
            raise


if __name__ == "__main__":
    main()
