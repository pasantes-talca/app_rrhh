from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from werkzeug.security import check_password_hash

_hasher = PasswordHasher()


def verify_password(stored_hash: str, password: str) -> tuple[bool, bool]:
    if stored_hash.startswith("$argon2"):
        try:
            valid = _hasher.verify(stored_hash, password)
            return valid, valid and _hasher.check_needs_rehash(stored_hash)
        except (VerifyMismatchError, InvalidHashError):
            return False, False
    try:
        return check_password_hash(stored_hash, password), True
    except ValueError:
        return False, False


def hash_password(password: str) -> str:
    return _hasher.hash(password)
