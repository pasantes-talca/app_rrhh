from datetime import date

from app.modules.vacations.service import seniority_months_at_year_end, vacation_days_for_seniority


def test_vacation_scale_matches_business_rule():
    assert vacation_days_for_seniority(5) is None
    assert vacation_days_for_seniority(6) == 14
    assert vacation_days_for_seniority(60) == 14
    assert vacation_days_for_seniority(61) == 21
    assert vacation_days_for_seniority(121) == 28
    assert vacation_days_for_seniority(241) == 35


def test_seniority_is_calculated_at_year_end():
    assert seniority_months_at_year_end(date(2020, 7, 1), 2026) == 77
