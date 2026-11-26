from datetime import date

from app.modules.overtime.rules import day_type, parse_hours, round_overtime


def test_overtime_parsing_and_rounding_matches_existing_rule():
    assert parse_hours("8:45") == 8.75
    assert round_overtime(1.74) == 1
    assert round_overtime(1.75) == 2


def test_day_type_handles_weekends_and_holidays():
    assert day_type(date(2026, 11, 23), {date(2026, 11, 23)}) == "DOM_FER"
    assert day_type(date(2026, 11, 28), set()) == "SAB"
    assert day_type(date(2026, 11, 27), set()) == "LAV"
