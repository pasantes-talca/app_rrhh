from datetime import datetime
from io import BytesIO
import re

import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.modules.licenses.models import LegacyEmployee
from .models import Overtime
from .rules import parse_hours, round_overtime


def _dataframe(content: bytes, filename: str) -> pd.DataFrame:
    lower = filename.lower()
    if lower.endswith(".csv"):
        return pd.read_csv(BytesIO(content))
    if lower.endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(content))
    soup = BeautifulSoup(content.decode("latin1", errors="replace").replace("\x00", ""), "html.parser")
    table = soup.find("table")
    if table is None:
        raise ValueError("No se encontró una tabla en el archivo")
    rows = [[cell.get_text(strip=True) for cell in row.find_all(["th", "td"])] for row in table.find_all("tr")]
    if len(rows) < 2:
        raise ValueError("La tabla no contiene registros")
    return pd.DataFrame(rows[1:], columns=rows[0])


def _date(value: object):
    text = str(value).strip()
    for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def import_report(session: Session, content: bytes, filename: str, user_id: int) -> tuple[int, int, list[str]]:
    frame = _dataframe(content, filename)
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    if "cuit" not in frame.columns or "fecha" not in frame.columns:
        raise ValueError("El archivo debe contener las columnas CUIT y Fecha")
    created = skipped = 0
    errors: list[str] = []
    for index, row in frame.iterrows():
        cuit = str(row.get("cuit", "")).strip()
        date_value = _date(row.get("fecha"))
        if not cuit or cuit == "nan" or date_value is None or "Totales" in cuit:
            skipped += 1; continue
        employee = session.scalar(select(LegacyEmployee).where(LegacyEmployee.cuil == cuit))
        if employee is None:
            match = re.search(r"\d{2}-(\d{7,8})-\d", cuit)
            if match:
                employee = session.scalar(select(LegacyEmployee).where(LegacyEmployee.document_number == match.group(1)))
        if employee is None and str(row.get("nombre", "")).strip() not in ("", "nan"):
            employee = session.scalar(select(LegacyEmployee).where(LegacyEmployee.display_name.ilike(f"%{str(row.get('nombre')).strip()}%")))
        if employee is None:
            errors.append(f"Fila {index + 2}: empleado no encontrado"); skipped += 1; continue
        entry = str(row.get("entradas", "")).replace("ds", "").strip()
        exit_value = str(row.get("salidas", "")).replace("ds", "").strip()
        if entry in ("", "nan", "Pendiente"):
            skipped += 1; continue
        try:
            time_from = datetime.strptime(entry, "%H:%M").time()
            time_to = datetime.strptime(exit_value, "%H:%M").time() if exit_value not in ("", "nan") else None
        except ValueError:
            errors.append(f"Fila {index + 2}: horario inválido"); skipped += 1; continue
        total = parse_hours(row.get("total hs", ""))
        hours = round_overtime(total - float(employee.workday_hours or 9)) if total else 0
        duplicate = session.scalar(select(Overtime).where(Overtime.employee_id == employee.id, Overtime.date == date_value, Overtime.time_from == time_from, Overtime.time_to == time_to))
        if duplicate:
            skipped += 1; continue
        session.add(Overtime(employee_id=employee.id, date=date_value, time_from=time_from, time_to=time_to, hours=hours, state="Pendiente", loaded_by=user_id, created_at=datetime.utcnow()))
        created += 1
    return created, skipped, errors[:50]
