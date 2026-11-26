from datetime import date

from app.modules.self_service.daily_notifications import _birthday_today


def test_birthday_today_handles_regular_and_leap_birthdays():
    assert _birthday_today(date(1990, 5, 4), date(2026, 5, 4))
    assert not _birthday_today(date(1990, 5, 4), date(2026, 5, 5))
    assert _birthday_today(date(1992, 2, 29), date(2026, 2, 28))
    assert not _birthday_today(date(1992, 2, 29), date(2028, 2, 28))
