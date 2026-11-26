"""Importa el libro de ausentismo de RR. HH. de forma idempotente."""
import argparse
import os
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date, datetime

import openpyxl

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from app import create_app  # noqa: E402
from database.models import Ausencia, AusentismoEmpleado, Empleado2, TipoAusencia  # noqa: E402
from extensions import db  # noqa: E402


def legajo(valor):
    texto = '' if valor is None else str(valor).strip()
    texto = re.sub(r'\.0$', '', texto)
    return str(int(texto)) if texto.isdigit() else texto.upper()


def nombre_normalizado(valor):
    texto = unicodedata.normalize('NFKD', '' if valor is None else str(valor))
    texto = ''.join(c for c in texto if not unicodedata.combining(c)).upper()
    return ' '.join(re.findall(r'[A-Z0-9]+', texto))


def fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        for formato in ('%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(valor.strip(), formato).date()
            except ValueError:
                pass
    raise ValueError(f'Fecha inválida: {valor!r}')


def elegir_empleado(candidatos, nombre_excel):
    presentes = [item for item in candidatos if item.presente_en_origen]
    if presentes:
        candidatos = presentes
    if len(candidatos) == 1:
        return candidatos[0]
    buscado = set(nombre_normalizado(nombre_excel).split())
    puntuados = []
    for empleado in candidatos:
        nombre = empleado.nombre_completo or f'{empleado.apellido or ""} {empleado.nombre or ""}'
        tokens = set(nombre_normalizado(nombre).split())
        puntuados.append((len(buscado & tokens), empleado))
    puntuados.sort(key=lambda item: item[0], reverse=True)
    if not puntuados or puntuados[0][0] == 0:
        return None
    if len(puntuados) > 1 and puntuados[0][0] == puntuados[1][0]:
        return None
    return puntuados[0][1]


def importar(ruta):
    libro = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    dimensiones = {}
    for fila in libro['DIMENSIONES'].iter_rows(min_row=2, values_only=True):
        clave = legajo(fila[0])
        if clave:
            dimensiones[clave] = {
                'nombre': str(fila[1] or '').strip(), 'area': str(fila[2] or '').strip(),
                'planta': str(fila[3] or '').strip(),
            }

    por_legajo = defaultdict(list)
    for empleado in Empleado2.query.filter(Empleado2.numero_legajo.isnot(None)).all():
        por_legajo[legajo(empleado.numero_legajo)].append(empleado)

    dimensiones_procesadas = 0
    for numero_fila, fila in enumerate(libro['DIMENSIONES'].iter_rows(min_row=2, values_only=True), start=2):
        clave = legajo(fila[0])
        if not clave:
            continue
        datos = dimensiones[clave]
        empleado = elegir_empleado(por_legajo.get(clave, []), datos['nombre'])
        item = AusentismoEmpleado.query.filter_by(legajo=clave).first() or AusentismoEmpleado(legajo=clave)
        item.empleado2_id = empleado.id if empleado else None
        item.nombre = datos['nombre'] or f'Legajo {clave}'
        item.area = datos['area'] or None
        item.planta = datos['planta'] or None
        item.fecha_ingreso = fecha(fila[4]) if fila[4] not in (None, '') else None
        item.fecha_baja = fecha(fila[5]) if fila[5] not in (None, '') else None
        item.fecha_nacimiento = fecha(fila[6]) if fila[6] not in (None, '') else None
        item.archivo_origen = os.path.basename(ruta)
        item.fila_excel = numero_fila
        db.session.add(item)
        dimensiones_procesadas += 1
    db.session.flush()

    catalogo = 0
    for fila in libro['TIPOS DE AUSENCIA'].iter_rows(min_row=2, values_only=True):
        if fila[0] in (None, ''):
            continue
        codigo = int(fila[0])
        item = db.session.get(TipoAusencia, codigo) or TipoAusencia(codigo=codigo)
        item.categoria = str(fila[1] or '').strip()
        item.descripcion = str(fila[2] or '').strip()
        item.impacto_productividad = str(fila[3] or '').strip() or None
        db.session.add(item)
        catalogo += 1
    db.session.flush()

    creados = actualizados = 0
    errores = []
    archivo = os.path.basename(ruta)
    for numero_fila, fila in enumerate(libro['HECHOS'].iter_rows(min_row=2, values_only=True), start=2):
        if not any(valor not in (None, '') for valor in fila):
            continue
        try:
            clave = legajo(fila[0])
            dimension = dimensiones.get(clave, {})
            empleado = elegir_empleado(por_legajo.get(clave, []), dimension.get('nombre', ''))
            inicio, fin = fecha(fila[1]), fecha(fila[2])
            observaciones = []
            if fin < inicio:
                inicio, fin = fin, inicio
                observaciones.append('Fechas de inicio y fin invertidas durante la importación porque el Excel las informaba al revés.')
            if not empleado:
                observaciones.append('Legajo no encontrado en empleados2; el registro se conserva pendiente de vinculación.')
            codigo = int(fila[4])
            if not db.session.get(TipoAusencia, codigo):
                raise ValueError(f'Código de ausencia inexistente: {codigo}')
            referencia = f'{archivo}:HECHOS:{numero_fila}'
            item = Ausencia.query.filter_by(origen='EXCEL', referencia_origen=referencia).first()
            if item:
                actualizados += 1
            else:
                item = Ausencia(origen='EXCEL', referencia_origen=referencia)
                creados += 1
            item.empleado2_id = empleado.id if empleado else None
            item.tipo_codigo = codigo
            item.fecha_inicio = inicio
            item.fecha_fin = fin
            item.dias_calendario = (fin - inicio).days + 1
            item.legajo_origen = clave
            item.nombre_origen = dimension.get('nombre') or None
            item.area_origen = dimension.get('area') or None
            item.planta_origen = dimension.get('planta') or None
            item.tipo_descripcion_origen = str(fila[3] or '').strip() or None
            item.archivo_origen = archivo
            item.fila_excel = numero_fila
            item.observaciones_importacion = ' '.join(observaciones) or None
            db.session.add(item)
        except Exception as exc:
            errores.append(f'Fila {numero_fila}: {exc}')
    if errores:
        db.session.rollback()
        raise RuntimeError('Importación cancelada; no se guardó nada:\n' + '\n'.join(errores))
    db.session.commit()
    return catalogo, dimensiones_procesadas, creados, actualizados


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('archivo')
    args = parser.parse_args()
    app = create_app()
    with app.app_context():
        tipos, dimensiones, creados, actualizados = importar(args.archivo)
        print(f'Tipos procesados: {tipos}')
        print(f'Empleados de la dimensión procesados: {dimensiones}')
        print(f'Ausencias creadas: {creados}')
        print(f'Ausencias actualizadas: {actualizados}')
