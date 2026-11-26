from django.db import models


class Notificacion(models.Model):
    usuario_id = models.IntegerField()
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50)
    referencia_tipo = models.CharField(max_length=50, null=True, blank=True)
    referencia_id = models.IntegerField(null=True, blank=True)
    leida = models.BooleanField(default=False)
    leida_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'rrhh"."notificaciones'


class TareaChecklist(models.Model):
    usuario_id = models.IntegerField()
    descripcion = models.CharField(max_length=250)
    completada = models.BooleanField(default=False)
    creado_en = models.DateTimeField()
    completado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'rrhh"."tareas_checklist'
