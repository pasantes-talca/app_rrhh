from datetime import date

from app.modules.absence.service import business_days, period


def test_business_days_excludes_weekends():
    assert business_days(date(2026, 11, 23), date(2026, 11, 29)) == 5
    assert business_days(date(2026, 11, 28), date(2026, 11, 29)) == 0


def test_period_supports_month_or_full_year():
    assert period(2026, 2) == (date(2026, 2, 1), date(2026, 2, 28))
    assert period(2026, 0) == (date(2026, 1, 1), date(2026, 12, 31))
