import unittest

from tests.safety import assert_safe_test_settings


class EnvironmentSafetyTests(unittest.TestCase):
    def test_accepts_isolated_sqlite(self):
        assert_safe_test_settings({
            "TESTING": True,
            "TRILAY_SYNC_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
        })

    def test_rejects_missing_testing_flag(self):
        with self.assertRaises(RuntimeError):
            assert_safe_test_settings({
                "TESTING": False,
                "TRILAY_SYNC_ENABLED": False,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
            })

    def test_rejects_enabled_trilay(self):
        with self.assertRaises(RuntimeError):
            assert_safe_test_settings({
                "TESTING": True,
                "TRILAY_SYNC_ENABLED": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
            })

    def test_rejects_corporate_network(self):
        with self.assertRaises(RuntimeError):
            assert_safe_test_settings({
                "TESTING": True,
                "TRILAY_SYNC_ENABLED": False,
                "SQLALCHEMY_DATABASE_URI": "postgresql://user:secret@192.168.1.2/rrhh",
            })

    def test_rejects_postgres_without_test_name(self):
        with self.assertRaises(RuntimeError):
            assert_safe_test_settings({
                "TESTING": True,
                "TRILAY_SYNC_ENABLED": False,
                "SQLALCHEMY_DATABASE_URI": "postgresql://localhost/recursos_humanos",
            })


if __name__ == "__main__":
    unittest.main()

