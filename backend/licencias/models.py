from django.db import models


class EmpleadoLegacy(models.Model):
    nombre_apellido = models.CharField(max_length=150)
    legajo = models.CharField(max_length=50, null=True, blank=True)
    dni = models.CharField(max_length=20)
    estado = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'rrhh"."empleados'


class TipoLicencia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    requiere_adjunto = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'rrhh"."tipos_licencia'


class SolicitudLicencia(models.Model):
    empleado = models.ForeignKey(EmpleadoLegacy, db_column="empleado_id", on_delete=models.DO_NOTHING)
    tipo_licencia = models.ForeignKey(TipoLicencia, db_column="tipo_licencia_id", on_delete=models.DO_NOTHING)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    cantidad_dias = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    motivo = models.TextField(null=True, blank=True)
    archivo_adjunto = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=50)
    estado_supervisor = models.CharField(max_length=30)
    observacion_rrhh = models.TextField(null=True, blank=True)
    observacion_supervisor = models.TextField(null=True, blank=True)
    aprobado_por = models.IntegerField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    supervisor_resuelto_por = models.IntegerField(null=True, blank=True)
    fecha_resolucion_supervisor = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'rrhh"."licencias'


class EmpleadoSupervisor(models.Model):
    empleado2_id = models.BigIntegerField()
    supervisor_empleado2_id = models.BigIntegerField()
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'rrhh"."empleados_supervisores'
