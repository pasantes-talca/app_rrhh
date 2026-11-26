"""Importa de forma idempotente la planilla histórica de vacaciones."""
import argparse
import sys
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import openpyxl

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from app import create_app
from database.models import Empleado2, VacacionMovimiento, VacacionSaldo
from extensions import db
from modules.vacaciones.routes import _dias_por_antiguedad, _meses_antiguedad_al_cierre


def decimal(valor, default=Decimal('0')):
    try:
        return Decimal(str(valor)) if valor is not None else default
    except (InvalidOperation, ValueError):
        return default


def fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    return valor if isinstance(valor, date) else None


def importar(ruta, periodo):
    hoja = openpyxl.load_workbook(ruta, data_only=True, read_only=True)['Hoja1']
    filas_por_legajo = defaultdict(list)
    for numero_fila, valores in enumerate(hoja.iter_rows(min_row=2, values_only=True), 2):
        if valores[1] is None:
            continue
        filas_por_legajo[str(valores[1]).strip()].append((numero_fila, valores))

    todos_empleados = Empleado2.query.all()
    empleados = {
        str(item.numero_legajo).strip(): item
        for item in todos_empleados if item.numero_legajo is not None
    }
    faltantes = sorted(set(filas_por_legajo) - set(empleados))
    if faltantes:
        raise RuntimeError(f'Hay legajos del Excel sin vincular: {", ".join(faltantes)}')

    # Se crea saldo calculado para toda la nómina; los 118 saldos del Excel lo reemplazan.
    for empleado in todos_empleados:
        meses = _meses_antiguedad_al_cierre(empleado.fecha_ingreso, periodo)
        dias = Decimal(_dias_por_antiguedad(meses) or 0)
        saldo = VacacionSaldo.query.filter_by(empleado2_id=empleado.id, periodo=periodo).first()
        if not saldo:
            saldo = VacacionSaldo(empleado2_id=empleado.id, periodo=periodo)
            db.session.add(saldo)
        saldo.fecha_ingreso_calculo = empleado.fecha_ingreso
        saldo.antiguedad_meses = meses
        saldo.dias_correspondientes = dias
        if saldo.origen != 'EXCEL':
            saldo.saldo_base = dias
            saldo.saldo_disponible = dias + decimal(saldo.ajustes)
            saldo.origen = 'CALCULO'

    db.session.flush()
    movimientos_nuevos = 0
    for legajo, filas in filas_por_legajo.items():
        empleado = empleados[legajo]
        numero_ultima, ultima = filas[-1]
        saldo_excel = decimal(ultima[22])
        fechas = [fecha(item[1][c]) for item in filas for c in (18, 19, 20)]
        fechas = [item for item in fechas if item]
        saldo = VacacionSaldo.query.filter_by(empleado2_id=empleado.id, periodo=periodo).one()
        saldo.saldo_base = saldo_excel
        saldo.saldo_disponible = saldo_excel + decimal(saldo.ajustes)
        saldo.origen = 'EXCEL'
        saldo.fila_excel = numero_ultima
        saldo.fecha_corte = max(fechas) if fechas else None
        saldo.observaciones = str(ultima[23] or ultima[24] or '').strip() or None

        for numero_fila, valores in filas:
            referencia = f'NOTIFICACION_VACACIONES_TALCA:{numero_fila}'
            if VacacionMovimiento.query.filter_by(origen='EXCEL', referencia_origen=referencia).first():
                continue
            db.session.add(VacacionMovimiento(
                empleado2_id=empleado.id,
                saldo=saldo,
                tipo='HISTORICO_IMPORTADO',
                fecha_desde=fecha(valores[18]),
                fecha_hasta=fecha(valores[19]),
                fecha_reintegro=fecha(valores[20]),
                dias=decimal(valores[21]),
                saldo_resultante=decimal(valores[22], None),
                detalle=str(valores[4] or '').strip() or None,
                observaciones=' | '.join(str(x).strip() for x in (valores[5], valores[23], valores[24]) if x),
                origen='EXCEL',
                referencia_origen=referencia,
            ))
            movimientos_nuevos += 1

    db.session.commit()
    return len(todos_empleados), len(filas_por_legajo), movimientos_nuevos


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('archivo')
    parser.add_argument('--periodo', type=int, default=date.today().year)
    args = parser.parse_args()
    app = create_app()
    with app.app_context():
        total, importados, movimientos = importar(args.archivo, args.periodo)
        print(f'Saldos generados: {total}; saldos desde Excel: {importados}; movimientos nuevos: {movimientos}')
