import unittest
from datetime import date

from integrations.trilay.empleados2 import (
    DATE_FIELDS,
    SOURCE_COLUMNS,
    _normalize,
    _text,
)


class TrilayContractTests(unittest.TestCase):
    def synthetic_row(self):
        row = {source: None for source in SOURCE_COLUMNS}
        row.update({
            "idUsuario": 900001,
            "codUsuario": " test.user ",
            "nombre": " Persona ",
            "apellido": " Sintética ",
            "fechanacimiento": "15/04/1990",
        })
        return row

    def test_contract_excludes_password_columns(self):
        normalized = {name.lower() for name in SOURCE_COLUMNS}
        forbidden = {"password", "clave", "contrasena", "contraseña"}
        self.assertTrue(normalized.isdisjoint(forbidden))

    def test_normalization_is_deterministic(self):
        one = _normalize(self.synthetic_row())
        two = _normalize(self.synthetic_row())
        self.assertEqual(one["huella_origen"], two["huella_origen"])
        self.assertEqual(one["cod_usuario"], "test.user")
        self.assertEqual(one["fecha_nacimiento"], date(1990, 4, 15))

    def test_missing_source_identifier_is_rejected(self):
        row = self.synthetic_row()
        row["idUsuario"] = None
        with self.assertRaises(ValueError):
            _normalize(row)

    def test_whitespace_normalization(self):
        self.assertEqual(_text("  Persona   Sintética  "), "Persona Sintética")
        self.assertIsNone(_text("  "))

    def test_declared_date_fields_are_mapped(self):
        self.assertTrue(DATE_FIELDS.issubset(set(SOURCE_COLUMNS.values())))


if __name__ == "__main__":
    unittest.main()

