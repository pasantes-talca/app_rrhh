from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from werkzeug.security import check_password_hash

from .models import Usuario

_hasher = PasswordHasher()


def verify_password(stored_hash: str, password: str) -> bool:
    if stored_hash.startswith("$argon2"):
        try:
            return _hasher.verify(stored_hash, password)
        except (VerifyMismatchError, InvalidHashError):
            return False
    try:
        return check_password_hash(stored_hash, password)
    except ValueError:
        return False


class LegacyPasswordBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        try:
            user = Usuario.objects.select_related("rol").prefetch_related("permisos_asignados").get(usuario__iexact=username.strip(), activo=True)
        except Usuario.DoesNotExist:
            return None
        return user if verify_password(user.password, password) else None

    def get_user(self, user_id):
        try:
            return Usuario.objects.select_related("rol").prefetch_related("permisos_asignados").get(pk=user_id, activo=True)
        except Usuario.DoesNotExist:
            return None
