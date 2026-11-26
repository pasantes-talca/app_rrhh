from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .serializers import LoginSerializer, UsuarioSerializer


@csrf_exempt
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def iniciar_sesion(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(
        request,
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response({"detail": "invalid_credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    login(request, user)
    return Response({"user": UsuarioSerializer(user).data, "csrf_token": get_token(request)})


@api_view(["GET"])
def sesion_actual(request):
    return Response(UsuarioSerializer(request.user).data)


@api_view(["GET"])
def csrf(request):
    return Response({"csrf_token": get_token(request)})


@api_view(["POST"])
def cerrar_sesion(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)
