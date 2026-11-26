"""Exporta empleados de Trilay separados por estado, sin incluir contraseñas."""
import sys
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from app import create_app
from integrations.trilay.empleados2 import SOURCE_COLUMNS, _source_engine
from sqlalchemy import text


def valor_texto(valor):
    return '' if valor is None else str(valor).strip()


def registro_completo(registro):
    nombre = valor_texto(registro.get('nombre'))
    apellido = valor_texto(registro.get('apellido'))
    dni = ''.join(c for c in valor_texto(registro.get('numeroDoc')) if c.isdigit())
    legajo = valor_texto(registro.get('nroLegajo'))
    return (
        bool(nombre and apellido)
        and len(dni) in (7, 8)
        and bool(legajo and legajo.strip('0'))
    )


def preparar_valor(valor):
    if isinstance(valor, (datetime, date)):
        return valor
    return valor


def agregar_hoja(libro, titulo, registros, columnas):
    hoja = libro.create_sheet(titulo)
    encabezados = [destino.replace('_', ' ').title() for _, destino in columnas]
    hoja.append(encabezados)
    for registro in registros:
        hoja.append([preparar_valor(registro.get(origen)) for origen, _ in columnas])

    rojo = 'E31E24'
    for celda in hoja[1]:
        celda.fill = PatternFill('solid', fgColor=rojo)
        celda.font = Font(color='FFFFFF', bold=True)
        celda.alignment = Alignment(horizontal='center', vertical='center')
    hoja.freeze_panes = 'A2'
    hoja.auto_filter.ref = hoja.dimensions
    hoja.sheet_view.showGridLines = False
    if hoja.max_row > 1:
        tabla = Table(displayName='Tabla' + ''.join(c for c in titulo if c.isalnum()), ref=hoja.dimensions)
        tabla.tableStyleInfo = TableStyleInfo(
            name='TableStyleMedium2', showFirstColumn=False,
            showLastColumn=False, showRowStripes=True, showColumnStripes=False,
        )
        hoja.add_table(tabla)
    for columna in hoja.columns:
        largo = max(len(valor_texto(celda.value)) for celda in columna)
        hoja.column_dimensions[columna[0].column_letter].width = min(max(largo + 2, 12), 35)


def exportar(destino):
    app = create_app()
    columnas = list(SOURCE_COLUMNS.items())
    nombres_sql = ', '.join(f'[{origen}]' for origen, _ in columnas)
    consulta = text(f'SELECT {nombres_sql} FROM [dbo].[Usuario] ORDER BY [apellido], [nombre]')
    with app.app_context():
        motor = _source_engine(app.config)
        try:
            with motor.connect() as conexion:
                registros = [dict(fila) for fila in conexion.execute(consulta).mappings()]
        finally:
            motor.dispose()

    activos = [r for r in registros if r.get('estado') == 0]
    desvinculados = [r for r in registros if r.get('estado') == 1]
    libro = Workbook()
    libro.remove(libro.active)
    agregar_hoja(libro, 'Activos', activos, columnas)
    agregar_hoja(libro, 'Desvinculados', desvinculados, columnas)
    agregar_hoja(libro, 'Activos completos', [r for r in activos if registro_completo(r)], columnas)
    agregar_hoja(libro, 'Desvinculados completos', [r for r in desvinculados if registro_completo(r)], columnas)
    libro.save(destino)
    return len(activos), len(desvinculados), sum(map(registro_completo, activos)), sum(map(registro_completo, desvinculados))


if __name__ == '__main__':
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / 'empleados_por_estado_trilay.xlsx'
    conteos = exportar(destino)
    print(f'Archivo: {destino.resolve()}')
    print(f'Activos={conteos[0]}; Desvinculados={conteos[1]}; Activos completos={conteos[2]}; Desvinculados completos={conteos[3]}')
