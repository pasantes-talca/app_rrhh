import unittest

from modules.security.shadow_permissions import (
    PermissionContext, Scope, compare, target_allows,
)


class ShadowPermissionTests(unittest.TestCase):
    def test_employee_can_read_own_document(self):
        context = PermissionContext(
            "empleado", "documentos:propios", 10, 10, scope=Scope.OWN,
        )
        self.assertTrue(target_allows(context)[0])

    def test_employee_cannot_read_another_document(self):
        context = PermissionContext(
            "empleado", "documentos:propios", 10, 11, scope=Scope.OWN,
        )
        decision = compare(True, context)
        self.assertFalse(decision.target_allowed)
        self.assertEqual(decision.difference, "excessive_current_access")

    def test_supervisor_only_sees_assigned_employee(self):
        allowed = PermissionContext(
            "supervisor", "licencias:supervisados", 20, 30,
            supervised_employee_ids=frozenset({30}), scope=Scope.SUPERVISED,
        )
        denied = PermissionContext(
            "supervisor", "licencias:supervisados", 20, 31,
            supervised_employee_ids=frozenset({30}), scope=Scope.SUPERVISED,
        )
        self.assertTrue(target_allows(allowed)[0])
        self.assertFalse(target_allows(denied)[0])

    def test_hierarchical_role_does_not_imply_confidential_access(self):
        context = PermissionContext(
            "gerencia", "documentos:gestionar", scope=Scope.GLOBAL,
        )
        self.assertFalse(target_allows(context)[0])

    def test_unknown_role_is_default_denied(self):
        self.assertFalse(target_allows(PermissionContext("otro", "perfil:propio"))[0])


if __name__ == "__main__":
    unittest.main()

