from rest_framework import serializers

from .models import Empleado


class EmpleadoListaSerializer(serializers.ModelSerializer):
    employee_number = serializers.CharField(source="numero_legajo", allow_null=True)
    display_name = serializers.CharField()
    company = serializers.CharField(source="empresa", allow_null=True)
    position = serializers.CharField(source="puesto", allow_null=True)

    class Meta:
        model = Empleado
        fields = ["id", "employee_number", "display_name", "company", "sector", "position"]


class EmpleadoDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = [
            "id", "numero_legajo", "numero_documento", "nombre", "apellido",
            "nombre_completo", "empresa", "sector", "puesto", "fecha_ingreso",
            "correo", "telefono", "fecha_nacimiento", "sexo", "domicilio",
            "provincia", "codigo_postal", "cuil", "licencia_conducir",
        ]
