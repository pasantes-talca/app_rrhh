import calendar
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import extract

from database.models import Ausencia, AusentismoEmpleado


MESES = ('', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre')
MESES_CORTOS = ('', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic')
DIAS_CORTOS = ('Lun', 'Mar', 'Mié', 'Jue', 'Vie')


def dias_habiles(desde, hasta):
    if not desde or not hasta or hasta < desde:
        return 0
    total = (hasta - desde).days + 1
    semanas, resto = divmod(total, 7)
    resultado = semanas * 5
    for offset in range(resto):
        if (desde.weekday() + offset) % 7 < 5:
            resultado += 1
    return resultado


def periodo(anio, mes):
    desde = date(anio, mes or 1, 1)
    ultimo_mes = mes or 12
    hasta = date(anio, ultimo_mes, calendar.monthrange(anio, ultimo_mes)[1])
    return desde, hasta


def empleados_dimension(desde, hasta, planta=''):
    consulta = AusentismoEmpleado.query
    if planta:
        consulta = consulta.filter(AusentismoEmpleado.planta == planta)
    return [e for e in consulta.all()
            if (not e.fecha_ingreso or e.fecha_ingreso <= hasta)
            and (not e.fecha_baja or e.fecha_baja >= desde)]


def capacidad_habil(empleados, desde, hasta):
    total = 0
    por_area = defaultdict(int)
    for empleado in empleados:
        inicio = max(desde, empleado.fecha_ingreso) if empleado.fecha_ingreso else desde
        fin = min(hasta, empleado.fecha_baja) if empleado.fecha_baja else hasta
        capacidad = dias_habiles(inicio, fin)
        total += capacidad
        por_area[empleado.area or 'Sin área'] += capacidad
    return total, por_area


def ausencias_periodo(desde, hasta, planta=''):
    consulta = Ausencia.query.filter(Ausencia.fecha_inicio <= hasta, Ausencia.fecha_fin >= desde)
    if planta:
        consulta = consulta.filter(Ausencia.planta_origen == planta)
    return consulta.order_by(Ausencia.fecha_inicio).all()


def dias_evento(evento, desde, hasta):
    return dias_habiles(max(evento.fecha_inicio, desde), min(evento.fecha_fin, hasta))


def _resumen_base(desde, hasta, planta=''):
    empleados = empleados_dimension(desde, hasta, planta)
    eventos = ausencias_periodo(desde, hasta, planta)
    capacidad, capacidad_area = capacidad_habil(empleados, desde, hasta)
    filas = [(evento, dias_evento(evento, desde, hasta)) for evento in eventos]
    filas = [(evento, dias) for evento, dias in filas if dias > 0]
    total_dias = sum(dias for _, dias in filas)
    personas = {evento.legajo_origen for evento, _ in filas}
    tasa = (total_dias / capacidad * 100) if capacidad else 0
    return empleados, filas, capacidad_area, total_dias, personas, tasa


def resumen_ausentismo(anio, mes=0, planta=''):
    desde, hasta = periodo(anio, mes)
    empleados, filas, capacidad_area, total_dias, personas, tasa = _resumen_base(desde, hasta, planta)
    categorias = defaultdict(int)
    personas_dias = defaultdict(int)
    personas_nombres = {}
    areas_dias = defaultdict(int)
    dias_semana = defaultdict(int)
    injustificadas = 0
    detalle = []
    for evento, dias in filas:
        categoria = evento.tipo.categoria if evento.tipo else 'SIN CATEGORÍA'
        categorias[categoria] += dias
        personas_dias[evento.legajo_origen] += dias
        personas_nombres[evento.legajo_origen] = evento.nombre_origen or f'Legajo {evento.legajo_origen}'
        area = evento.area_origen or 'Sin área'
        areas_dias[area] += dias
        if categoria.upper() == 'INJUSTIFICADA':
            injustificadas += dias
        actual = max(evento.fecha_inicio, desde)
        fin = min(evento.fecha_fin, hasta)
        while actual <= fin:
            if actual.weekday() < 5:
                dias_semana[DIAS_CORTOS[actual.weekday()]] += 1
            actual += timedelta(days=1)
        detalle.append({'legajo': evento.legajo_origen, 'nombre': personas_nombres[evento.legajo_origen],
                        'area': area, 'planta': evento.planta_origen or '-',
                        'categoria': categoria, 'descripcion': evento.tipo.descripcion if evento.tipo else '-',
                        'desde': evento.fecha_inicio, 'hasta': evento.fecha_fin, 'dias': dias})

    anterior_hasta = desde - timedelta(days=1)
    duracion = (hasta - desde).days
    anterior_desde = anterior_hasta - timedelta(days=duracion)
    _, _, _, dias_anteriores, _, _ = _resumen_base(anterior_desde, anterior_hasta, planta)
    variacion = ((total_dias - dias_anteriores) / dias_anteriores * 100) if dias_anteriores else None

    areas_tasa = {area: (dias / capacidad_area.get(area, 0) * 100 if capacidad_area.get(area) else 0)
                  for area, dias in areas_dias.items()}
    top_personas = sorted(personas_dias, key=personas_dias.get, reverse=True)[:10]
    top_areas = sorted(areas_tasa, key=areas_tasa.get, reverse=True)[:10]
    return {
        'desde': desde, 'hasta': hasta, 'empleados_activos': len(empleados),
        'empleados_ausentes': len(personas), 'dias_habiles': total_dias,
        'tasa': tasa, 'injustificadas': injustificadas,
        'promedio': total_dias / len(personas) if personas else 0,
        'variacion': variacion,
        'categorias': {'labels': list(categorias), 'values': list(categorias.values())},
        'personas': {'labels': [personas_nombres[k] for k in top_personas],
                     'values': [personas_dias[k] for k in top_personas]},
        'areas': {'labels': top_areas, 'values': [round(areas_tasa[k], 2) for k in top_areas]},
        'semana': {'labels': list(DIAS_CORTOS), 'values': [dias_semana[d] for d in DIAS_CORTOS]},
        'detalle': sorted(detalle, key=lambda item: (item['dias'], item['desde']), reverse=True),
    }


def resumen_tendencia(anio, planta=''):
    meses_dias, meses_tasa = [], []
    heatmap = []
    for mes in range(1, 13):
        resumen = resumen_ausentismo(anio, mes, planta)
        meses_dias.append(resumen['dias_habiles'])
        meses_tasa.append(round(resumen['tasa'], 2))
        heatmap.append(resumen['semana']['values'])
    return {'labels': list(MESES_CORTOS[1:]), 'dias': meses_dias,
            'tasas': meses_tasa, 'heatmap': heatmap, 'dias_semana': list(DIAS_CORTOS)}


def resumen_vacaciones(anio, mes=0, planta=''):
    desde, hasta = periodo(anio, mes)
    empleados = empleados_dimension(desde, hasta, planta)
    eventos = [e for e in ausencias_periodo(desde, hasta, planta) if e.tipo_codigo == 2]
    personas = {e.legajo_origen for e in eventos}
    areas_personas = defaultdict(set)
    dotacion_area = defaultdict(int)
    for empleado in empleados:
        dotacion_area[empleado.area or 'Sin área'] += 1
    filas = []
    for evento in eventos:
        area = evento.area_origen or 'Sin área'
        areas_personas[area].add(evento.legajo_origen)
        filas.append({'nombre': evento.nombre_origen or f'Legajo {evento.legajo_origen}',
                      'legajo': evento.legajo_origen, 'area': area,
                      'planta': evento.planta_origen or '-', 'desde': evento.fecha_inicio,
                      'hasta': evento.fecha_fin, 'dias': (evento.fecha_fin - evento.fecha_inicio).days + 1})
    areas = sorted(areas_personas, key=lambda a: len(areas_personas[a]), reverse=True)
    return {
        'personas': len(personas), 'dotacion': len(empleados),
        'porcentaje': len(personas) / len(empleados) * 100 if empleados else 0,
        'areas_personas': {'labels': areas, 'values': [len(areas_personas[a]) for a in areas]},
        'areas_porcentaje': {'labels': areas, 'values': [round(len(areas_personas[a]) / dotacion_area[a] * 100, 2)
                                                        if dotacion_area[a] else 0 for a in areas]},
        'detalle': sorted(filas, key=lambda item: item['desde']), 'desde': desde, 'hasta': hasta,
    }
