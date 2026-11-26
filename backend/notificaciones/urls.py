from django.urls import path

from . import views

urlpatterns = [
    path("", views.listar, name="notificaciones-lista"),
    path("<int:notification_id>/read", views.marcar_leida, name="notificaciones-leer"),
    path("read-all", views.marcar_todas, name="notificaciones-leer-todas"),
]
