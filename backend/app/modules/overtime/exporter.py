from collections import defaultdict
from io import BytesIO
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.communications.models import ImportantDate
from .models import Company, Overtime, Sector
from .rules import day_type


def export_workbook(session: Session, records: list[Overtime]) -> BytesIO:
    template = get_settings().overtime_template
    workbook = load_workbook(template) if template.is_file() else Workbook()
    sheet = workbook.active
    if not template.is_file():
        sheet.append(["Empresa", "Sector", "CUIL/DNI", "Empleado", "Dom/Fer", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Feriado", "Subtotal LAV", "Subtotal Sáb", "Subtotal Dom/Fer", "Total"])
    holidays = set(session.scalars(select(ImportantDate.date)).all())
    by_employee: defaultdict[int, list[Overtime]] = defaultdict(list)
    for record in records:
        by_employee[record.employee_id].append(record)
    day_column = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 5}
    row_index = 7 if template.is_file() else 2
    for employee_records in by_employee.values():
        employee = employee_records[0].employee
        company = session.get(Company, employee.company_id) if employee.company_id else None
        sector = session.get(Sector, employee.sector_id) if employee.sector_id else None
        totals = {"LAV": 0.0, "SAB": 0.0, "DOM_FER": 0.0}
        columns: defaultdict[int, float] = defaultdict(float)
        for record in employee_records:
            hours = float(record.hours or 0)
            if hours <= 0:
                continue
            kind = day_type(record.date, holidays)
            totals[kind] += hours
            column = 5 if kind == "DOM_FER" and record.date.weekday() == 6 else 12 if kind == "DOM_FER" else day_column[record.date.weekday()]
            columns[column] += hours
            if template.is_file():
                sheet.cell(row=4, column=day_column[record.date.weekday()], value=record.date.strftime("%d/%m/%y"))
        if sum(totals.values()) <= 0:
            continue
        sheet.cell(row=row_index, column=1, value=company.name if company else "").alignment = Alignment(horizontal="center")
        sheet.cell(row=row_index, column=2, value=sector.name if sector else "").alignment = Alignment(horizontal="center")
        sheet.cell(row=row_index, column=3, value=employee.cuil or employee.document_number).alignment = Alignment(horizontal="center")
        sheet.cell(row=row_index, column=4, value=employee.display_name)
        for column, hours in columns.items():
            sheet.cell(row=row_index, column=column, value=hours).alignment = Alignment(horizontal="center")
        rates = {"LAV": float(company.weekday_rate or 0) if company else 0, "SAB": float(company.saturday_rate or 0) if company else 0, "DOM_FER": float(company.sunday_holiday_rate or 0) if company else 0}
        subtotals = {key: totals[key] * rates[key] for key in totals}
        for column, key in ((13, "LAV"), (14, "SAB"), (15, "DOM_FER")):
            if subtotals[key] > 0:
                sheet.cell(row=row_index, column=column, value=subtotals[key])
        total = sum(subtotals.values())
        if total > 0:
            sheet.cell(row=row_index, column=16, value=total)
            if template.is_file():
                sheet.cell(row=row_index, column=18, value=total)
        row_index += 1
    output = BytesIO(); workbook.save(output); output.seek(0)
    return output
