import unittest
from datetime import datetime, timedelta, timezone

from modules.security.activation import (
    consume_activation, issue_activation, revoke, verify_password,
)


class ActivationPrototypeTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)

    def test_single_use_token_and_argon2id_hash(self):
        token, record = issue_activation(42, self.now)
        password_hash = consume_activation(record, token, "Synthetic!Pass2026", self.now)
        self.assertTrue(password_hash.startswith("$argon2id$"))
        self.assertTrue(verify_password(password_hash, "Synthetic!Pass2026"))
        with self.assertRaises(ValueError):
            consume_activation(record, token, "Another!Pass2026", self.now)

    def test_expired_token_is_rejected(self):
        token, record = issue_activation(42, self.now, ttl_minutes=1)
        with self.assertRaisesRegex(ValueError, "activation_not_available"):
            consume_activation(record, token, "Synthetic!Pass2026", self.now + timedelta(minutes=2))

    def test_invalid_attempts_are_counted_and_limited(self):
        token, record = issue_activation(42, self.now)
        for _ in range(5):
            with self.assertRaisesRegex(ValueError, "invalid_token"):
                consume_activation(record, "wrong", "Synthetic!Pass2026", self.now)
        with self.assertRaisesRegex(ValueError, "activation_rate_limited"):
            consume_activation(record, token, "Synthetic!Pass2026", self.now)

    def test_revocation(self):
        token, record = issue_activation(42, self.now)
        revoke(record, self.now)
        with self.assertRaisesRegex(ValueError, "activation_not_available"):
            consume_activation(record, token, "Synthetic!Pass2026", self.now)

    def test_weak_password_is_rejected_without_using_token(self):
        token, record = issue_activation(42, self.now)
        with self.assertRaisesRegex(ValueError, "weak_password"):
            consume_activation(record, token, "short", self.now)
        self.assertIsNone(record.used_at)


if __name__ == "__main__":
    unittest.main()

