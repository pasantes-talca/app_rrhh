from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Notificacion, TareaChecklist


def _notification(item):
    return {"id": item.id, "title": item.titulo, "message": item.mensaje, "kind": item.tipo, "read": item.leida, "created_at": item.creado_en}


def _task(item):
    return {"id": item.id, "description": item.descripcion, "completed": item.completada, "created_at": item.creado_en, "completed_at": item.completado_en}


class TaskInput(serializers.Serializer):
    description = serializers.CharField(min_length=1, max_length=250)


@api_view(["GET"])
def listar(request):
    rows = Notificacion.objects.filter(usuario_id=request.user.id).order_by("-creado_en")[:100]
    return Response([_notification(row) for row in rows])


@api_view(["POST"])
def marcar_leida(request, notification_id):
    updated = Notificacion.objects.filter(pk=notification_id, usuario_id=request.user.id).update(leida=True, leida_en=timezone.now())
    return Response(status=status.HTTP_204_NO_CONTENT if updated else status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def marcar_todas(request):
    Notificacion.objects.filter(usuario_id=request.user.id, leida=False).update(leida=True, leida_en=timezone.now())
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def checklist(request):
    if request.method == "GET":
        rows = TareaChecklist.objects.filter(usuario_id=request.user.id).order_by("completada", "-creado_en")
        return Response([_task(row) for row in rows])
    payload = TaskInput(data=request.data)
    payload.is_valid(raise_exception=True)
    row = TareaChecklist.objects.create(usuario_id=request.user.id, descripcion=payload.validated_data["description"].strip(), completada=False, creado_en=timezone.now())
    return Response(_task(row), status=status.HTTP_201_CREATED)


@api_view(["POST"])
def alternar_tarea(request, task_id):
    row = TareaChecklist.objects.filter(pk=task_id, usuario_id=request.user.id).first()
    if not row:
        return Response({"detail": "task_not_found"}, status=status.HTTP_404_NOT_FOUND)
    row.completada = not row.completada
    row.completado_en = timezone.now() if row.completada else None
    row.save(update_fields=["completada", "completado_en"])
    return Response(_task(row))


@api_view(["DELETE"])
def eliminar_tarea(request, task_id):
    deleted, _ = TareaChecklist.objects.filter(pk=task_id, usuario_id=request.user.id).delete()
    return Response(status=status.HTTP_204_NO_CONTENT if deleted else status.HTTP_404_NOT_FOUND)
