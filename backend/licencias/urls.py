from django.urls import path

from . import views

urlpatterns = [
    path("types", views.tipos, name="licencias-tipos"),
    path("", views.listar, name="licencias-lista"),
    path("upload", views.crear, name="licencias-crear"),
    path("<int:leave_id>/supervisor-resolution", views.resolver_supervisor, name="licencias-resolver-supervisor"),
    path("<int:leave_id>/hr-resolution", views.resolver_rrhh, name="licencias-resolver-rrhh"),
    path("<int:leave_id>/attachment", views.adjunto, name="licencias-adjunto"),
]
