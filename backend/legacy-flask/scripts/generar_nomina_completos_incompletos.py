"""Separa la nómina maestra según presencia de nombre, apellido, DNI y legajo."""
import argparse
import unicodedata
from pathlib import Path

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


def tiene_dato(valor):
    return valor is not None and str(valor).strip() != ''


def normalizar_encabezado(valor):
    texto = '' if valor is None else str(valor).strip().lower()
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode()


def preparar_hoja(hoja, color):
    hoja.freeze_panes = 'A2'
    hoja.auto_filter.ref = hoja.dimensions
    hoja.sheet_view.showGridLines = False
    hoja.row_dimensions[1].height = 28
    relleno = PatternFill('solid', fgColor=color)
    for celda in hoja[1]:
        celda.fill = relleno
        celda.font = Font(color='FFFFFF', bold=True)
        celda.alignment = Alignment(vertical='center')
    for columna in range(1, hoja.max_column + 1):
        valores = [
            '' if hoja.cell(fila, columna).value is None else str(hoja.cell(fila, columna).value)
            for fila in range(1, min(hoja.max_row, 120) + 1)
        ]
        ancho = min(max(max((len(valor) for valor in valores), default=8) + 2, 12), 35)
        hoja.column_dimensions[get_column_letter(columna)].width = ancho


def generar(origen, destino):
    libro_origen = openpyxl.load_workbook(origen, data_only=False, read_only=True)
    hoja_origen = libro_origen['EMPLEADOS POR DNI']
    encabezados = [celda.value for celda in hoja_origen[1]]
    indices = {normalizar_encabezado(valor): indice for indice, valor in enumerate(encabezados)}
    requeridos = ('nombre', 'apellido', 'dni', 'numero de legajo')
    faltantes = [campo for campo in requeridos if campo not in indices]
    if faltantes:
        raise RuntimeError(f'No se encontraron estas columnas: {", ".join(faltantes)}')
    indices_principales = tuple(indices[campo] for campo in requeridos)
    completos = []
    incompletos = []

    for fila in hoja_origen.iter_rows(min_row=2, values_only=True):
        destino_fila = completos if all(tiene_dato(fila[indice]) for indice in indices_principales) else incompletos
        destino_fila.append(fila)

    libro = Workbook()
    libro.remove(libro.active)
    for nombre, filas, color in (
        ('Datos completos', completos, '16865C'),
        ('Datos incompletos', incompletos, 'A33A3F'),
    ):
        hoja = libro.create_sheet(nombre)
        hoja.append(encabezados)
        for fila in filas:
            hoja.append(fila)
        preparar_hoja(hoja, color)

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    libro.save(destino)
    return len(completos), len(incompletos), len(encabezados)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('origen')
    parser.add_argument('destino')
    argumentos = parser.parse_args()
    completos, incompletos, columnas = generar(argumentos.origen, argumentos.destino)
    print(f'completos={completos} | incompletos={incompletos} | columnas={columnas}')
