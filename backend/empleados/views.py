from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from usuarios.permissions import GestionPersonas

from .models import Empleado
from .serializers import EmpleadoDetalleSerializer, EmpleadoListaSerializer


@api_view(["GET"])
@permission_classes([GestionPersonas])
def listar(request):
    query = request.query_params.get("q", "").strip()
    page_number = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(max(int(request.query_params.get("page_size", 30)), 1), 100)
    queryset = Empleado.objects.all().order_by("apellido", "nombre", "id")
    if query:
        queryset = queryset.filter(
            Q(nombre_completo__icontains=query)
            | Q(nombre__icontains=query)
            | Q(apellido__icontains=query)
            | Q(numero_legajo__icontains=query)
            | Q(numero_documento__icontains=query)
        )
    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_number)
    return Response({
        "items": EmpleadoListaSerializer(page.object_list, many=True).data,
        "total": paginator.count,
        "page": page.number,
        "page_size": page_size,
    })


@api_view(["GET"])
@permission_classes([GestionPersonas])
def detalle(request, employee_id):
    employee = Empleado.objects.get(pk=employee_id)
    return Response(EmpleadoDetalleSerializer(employee).data)
