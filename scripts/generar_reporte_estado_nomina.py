"""Genera un libro separado por estado a partir de la nómina maestra."""
import argparse
import re
import unicodedata
from pathlib import Path

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


def texto(valor):
    return '' if valor is None else str(valor).strip()


def normalizar(valor):
    limpio = unicodedata.normalize('NFKD', texto(valor)).encode('ascii', 'ignore').decode().lower()
    return ' '.join(limpio.split())


def clasificar_estado(valor):
    estado = normalizar(valor)
    if not estado:
        return None
    if estado == '1' or 'trilay usuario: 1' in estado or 'baja' in estado or 'desvinculado' in estado:
        return 'desvinculado'
    if estado == '0' or 'trilay usuario: 0' in estado or 'activo' in estado:
        return 'activo'
    return None


def nombre_valido(valor):
    valor = texto(valor)
    return bool(valor and valor != '-' and ':' not in valor and ';' not in valor)


def dni_valido(valor):
    valor = re.sub(r'\.0$', '', texto(valor)).replace('.', '').replace(' ', '')
    return bool(re.fullmatch(r'\d{7,8}', valor))


def legajo_valido(valor):
    valor = re.sub(r'\.0$', '', texto(valor))
    return bool(valor and valor not in ('0', '-') and ':' not in valor and ';' not in valor)


def registro_completo(fila):
    return (
        nombre_valido(fila[1]) and nombre_valido(fila[2])
        and dni_valido(fila[3]) and legajo_valido(fila[28])
    )


def preparar_hoja(hoja, color):
    hoja.freeze_panes = 'A2'
    hoja.auto_filter.ref = hoja.dimensions
    hoja.sheet_view.showGridLines = False
    relleno = PatternFill('solid', fgColor=color)
    for celda in hoja[1]:
        celda.fill = relleno
        celda.font = Font(color='FFFFFF', bold=True)
        celda.alignment = Alignment(vertical='center')
    hoja.row_dimensions[1].height = 28
    for columna in range(1, hoja.max_column + 1):
        valores = [texto(hoja.cell(fila, columna).value) for fila in range(1, min(hoja.max_row, 150) + 1)]
        ancho = min(max(max((len(v) for v in valores), default=8) + 2, 12), 35)
        hoja.column_dimensions[get_column_letter(columna)].width = ancho


def generar(origen, destino):
    libro_origen = openpyxl.load_workbook(origen, data_only=True, read_only=True)
    hoja_origen = libro_origen['EMPLEADOS POR DNI']
    encabezados = [celda.value for celda in hoja_origen[1]]
    filas = [tuple(fila) for fila in hoja_origen.iter_rows(min_row=2, values_only=True)]

    activos = [fila for fila in filas if clasificar_estado(fila[41]) == 'activo']
    desvinculados = [fila for fila in filas if clasificar_estado(fila[41]) == 'desvinculado']
    activos_completos = [fila for fila in activos if registro_completo(fila)]
    desvinculados_completos = [fila for fila in desvinculados if registro_completo(fila)]

    libro = Workbook()
    libro.remove(libro.active)
    conjuntos = (
        ('Activos', activos, encabezados, 'D71920'),
        ('Desvinculados', desvinculados, encabezados, '5B5B66'),
        ('Activos completos', activos_completos, ['Nombre', 'Apellido', 'DNI', 'Número de legajo'], '16865C'),
        ('Desvinculados completos', desvinculados_completos, ['Nombre', 'Apellido', 'DNI', 'Número de legajo'], 'A33A3F'),
    )
    for nombre, registros, titulos, color in conjuntos:
        hoja = libro.create_sheet(nombre)
        hoja.append(titulos)
        if nombre.endswith('completos'):
            for fila in registros:
                hoja.append([fila[1], fila[2], texto(fila[3]), texto(fila[28])])
                hoja.cell(hoja.max_row, 3).number_format = '@'
                hoja.cell(hoja.max_row, 4).number_format = '@'
        else:
            for fila in registros:
                hoja.append(fila)
        preparar_hoja(hoja, color)

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    libro.save(destino)
    return {
        'activos': len(activos),
        'desvinculados': len(desvinculados),
        'activos_completos': len(activos_completos),
        'desvinculados_completos': len(desvinculados_completos),
        'sin_clasificar': len(filas) - len(activos) - len(desvinculados),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('origen')
    parser.add_argument('destino')
    argumentos = parser.parse_args()
    resultado = generar(argumentos.origen, argumentos.destino)
    print(' | '.join(f'{clave}={valor}' for clave, valor in resultado.items()))
