# Plan reversible de retiro de Flask

Flask continúa siendo el sistema de respaldo. No debe eliminarse mientras la matriz de paridad contenga filas parciales.

## Etapas

1. Ejecutar React/FastAPI en QA con una copia anonimizada de PostgreSQL.
2. Mantener Flask disponible en una ruta interna separada y comparar resultados.
3. Cerrar brechas de identidad, acciones masivas, indicadores y pruebas E2E.
4. Congelar cambios funcionales durante la validación final.
5. Crear backup de base, uploads y versión del repositorio.
6. Cambiar el proxy de QA hacia la arquitectura nueva y ejecutar smoke tests.
7. Documentar aceptación y ventana de reversión.
8. Retirar código Flask en un cambio separado, revisable y reversible.

## Rollback

- Restaurar la configuración anterior del proxy.
- Volver a la versión Flask preservada.
- No revertir datos automáticamente: evaluar primero escrituras realizadas por la nueva API.
- Conservar logs de auditoría y evidencias del incidente.

## Elementos que sí pueden limpiarse durante la migración

- Builds locales (`frontend/dist`).
- Metadatos de instalación (`*.egg-info`).
- Cachés y `*.tsbuildinfo`.
- Archivos temporales sin datos corporativos.

