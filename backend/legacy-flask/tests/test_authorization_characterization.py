import unittest
from types import SimpleNamespace

from modules.administracion.security import accion_endpoint, tiene_permiso


def user(role, permissions=()):
    return SimpleNamespace(
        rol=SimpleNamespace(nombre=role) if role else None,
        permisos=list(permissions),
    )


class AuthorizationCharacterizationTests(unittest.TestCase):
    def test_administrator_has_global_permission(self):
        self.assertTrue(tiene_permiso(user("administrador"), "documentos", "anular"))

    def test_management_roles_only_read_absence_via_central_policy(self):
        self.assertTrue(tiene_permiso(user("recursos_humanos"), "ausentismo", "consultar"))
        self.assertFalse(tiene_permiso(user("recursos_humanos"), "ausentismo", "editar"))

    def test_gerencia_only_reads_indicators(self):
        self.assertTrue(tiene_permiso(user("gerencia"), "indicadores", "consultar"))
        self.assertFalse(tiene_permiso(user("gerencia"), "indicadores", "exportar"))

    def test_explicit_denial(self):
        permission = SimpleNamespace(modulo="documentos", accion="consultar", permitido=False)
        self.assertFalse(tiene_permiso(user("empleado", [permission]), "documentos", "consultar"))

    def test_action_classifier(self):
        self.assertEqual(accion_endpoint("documentos.descargar", "GET"), "exportar")
        self.assertEqual(accion_endpoint("noticias.eliminar", "POST"), "anular")
        self.assertEqual(accion_endpoint("empleados.editar", "POST"), "editar")

    @unittest.expectedFailure
    def test_known_vulnerability_unconfigured_user_should_be_denied(self):
        # Defecto SEC-001: hoy devuelve True por compatibilidad.
        self.assertFalse(tiene_permiso(user("empleado"), "administracion", "consultar"))


if __name__ == "__main__":
    unittest.main()

