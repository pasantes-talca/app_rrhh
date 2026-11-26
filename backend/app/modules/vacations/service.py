from datetime import date
from decimal import Decimal


def seniority_months_at_year_end(start_date: date | None, year: int) -> int | None:
    end = date(year, 12, 31)
    if start_date is None or start_date > end:
        return None
    months = (end.year - start_date.year) * 12 + end.month - start_date.month
    return months - int(end.day < start_date.day)


def vacation_days_for_seniority(months: int | None) -> int | None:
    if months is None or months < 6:
        return None
    if months <= 60:
        return 14
    if months <= 120:
        return 21
    if months <= 240:
        return 28
    return 35


def non_negative(value: Decimal) -> Decimal:
    return max(value, Decimal("0"))
