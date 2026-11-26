"""Prototipo aislado de activación; no consulta ni modifica Usuario."""
import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


PASSWORD_HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)


@dataclass
class ActivationRecord:
    user_id: int
    token_digest: str
    expires_at: datetime
    used_at: datetime | None = None
    revoked_at: datetime | None = None
    failed_attempts: int = 0


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue_activation(user_id: int, now=None, ttl_minutes=30):
    now = now or datetime.now(timezone.utc)
    token = secrets.token_urlsafe(32)
    return token, ActivationRecord(user_id, _digest(token), now + timedelta(minutes=ttl_minutes))


def consume_activation(record: ActivationRecord, token: str, password: str, now=None, max_attempts=5):
    now = now or datetime.now(timezone.utc)
    if record.revoked_at or record.used_at or now >= record.expires_at:
        raise ValueError("activation_not_available")
    if record.failed_attempts >= max_attempts:
        raise ValueError("activation_rate_limited")
    if not secrets.compare_digest(record.token_digest, _digest(token)):
        record.failed_attempts += 1
        raise ValueError("invalid_token")
    if len(password) < 12:
        raise ValueError("weak_password")
    record.used_at = now
    return PASSWORD_HASHER.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def revoke(record: ActivationRecord, now=None):
    record.revoked_at = now or datetime.now(timezone.utc)

