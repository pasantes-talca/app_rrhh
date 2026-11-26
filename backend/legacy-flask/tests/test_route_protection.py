import unittest

from app import create_app


class TestConfig:
    TESTING = True
    SECRET_KEY = "synthetic-only"
    SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    TRILAY_SYNC_ENABLED = False
    UPLOAD_FOLDER = ".test-artifacts/uploads"


class RouteProtectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestConfig)
        cls.client = cls.app.test_client()

    def test_root_redirects_to_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login", response.location)

    def test_protected_routes_redirect_anonymous_user(self):
        for path in (
            "/dashboard/", "/empleados/", "/licencias/", "/mis-vacaciones/",
            "/ausentismo/", "/horas_extra/", "/documentos/", "/administracion/",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/auth/login", response.location)


if __name__ == "__main__":
    unittest.main()

