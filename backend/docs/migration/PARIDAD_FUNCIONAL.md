# Paridad funcional de la migración

Fecha de revisión: 2026-11-25.

Este documento evita retirar Flask por intuición. `Verificado` significa que existe API FastAPI, pantalla React y una validación automatizada aplicable. `Parcial` significa que el reemplazo existe, pero todavía falta una prueba de integración o una variante del flujo original.

| Módulo | API FastAPI | React | Estado | Observación pendiente |
|---|---:|---:|---|---|
| Autenticación, sesión, CSRF y cambio de clave | Sí | Sí | Parcial | Falta E2E con PostgreSQL QA y rate limiting distribuido. |
| Dashboard, calendario y checklist | Sí | Sí | Parcial | Falta comparación visual/E2E con datos QA. |
| Tema visual claro/oscuro | N/A | Sí | Parcial | Preferencia persistente y contraste global migrados; falta auditoría visual y de accesibilidad en todos los módulos. |
| Notificaciones y avisos diarios | Sí | Sí | Parcial | La generación es idempotente al consultar dashboard/notificaciones; falta ejecución programada independiente. |
| Empleados2: directorio y ficha | Sí | Sí | Parcial | Solo lectura deliberada. No se unifica ni edita `Empleado`/`Empleado2` sin autorización. |
| Perfil personal y foto | Sí | Sí | Parcial | Escribe sobre `Empleado` legado; falta decisión canónica para usuarios vinculados únicamente a `Empleado2`. |
| Estructura organizacional | Sí | Sí | Parcial | Datos trasladados del organigrama verificado; falta fuente administrable. |
| Vacaciones: saldo y calendario | Sí | Sí | Parcial | Falta conciliación QA contra el Excel/Veotime y circuito completo de solicitud. |
| Licencias y aprobación supervisor/RR. HH. | Sí | Sí | Parcial | Falta prueba integral con jerarquías reales y múltiples supervisores. |
| Ausentismo | Sí | Sí | Parcial | Falta CRUD/importación operativa y prueba con dataset QA completo. |
| Indicadores de ausentismo | Sí | Sí | Parcial | Gráficos migrados; falta vista de indicadores de vacaciones. |
| Horas extra | Sí | Sí | Parcial | API cubre carga, importación, aprobación, rechazo, exportación y limpieza; falta exponer todas las acciones masivas en React. |
| Noticias | Sí | Sí | Parcial | Publicación/edición/eliminación e imagen migradas; falta E2E de segmentación. |
| Fechas importantes | Sí | Sí | Parcial | CRUD básico migrado; falta edición y carga oficial automatizada por año. |
| Sanciones | Sí | Sí | Parcial | Alta/edición/archivo y vencimiento migrados; falta detalle dedicado/E2E. |
| Documentos y carpetas por empleado | Sí | Sí | Parcial | Alta, edición, reemplazo, archivo y acceso migrados. Eliminación física queda bloqueada por la política de no borrar registros. |
| Recibos de sueldo | Sí | Sí | Parcial | Publicación, lectura y respuesta migradas; falta firma digital con validez jurídica, si RR. HH. la exige. |
| Administración de usuarios | Sí | Sí | Parcial | Cuentas protegidas, roles, claves, permisos, auditoría, errores, sesiones, seguridad, estado y reportes migrados; falta E2E. |
| Integración Trilay | Reutilizada | N/A | Parcial | Se mantiene solo lectura e idempotente. Falta ejecutar prueba controlada en QA con SQL Server accesible. |

## Condiciones para retirar Flask

1. Probar cada fila parcial contra una base QA anonimizada.
2. Ejecutar E2E por rol: empleado, supervisor, RR. HH., gerencia y administrador.
3. Comparar saldos, conteos, estados, archivos y autorizaciones entre ambas versiones.
4. Aprobar la identidad canónica entre `Empleado` y `Empleado2`.
5. Realizar backup, ensayo de rollback y aceptación de RR. HH./Sistemas.
6. Recién entonces retirar rutas, templates, static y dependencias Flask reemplazadas.

