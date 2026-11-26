import unittest

from tests.postgres_config import PostgreSQLTestConfig, validate


class PostgreSQLTestConfigTests(unittest.TestCase):
    def test_configuration_is_local_and_isolated(self):
        validated = validate()
        self.assertTrue(validated["TESTING"])
        self.assertFalse(validated["TRILAY_SYNC_ENABLED"])
        self.assertIn("127.0.0.1:55432/talca_rrhh_test", validated["SQLALCHEMY_DATABASE_URI"])


if __name__ == "__main__":
    unittest.main()

