from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.http import FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from notificaciones.models import Notificacion
from usuarios.models import Usuario

from .models import EmpleadoSupervisor, SolicitudLicencia, TipoLicencia
from .serializers import CrearLicenciaSerializer, ResolucionLicenciaSerializer, SolicitudLicenciaSerializer, TipoLicenciaSerializer

MANAGEMENT_ROLES = {"administrador", "recursos_humanos"}
ALLOWED_CONTENT_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "image/jpeg", "image/png"}


def _supervised_employee_ids(user):
    if not user.empleado2_id:
        return set()
    source_ids = EmpleadoSupervisor.objects.filter(supervisor_empleado2_id=user.empleado2_id, activo=True).values_list("empleado2_id", flat=True)
    return set(Usuario.objects.filter(empleado2_id__in=source_ids, empleado_id__isnull=False).values_list("empleado_id", flat=True))


def _notify(users, title, message, reference, reference_type):
    now = timezone.now()
    for user in users:
        Notificacion.objects.get_or_create(
            usuario_id=user.id, referencia_tipo=reference_type, referencia_id=reference,
            defaults={"titulo": title, "mensaje": message, "tipo": "licencia", "leida": False, "creado_en": now},
        )


def _save_attachment(upload):
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        return None, "unsupported_file_type"
    if upload.size > 10 * 1024 * 1024:
        return None, "file_too_large"
    safe_name = Path(upload.name).name.replace(" ", "_")
    relative = Path("licenses") / f"{uuid4().hex}_{safe_name}"
    target = (settings.MEDIA_ROOT / relative).resolve()
    root = settings.MEDIA_ROOT.resolve()
    if root not in target.parents:
        return None, "invalid_storage_path"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as destination:
        for chunk in upload.chunks():
            destination.write(chunk)
    return str(relative), None


@api_view(["GET"])
def tipos(request):
    queryset = TipoLicencia.objects.filter(activo=True).order_by("nombre")
    return Response(TipoLicenciaSerializer(queryset, many=True).data)


@api_view(["GET"])
def listar(request):
    queryset = SolicitudLicencia.objects.select_related("empleado", "tipo_licencia").order_by("-fecha_desde")
    if request.user.rol.nombre not in MANAGEMENT_ROLES:
        allowed = _supervised_employee_ids(request.user)
        if request.user.empleado_id:
            allowed.add(request.user.empleado_id)
        queryset = queryset.filter(empleado_id__in=allowed) if allowed else queryset.none()
    return Response(SolicitudLicenciaSerializer(queryset, many=True).data)


@api_view(["POST"])
def crear(request):
    if not request.user.empleado_id:
        return Response({"detail": "user_has_no_employee"}, status=status.HTTP_409_CONFLICT)
    serializer = CrearLicenciaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    leave_type = TipoLicencia.objects.filter(pk=serializer.validated_data["type_id"], activo=True).first()
    if not leave_type:
        return Response({"detail": "invalid_leave_type"}, status=status.HTTP_400_BAD_REQUEST)
    attachment = request.FILES.get("attachment")
    if leave_type.requiere_adjunto and not attachment:
        return Response({"detail": "attachment_required"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    attachment_path = None
    if attachment:
        attachment_path, error = _save_attachment(attachment)
        if error:
            code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE if error == "file_too_large" else status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            return Response({"detail": error}, status=code)
    supervisors = EmpleadoSupervisor.objects.filter(empleado2_id=request.user.empleado2_id, activo=True) if request.user.empleado2_id else EmpleadoSupervisor.objects.none()
    vacation = "vacacion" in leave_type.nombre.lower().replace("ó", "o")
    supervisor_status = "Pendiente" if vacation and supervisors.exists() else ("Sin asignar" if vacation else "No requerido")
    with transaction.atomic():
        item = SolicitudLicencia.objects.create(
            empleado_id=request.user.empleado_id, tipo_licencia=leave_type,
            fecha_desde=serializer.validated_data["date_from"], fecha_hasta=serializer.validated_data["date_to"],
            cantidad_dias=serializer.validated_data["days"], motivo=serializer.validated_data.get("reason"),
            archivo_adjunto=attachment_path, estado="Pendiente", estado_supervisor=supervisor_status, creado_en=timezone.now(),
        )
        if supervisor_status == "Pendiente":
            targets = supervisors.values_list("supervisor_empleado2_id", flat=True)
            recipients = Usuario.objects.filter(empleado2_id__in=targets, activo=True)
            reference_type = "license_supervisor"
        else:
            recipients = Usuario.objects.filter(rol__nombre="recursos_humanos", activo=True)
            reference_type = "license_no_supervisor" if supervisor_status == "Sin asignar" else "license_hr"
        _notify(recipients, "Nueva solicitud de licencia", f"{item.empleado.nombre_apellido} solicitó {leave_type.nombre}.", item.id, reference_type)
    item = SolicitudLicencia.objects.select_related("empleado", "tipo_licencia").get(pk=item.pk)
    return Response(SolicitudLicenciaSerializer(item).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def resolver_supervisor(request, leave_id):
    payload = ResolucionLicenciaSerializer(data=request.data)
    payload.is_valid(raise_exception=True)
    item = SolicitudLicencia.objects.select_related("empleado", "tipo_licencia").filter(pk=leave_id).first()
    if not item:
        return Response({"detail": "license_not_found"}, status=status.HTTP_404_NOT_FOUND)
    if item.empleado_id not in _supervised_employee_ids(request.user) or item.estado != "Pendiente" or item.estado_supervisor != "Pendiente":
        return Response({"detail": "license_not_available_for_supervisor"}, status=status.HTTP_403_FORBIDDEN)
    item.estado_supervisor = payload.validated_data["decision"]
    item.supervisor_resuelto_por = request.user.id
    item.fecha_resolucion_supervisor = timezone.now()
    item.observacion_supervisor = payload.validated_data.get("observation")
    owner = Usuario.objects.filter(empleado_id=item.empleado_id, activo=True).first()
    if item.estado_supervisor == "Rechazada":
        item.estado, item.fecha_resolucion = "Rechazada", timezone.now()
        if owner: _notify([owner], "Actualización de vacaciones", "Tu solicitud fue rechazada por supervisión.", item.id, "license_supervisor_result")
    else:
        _notify(Usuario.objects.filter(rol__nombre="recursos_humanos", activo=True), "Vacaciones aprobadas por supervisión", f"{item.empleado.nombre_apellido} tiene una solicitud pendiente.", item.id, "license_hr")
        if owner: _notify([owner], "Actualización de vacaciones", "Tu supervisor aprobó la solicitud. Ahora será revisada por RR. HH.", item.id, "license_supervisor_result")
    item.save()
    return Response(SolicitudLicenciaSerializer(item).data)


@api_view(["POST"])
def resolver_rrhh(request, leave_id):
    if request.user.rol.nombre not in MANAGEMENT_ROLES:
        return Response({"detail": "permission_denied"}, status=status.HTTP_403_FORBIDDEN)
    payload = ResolucionLicenciaSerializer(data=request.data)
    payload.is_valid(raise_exception=True)
    item = SolicitudLicencia.objects.select_related("empleado", "tipo_licencia").filter(pk=leave_id).first()
    if not item:
        return Response({"detail": "license_not_found"}, status=status.HTTP_404_NOT_FOUND)
    if item.estado != "Pendiente" or item.estado_supervisor not in {"Aprobada", "No requerido", "Sin asignar"}:
        return Response({"detail": "license_not_ready_for_hr"}, status=status.HTTP_409_CONFLICT)
    item.estado = payload.validated_data["decision"]
    item.observacion_rrhh = payload.validated_data.get("observation")
    item.aprobado_por, item.fecha_resolucion = request.user.id, timezone.now()
    item.save()
    owner = Usuario.objects.filter(empleado_id=item.empleado_id, activo=True).first()
    if owner: _notify([owner], f"Licencia {item.estado.lower()}", f"Tu solicitud fue {item.estado.lower()} por RR. HH.", item.id, "license")
    return Response(SolicitudLicenciaSerializer(item).data)


@api_view(["GET"])
def adjunto(request, leave_id):
    item = SolicitudLicencia.objects.filter(pk=leave_id).first()
    allowed = item and (request.user.rol.nombre in MANAGEMENT_ROLES or request.user.empleado_id == item.empleado_id or item.empleado_id in _supervised_employee_ids(request.user))
    if not allowed or not item.archivo_adjunto:
        return Response({"detail": "attachment_not_found"}, status=status.HTTP_404_NOT_FOUND)
    target = (settings.MEDIA_ROOT / item.archivo_adjunto).resolve()
    if settings.MEDIA_ROOT.resolve() not in target.parents or not target.is_file():
        return Response({"detail": "attachment_not_found"}, status=status.HTTP_404_NOT_FOUND)
    return FileResponse(target.open("rb"), as_attachment=True, filename=target.name)
