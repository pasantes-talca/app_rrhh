from django.urls import include, path
from notificaciones import views as self_service_views

from core.views import health

urlpatterns = [
    path("api/v1/health", health, name="health"),
    path("api/v1/auth/", include("usuarios.urls")),
    path("api/v1/employees/", include("empleados.urls")),
    path("api/v1/vacations/", include("vacaciones.urls")),
    path("api/v1/licenses/", include("licencias.urls")),
    path("api/v1/absence/", include("ausentismo.urls")),
    path("api/v1/overtime/", include("horas_extra.urls")),
    path("api/v1/news/", include("noticias.urls")),
    path("api/v1/sanctions/", include("sanciones.urls")),
    path("api/v1/documents/", include("documentos.urls")),
    path("api/v1/notifications/", include("notificaciones.urls")),
    path("api/v1/checklist", self_service_views.checklist, name="checklist"),
    path("api/v1/checklist/<int:task_id>/toggle", self_service_views.alternar_tarea, name="checklist-toggle"),
    path("api/v1/checklist/<int:task_id>", self_service_views.eliminar_tarea, name="checklist-delete"),
    path("api/v1/administration/", include("administracion.urls")),
    path("api/v1/organization/", include("estructura.urls")),
    path("api/v1/indicators/", include("indicadores.urls")),
    path("api/v1/dashboard/", include("dashboard.urls")),
    path("api/v1/profile/", include("perfil.urls")),
]
