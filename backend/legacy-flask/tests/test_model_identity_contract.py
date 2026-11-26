import unittest

from database.models import Empleado, Empleado2, Usuario


class ModelIdentityContractTests(unittest.TestCase):
    def test_primary_keys(self):
        self.assertEqual([c.name for c in Empleado.__table__.primary_key], ["id"])
        self.assertEqual([c.name for c in Empleado2.__table__.primary_key], ["id"])

    def test_user_links_both_employee_models(self):
        foreign_keys = {fk.target_fullname for c in Usuario.__table__.columns for fk in c.foreign_keys}
        self.assertIn("rrhh.empleados.id", foreign_keys)
        self.assertIn("rrhh.empleados2.id", foreign_keys)

    def test_trilay_identifier_is_unique(self):
        self.assertTrue(Empleado2.__table__.c.id_usuario.unique)

    def test_legacy_business_identifiers_are_unique(self):
        self.assertTrue(Empleado.__table__.c.dni.unique)
        self.assertTrue(Empleado.__table__.c.cuil.unique)
        self.assertTrue(Empleado.__table__.c.legajo.unique)


if __name__ == "__main__":
    unittest.main()

