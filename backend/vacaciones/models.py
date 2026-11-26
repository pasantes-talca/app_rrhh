from django.db import models

from empleados.models import Empleado


class SaldoVacaciones(models.Model):
    empleado = models.ForeignKey(Empleado, db_column="empleado2_id", on_delete=models.DO_NOTHING)
    periodo = models.IntegerField()
    fecha_ingreso_calculo = models.DateField(null=True, blank=True)
    antiguedad_meses = models.IntegerField(null=True, blank=True)
    dias_correspondientes = models.DecimalField(max_digits=8, decimal_places=2)
    saldo_base = models.DecimalField(max_digits=8, decimal_places=2)
    ajustes = models.DecimalField(max_digits=8, decimal_places=2)
    saldo_disponible = models.DecimalField(max_digits=8, decimal_places=2)
    origen = models.CharField(max_length=30)
    fecha_corte = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'rrhh"."vacaciones_saldos'


class MovimientoVacaciones(models.Model):
    empleado = models.ForeignKey(Empleado, db_column="empleado2_id", on_delete=models.DO_NOTHING)
    saldo_id = models.BigIntegerField(null=True, blank=True)
    licencia_id = models.IntegerField(null=True, blank=True)
    tipo = models.CharField(max_length=40)
    fecha_desde = models.DateField(null=True, blank=True)
    fecha_hasta = models.DateField(null=True, blank=True)
    fecha_reintegro = models.DateField(null=True, blank=True)
    dias = models.DecimalField(max_digits=8, decimal_places=2)
    saldo_resultante = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    detalle = models.TextField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    origen = models.CharField(max_length=30)
    referencia_origen = models.CharField(max_length=100)
    creado_en = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'rrhh"."vacaciones_movimientos'
