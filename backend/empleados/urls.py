from django.urls import path

from . import views

urlpatterns = [
    path("", views.listar, name="empleados-lista"),
    path("<int:employee_id>", views.detalle, name="empleados-detalle"),
]
