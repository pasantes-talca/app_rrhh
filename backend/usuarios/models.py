from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'rrhh"."roles'


class UsuarioManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(usuario__iexact=username)


class Usuario(AbstractBaseUser):
    empleado_id = models.IntegerField(null=True, blank=True)
    empleado2_id = models.BigIntegerField(null=True, blank=True)
    rol = models.ForeignKey(Rol, db_column="rol_id", on_delete=models.DO_NOTHING)
    usuario = models.CharField(max_length=100, unique=True)
    nombre_mostrar = models.CharField(max_length=150, null=True, blank=True)
    correo = models.EmailField(max_length=150, null=True, blank=True)
    foto_perfil = models.CharField(max_length=255, null=True, blank=True)
    cuenta_protegida = models.BooleanField(default=False)
    password = models.TextField(db_column="password_hash")
    activo = models.BooleanField(default=True)
    debe_cambiar_password = models.BooleanField(default=False)
    last_login = models.DateTimeField(db_column="ultimo_acceso", null=True, blank=True)
    creado_en = models.DateTimeField()

    USERNAME_FIELD = "usuario"
    objects = UsuarioManager()

    class Meta:
        managed = False
        db_table = 'rrhh"."usuarios'

    @property
    def is_staff(self):
        return self.rol.nombre == "administrador"

    @property
    def is_active(self):
        return self.activo


class PermisoUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, db_column="usuario_id", on_delete=models.DO_NOTHING, related_name="permisos_asignados")
    modulo = models.CharField(max_length=50)
    accion = models.CharField(max_length=30)
    permitido = models.BooleanField(default=False)
    asignado_por = models.IntegerField(null=True, blank=True)
    actualizado_en = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'rrhh"."permisos_usuario'
