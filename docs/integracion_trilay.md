# Integracion Trilay -> rrhh.empleados2

La tabla `rrhh.empleados2` es una replica limpia e independiente de `erp.dbo.Usuario`. No reemplaza, vincula ni modifica `rrhh.empleados`.

## Estado

- Migracion `migrations/20261102_create_empleados2.sql`: aplicada el 02/11/2026.
- Carga de Trilay: 411 filas, todas con `id_usuario` unico.
- Nomina maestra del 05/11/2026: 640 filas importadas desde la hoja `EMPLEADOS POR DNI`.
- Total consolidado en `rrhh.empleados2`: 650 filas (401 compartidas por nomina y Trilay, 239 exclusivas de nomina y 10 exclusivas de Trilay).
- Tabla original `rrhh.empleados`: conservada con 335 filas durante la verificacion.
- SQL Server: solo se ejecuta un `SELECT` con columnas explicitas.

La consulta automatica a Trilay excluye contraseña, hashes, IP y datos de autenticacion. La nomina maestra incorpora sus columnas administrativas, salariales y bancarias únicamente en PostgreSQL; no se exponen en vistas generales. La lista consultada a Trilay esta en `integrations/trilay/empleados2.py`.

## Sincronizacion

`idUsuario` es la clave estable. PostgreSQL utiliza `INSERT ... ON CONFLICT DO UPDATE`; por eso repetir el proceso no duplica filas. Los registros que dejan de aparecer no se eliminan: quedan con `presente_en_origen=false`.

Las filas sin `idUsuario` se identifican mediante `nomina_referencia`. En nuevas altas provenientes solo de Trilay, los campos exclusivos de la nomina permanecen vacios.

Ejecucion unica:

```powershell
python trilay_sync.py --apply
```

Worker cada una hora:

```powershell
python trilay_sync.py --apply --worker
```

El worker debe desplegarse como servicio o tarea programada del servidor. Requiere `TRILAY_SYNC_ENABLED=true` y usa `TRILAY_SYNC_INTERVAL_SECONDS=3600`. Un advisory lock de PostgreSQL impide ejecuciones simultaneas.

La aplicacion continua operativa si Trilay se desconecta; el worker registra el error y ninguna fila existente se elimina o sobrescribe durante una conexion fallida.
