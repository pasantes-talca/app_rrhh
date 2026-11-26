import unittest

from modules.security.hardening import (
    FixedWindowRateLimiter, redact_mapping, secure_settings,
)


class SecurityHardeningTests(unittest.TestCase):
    def test_production_rejects_default_or_short_secret(self):
        for secret in (None, "default_secret_key", "short"):
            with self.subTest(secret=secret), self.assertRaises(RuntimeError):
                secure_settings("production", secret)

    def test_production_cookie_settings(self):
        settings = secure_settings("production", "x" * 48)
        self.assertFalse(settings["DEBUG"])
        self.assertTrue(settings["SESSION_COOKIE_SECURE"])
        self.assertTrue(settings["SESSION_COOKIE_HTTPONLY"])
        self.assertTrue(settings["WTF_CSRF_ENABLED"])

    def test_sensitive_log_fields_are_redacted(self):
        result = redact_mapping({
            "usuario": "synthetic",
            "password": "not-for-logs",
            "cbu": "synthetic-bank-value",
        })
        self.assertEqual(result["usuario"], "synthetic")
        self.assertEqual(result["password"], "[REDACTED]")
        self.assertEqual(result["cbu"], "[REDACTED]")

    def test_rate_limit_separates_keys_and_expires(self):
        now = [0.0]
        limiter = FixedWindowRateLimiter(2, 60, clock=lambda: now[0])
        self.assertTrue(limiter.allow("user-a"))
        self.assertTrue(limiter.allow("user-a"))
        self.assertFalse(limiter.allow("user-a"))
        self.assertTrue(limiter.allow("user-b"))
        now[0] = 61
        self.assertTrue(limiter.allow("user-a"))


if __name__ == "__main__":
    unittest.main()

