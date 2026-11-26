# Migración de FastAPI a Django REST Framework

Fecha de inicio: 26 de noviembre de 2026.

## Decisión

Por pedido explícito se adopta la arquitectura del sistema de Logística y Expedición:

- `backend/manage.py` como punto de entrada.
- `backend/config/` para configuración, ASGI, WSGI y enrutamiento.
- Una aplicación Django por dominio, ubicada directamente dentro de `backend/`.
- Django REST Framework para `/api/v1`.
- React, TypeScript y Vite en `frontend/`.

Se conserva PostgreSQL y la integración SQL Server en modo de solo lectura. No se recrean ni eliminan tablas existentes.

## Estrategia segura

FastAPI permanece temporalmente en `backend/app/` mientras se trasladan y verifican sus contratos. No debe retirarse hasta que cada endpoint consumido por React tenga una implementación Django equivalente y pruebas positivas, negativas y de autorización.

## Estado actual

- Django instalado y configurado.
- Health check Django verificado.
- Autenticación compatible con hashes Argon2 y Werkzeug implementada.
- Modelos no administrados para `rrhh.roles`, `rrhh.usuarios`, `rrhh.permisos_usuario` y `rrhh.empleados2`.
- Directorio de empleados implementado con permisos backend.
- Aplicaciones de dominio y rutas base creadas.
- FastAPI preservado para comparación y rollback.

## Condición de retiro de FastAPI

1. Paridad de todos los contratos `/api/v1`.
2. Pruebas por rol y objeto.
3. Comparación contra PostgreSQL QA anonimizado.
4. Validación de archivos, saldos, jerarquías e integraciones.
5. Aceptación funcional y ensayo de rollback.
