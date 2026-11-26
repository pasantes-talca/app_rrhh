from datetime import date


def parse_hours(value: object) -> float:
    text = str(value).strip()
    if ":" not in text:
        return 0.0
    try:
        hours, minutes = text.split(":", 1)
        return float(hours) + float(minutes) / 60
    except (TypeError, ValueError):
        return 0.0


def round_overtime(value: float) -> float:
    if value <= 0:
        return 0.0
    whole = int(value)
    return float(whole + 1 if value - whole >= 0.75 else whole)


def day_type(value: date, holidays: set[date]) -> str:
    if value in holidays or value.weekday() == 6:
        return "DOM_FER"
    if value.weekday() == 5:
        return "SAB"
    return "LAV"
