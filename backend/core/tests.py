from django.test import SimpleTestCase


class ApiContractTests(SimpleTestCase):
    def test_health_contract(self):
        response = self.client.get("/api/v1/health", HTTP_HOST="127.0.0.1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["service"], "talca-personas")

    def test_private_endpoints_reject_anonymous_access(self):
        session_response = self.client.get("/api/v1/auth/me", HTTP_HOST="127.0.0.1")
        employees_response = self.client.get("/api/v1/employees/", HTTP_HOST="127.0.0.1")
        self.assertIn(session_response.status_code, {401, 403})
        self.assertIn(employees_response.status_code, {401, 403})
