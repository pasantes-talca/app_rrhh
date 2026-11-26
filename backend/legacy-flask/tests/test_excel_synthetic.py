import tempfile
import unittest
from datetime import date
from pathlib import Path

import openpyxl

from scripts.importar_ausentismo_excel import fecha, legajo, nombre_normalizado
from scripts.importar_vacaciones_excel import decimal


class SyntheticExcelTests(unittest.TestCase):
    def test_absence_workbook_has_required_sheets_and_types(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ausentismo-sintetico.xlsx"
            book = openpyxl.Workbook()
            dimensions = book.active
            dimensions.title = "DIMENSIONES"
            dimensions.append(["LEGAJO", "NOMBRE", "AREA", "PLANTA", "INGRESO", "BAJA", "NACIMIENTO"])
            dimensions.append([101, "PERSONA SINTETICA", "CALIDAD", "MENDOZA", date(2020, 1, 2), None, date(1990, 2, 3)])
            facts = book.create_sheet("HECHOS")
            facts.append(["LEGAJO", "DESDE", "HASTA", "DESCRIPCION", "CODIGO"])
            facts.append([101, date(2026, 1, 5), date(2026, 1, 6), "CAPACITACION", 14])
            types = book.create_sheet("TIPOS DE AUSENCIA")
            types.append(["COD", "CATEGORIA", "DESCRIPCION", "IMPACTO"])
            types.append([14, "FORMACION", "CAPACITACION", "PLANIFICADA"])
            book.save(path)

            loaded = openpyxl.load_workbook(path, read_only=True, data_only=True)
            self.assertEqual(set(loaded.sheetnames), {"DIMENSIONES", "HECHOS", "TIPOS DE AUSENCIA"})
            row = next(loaded["DIMENSIONES"].iter_rows(min_row=2, values_only=True))
            self.assertEqual(legajo(row[0]), "101")
            self.assertEqual(nombre_normalizado(row[1]), "PERSONA SINTETICA")
            self.assertEqual(fecha(row[4]), date(2020, 1, 2))
            loaded.close()
            book.close()

    def test_vacation_numeric_normalization(self):
        self.assertEqual(str(decimal("14.5")), "14.5")
        self.assertEqual(str(decimal(None)), "0")


if __name__ == "__main__":
    unittest.main()

