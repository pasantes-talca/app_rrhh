import unittest
from datetime import date

from modules.indicadores.services import dias_habiles, periodo
from modules.vacaciones.routes import (
    _antiguedad_al_cierre,
    _dias_por_antiguedad,
    _meses_antiguedad_al_cierre,
)


class VacationRulesTests(unittest.TestCase):
    def test_days_by_seniority_boundaries(self):
        self.assertIsNone(_dias_por_antiguedad(None))
        self.assertIsNone(_dias_por_antiguedad(5))
        self.assertEqual(_dias_por_antiguedad(6), 14)
        self.assertEqual(_dias_por_antiguedad(59), 14)
        # Caracteriza los límites inclusivos actuales; VAC-001 requiere definición de RR. HH.
        self.assertEqual(_dias_por_antiguedad(60), 14)
        self.assertEqual(_dias_por_antiguedad(61), 21)
        self.assertEqual(_dias_por_antiguedad(120), 21)
        self.assertEqual(_dias_por_antiguedad(121), 28)
        self.assertEqual(_dias_por_antiguedad(240), 28)
        self.assertEqual(_dias_por_antiguedad(241), 35)

    def test_seniority_at_year_end(self):
        ingreso = date(2020, 7, 1)
        self.assertEqual(_antiguedad_al_cierre(ingreso, 2026), 6)
        self.assertEqual(_meses_antiguedad_al_cierre(ingreso, 2026), 77)


class AbsenceIndicatorRulesTests(unittest.TestCase):
    def test_business_days_in_complete_week(self):
        self.assertEqual(dias_habiles(date(2026, 11, 23), date(2026, 11, 29)), 5)

    def test_invalid_period_has_zero_days(self):
        self.assertEqual(dias_habiles(date(2026, 11, 2), date(2026, 11, 1)), 0)

    def test_year_period(self):
        self.assertEqual(periodo(2026, 0), (date(2026, 1, 1), date(2026, 12, 31)))


if __name__ == "__main__":
    unittest.main()

