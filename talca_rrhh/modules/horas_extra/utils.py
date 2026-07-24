def parsear_horas(texto: str) -> float:
    """Convierte 'HH:MM' a decimal. Ej: '8:45' -> 8.75."""
    texto = str(texto).strip()
    if ':' not in texto:
        return 0.0
    try:
        h, m = texto.split(':')
        return float(h) + float(m) / 60.0
    except (ValueError, IndexError):
        return 0.0

def redondear_horas_extra(horas_extra_decimal: float) -> float:
    """
    Redondea horas extra según regla de negocio:
    - Fracción < 45 min (0.75 h) -> no hay extra.
    - Fracción >= 45 min -> redondea 1 hora entera hacia arriba.
    """
    if horas_extra_decimal <= 0:
        return 0.0

    parte_entera = int(horas_extra_decimal)
    fraccion = horas_extra_decimal - parte_entera

    if fraccion >= 0.75:
        return float(parte_entera + 1)

    return float(parte_entera)

def obtener_tipo_dia(fecha, feriados: set) -> str:
    """Retorna el tipo de día: LAV, SAB o DOM_FER."""
    if fecha in feriados:
        return 'DOM_FER'
    weekday = fecha.weekday()
    if weekday == 6:
        return 'DOM_FER'
    if weekday == 5:
        return 'SAB'
    return 'LAV'
