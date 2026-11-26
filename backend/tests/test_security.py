from dataclasses import replace

import pytest
from fastapi import HTTPException
from werkzeug.security import generate_password_hash

from app.core.security import Principal, require_permission
from app.core.rate_limit import SlidingWindowLimiter
from app.modules.auth.passwords import hash_password, verify_password
from app.modules.administration.router import _admin


def test_existing_werkzeug_hash_is_accepted_and_marked_for_upgrade():
    valid, needs_rehash = verify_password(generate_password_hash("Talca-test-2026"), "Talca-test-2026")
    assert valid is True
    assert needs_rehash is True


def test_argon2_hash_is_verified_without_exposing_password():
    encoded = hash_password("Talca-test-2026")
    assert "Talca-test-2026" not in encoded
    assert verify_password(encoded, "Talca-test-2026")[0] is True
    assert verify_password(encoded, "incorrecta")[0] is False


def test_permission_dependency_is_default_deny_and_admin_wildcard():
    dependency = require_permission("employees:read")
    with pytest.raises(HTTPException) as denied:
        dependency(Principal(1, "empleado", 1, frozenset()))
    assert denied.value.status_code == 403
    assert dependency(Principal(2, "administrador", None, frozenset({"*"}))).user_id == 2


def test_administration_is_restricted_to_administrator_role():
    with pytest.raises(HTTPException) as denied:
        _admin(Principal(1, "recursos_humanos", 1, frozenset()))
    assert denied.value.status_code == 403
    assert _admin(Principal(2, "administrador", None, frozenset({"*"}))) is None


def test_login_rate_limiter_uses_a_sliding_window_and_can_reset():
    limiter = SlidingWindowLimiter(maximum=2, window_seconds=10)
    assert limiter.allow("client", now=0)
    assert limiter.allow("client", now=1)
    assert not limiter.allow("client", now=2)
    assert limiter.allow("client", now=11)
    limiter.reset("client")
    assert limiter.allow("client", now=11)
