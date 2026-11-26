from rest_framework.permissions import BasePermission


class TieneRol(BasePermission):
    roles: set[str] = set()

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol.nombre in self.roles)


class GestionPersonas(TieneRol):
    roles = {"administrador", "recursos_humanos", "gerencia"}
