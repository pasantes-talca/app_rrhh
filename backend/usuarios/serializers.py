from rest_framework import serializers

from .models import Usuario


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=256, write_only=True)


class UsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="usuario")
    display_name = serializers.CharField(source="nombre_mostrar", allow_null=True)
    role = serializers.CharField(source="rol.nombre")
    employee_id = serializers.IntegerField(source="empleado_id", allow_null=True)
    employee2_id = serializers.IntegerField(source="empleado2_id", allow_null=True)
    must_change_password = serializers.BooleanField(source="debe_cambiar_password")
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ["id", "username", "display_name", "role", "employee_id", "employee2_id", "must_change_password", "permissions"]

    def get_permissions(self, obj):
        return [
            f"{permission.modulo}.{permission.accion}"
            for permission in obj.permisos_asignados.all()
            if permission.permitido
        ]
