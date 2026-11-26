"""Genera una nómina limpia de empleados activos/vinculados sin fecha de egreso."""
import argparse
from pathlib import Path

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from generar_reporte_estado_nomina import (
    clasificar_estado,
    dni_valido,
    legajo_valido,
    nombre_valido,
    normalizar,
    texto,
)


def generar(origen, destino):
    libro_origen = openpyxl.load_workbook(origen, data_only=True, read_only=True)
    hoja_origen = libro_origen['EMPLEADOS POR DNI']
    seleccionados = []

    for fila in hoja_origen.iter_rows(min_row=2, values_only=True):
        estado = clasificar_estado(fila[41])
        vinculado = normalizar(fila[74]) == 'vinculado'
        fecha_egreso_vacia = not texto(fila[30])
        datos_completos = (
            nombre_valido(fila[1]) and nombre_valido(fila[2])
            and dni_valido(fila[3]) and legajo_valido(fila[28])
        )
        activo_o_vinculado = estado == 'activo' or (estado is None and vinculado)
        if activo_o_vinculado and estado != 'desvinculado' and fecha_egreso_vacia and datos_completos:
            seleccionados.append((texto(fila[1]), texto(fila[2]), texto(fila[3]), texto(fila[28])))

    seleccionados.sort(key=lambda item: (item[1].upper(), item[0].upper(), item[3]))
    libro = Workbook()
    hoja = libro.active
    hoja.title = 'Empleados activos'
    hoja.append(['Nombre', 'Apellido', 'DNI', 'Número de legajo'])
    for registro in seleccionados:
        hoja.append(registro)
        hoja.cell(hoja.max_row, 3).number_format = '@'
        hoja.cell(hoja.max_row, 4).number_format = '@'

    hoja.freeze_panes = 'A2'
    hoja.auto_filter.ref = hoja.dimensions
    hoja.sheet_view.showGridLines = False
    hoja.row_dimensions[1].height = 28
    relleno = PatternFill('solid', fgColor='D71920')
    for celda in hoja[1]:
        celda.fill = relleno
        celda.font = Font(color='FFFFFF', bold=True)
        celda.alignment = Alignment(vertical='center')
    for columna, ancho in {'A': 28, 'B': 32, 'C': 16, 'D': 18}.items():
        hoja.column_dimensions[columna].width = ancho

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    libro.save(destino)
    return len(seleccionados)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('origen')
    parser.add_argument('destino')
    argumentos = parser.parse_args()
    cantidad = generar(argumentos.origen, argumentos.destino)
    print(f'empleados_exportados={cantidad}')
