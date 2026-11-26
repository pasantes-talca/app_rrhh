from django.urls import path

from . import views

urlpatterns = [
    path("summary", views.resumen, name="vacaciones-resumen"),
    path("calendar", views.calendario, name="vacaciones-calendario"),
]
