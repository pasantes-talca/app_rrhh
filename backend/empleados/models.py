from django.db import models


class Empleado(models.Model):
    id_usuario = models.BigIntegerField(null=True, blank=True, unique=True)
    numero_legajo = models.CharField(max_length=100, null=True, blank=True)
    numero_documento = models.CharField(max_length=100, null=True, blank=True)
    nombre = models.CharField(max_length=150, null=True, blank=True)
    apellido = models.CharField(max_length=150, null=True, blank=True)
    nombre_completo = models.CharField(max_length=350, null=True, blank=True)
    empresa = models.CharField(max_length=150, null=True, blank=True)
    sector = models.CharField(max_length=150, null=True, blank=True)
    puesto = models.CharField(max_length=150, null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    presente_en_origen = models.BooleanField(default=False)
    correo = models.EmailField(max_length=120, null=True, blank=True)
    telefono = models.CharField(max_length=100, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=50, null=True, blank=True)
    domicilio = models.CharField(max_length=300, null=True, blank=True)
    provincia = models.CharField(max_length=100, null=True, blank=True)
    codigo_postal = models.CharField(max_length=20, null=True, blank=True)
    cuil = models.CharField(max_length=100, null=True, blank=True)
    licencia_conducir = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'rrhh"."empleados2'

    @property
    def display_name(self):
        return self.nombre_completo or f"{self.apellido or ''} {self.nombre or ''}".strip()
