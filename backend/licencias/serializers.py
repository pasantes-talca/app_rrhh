from rest_framework import serializers

from .models import SolicitudLicencia, TipoLicencia


class TipoLicenciaSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="nombre")
    description = serializers.CharField(source="descripcion", allow_null=True)
    attachment_required = serializers.BooleanField(source="requiere_adjunto")

    class Meta:
        model = TipoLicencia
        fields = ["id", "name", "description", "attachment_required"]


class SolicitudLicenciaSerializer(serializers.ModelSerializer):
    employee_id = serializers.IntegerField(source="empleado_id")
    employee_name = serializers.CharField(source="empleado.nombre_apellido")
    type_id = serializers.IntegerField(source="tipo_licencia_id")
    type_name = serializers.CharField(source="tipo_licencia.nombre")
    date_from = serializers.DateField(source="fecha_desde")
    date_to = serializers.DateField(source="fecha_hasta")
    days = serializers.DecimalField(source="cantidad_dias", max_digits=10, decimal_places=2, allow_null=True)
    reason = serializers.CharField(source="motivo", allow_null=True)
    status = serializers.CharField(source="estado")
    supervisor_status = serializers.CharField(source="estado_supervisor")
    hr_observation = serializers.CharField(source="observacion_rrhh", allow_null=True)
    supervisor_observation = serializers.CharField(source="observacion_supervisor", allow_null=True)
    has_attachment = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source="creado_en")

    class Meta:
        model = SolicitudLicencia
        fields = ["id", "employee_id", "employee_name", "type_id", "type_name", "date_from", "date_to", "days", "reason", "status", "supervisor_status", "hr_observation", "supervisor_observation", "has_attachment", "created_at"]

    def get_has_attachment(self, obj):
        return bool(obj.archivo_adjunto)


class CrearLicenciaSerializer(serializers.Serializer):
    type_id = serializers.IntegerField(min_value=1)
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    days = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1, max_value=365)
    reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        if attrs["date_to"] < attrs["date_from"]:
            raise serializers.ValidationError("invalid_leave_period")
        return attrs


class ResolucionLicenciaSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=["Aprobada", "Rechazada"])
    observation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
