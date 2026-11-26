from django.urls import path

from . import views

urlpatterns = [
    path("login", views.iniciar_sesion, name="login"),
    path("me", views.sesion_actual, name="me"),
    path("csrf", views.csrf, name="csrf"),
    path("logout", views.cerrar_sesion, name="logout"),
]
