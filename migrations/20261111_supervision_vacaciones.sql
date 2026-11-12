CREATE TABLE IF NOT EXISTS rrhh.empleados_supervisores (
    id BIGSERIAL PRIMARY KEY,
    empleado2_id BIGINT NOT NULL REFERENCES rrhh.empleados2(id) ON DELETE CASCADE,
    supervisor_empleado2_id BIGINT NOT NULL REFERENCES rrhh.empleados2(id) ON DELETE CASCADE,
    es_principal BOOLEAN NOT NULL DEFAULT FALSE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_desde DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_hasta DATE,
    origen VARCHAR(50) NOT NULL DEFAULT 'ORGANIGRAMA',
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_empleado_supervisor UNIQUE (empleado2_id, supervisor_empleado2_id),
    CONSTRAINT ck_supervisor_no_autorreferencia CHECK (empleado2_id <> supervisor_empleado2_id)
);
CREATE INDEX IF NOT EXISTS ix_empleados_supervisores_empleado ON rrhh.empleados_supervisores (empleado2_id);
CREATE INDEX IF NOT EXISTS ix_empleados_supervisores_supervisor ON rrhh.empleados_supervisores (supervisor_empleado2_id);

ALTER TABLE rrhh.licencias ADD COLUMN IF NOT EXISTS estado_supervisor VARCHAR(30) NOT NULL DEFAULT 'No requerido';
ALTER TABLE rrhh.licencias ADD COLUMN IF NOT EXISTS supervisor_resuelto_por INTEGER REFERENCES rrhh.usuarios(id);
ALTER TABLE rrhh.licencias ADD COLUMN IF NOT EXISTS fecha_resolucion_supervisor TIMESTAMP;
ALTER TABLE rrhh.licencias ADD COLUMN IF NOT EXISTS observacion_supervisor TEXT;

-- Los operarios de Producción dependen del equipo de cuatro supervisores
-- representado en el organigrama. Cualquiera puede realizar la primera revisión.
DELETE FROM rrhh.empleados_supervisores relacion
WHERE relacion.origen = 'ORGANIGRAMA_2026-10-08'
  AND relacion.empleado2_id NOT IN (
      SELECT empleado2_id FROM rrhh.usuarios
      WHERE usuario IN (
          'gsalinas','cgarcia','aantonucci','gmontiel','ldanilo',
          'aeduardo','sborquez','asosa','agauna','agutierrez',
          'jescobar','egonzalez','flopez','msanchez','fcampillay'
      )
  );

INSERT INTO rrhh.empleados_supervisores
    (empleado2_id, supervisor_empleado2_id, es_principal, activo, origen)
SELECT empleado.id, supervisor.id, FALSE, TRUE, 'ORGANIGRAMA_2026-10-08'
FROM rrhh.usuarios cuenta_empleado
JOIN rrhh.empleados2 empleado ON empleado.id = cuenta_empleado.empleado2_id
CROSS JOIN rrhh.empleados2 supervisor
WHERE cuenta_empleado.usuario IN (
    'gsalinas','cgarcia','aantonucci','gmontiel','ldanilo',
    'aeduardo','sborquez','asosa','agauna','agutierrez',
    'jescobar','egonzalez','flopez','msanchez','fcampillay'
)
AND supervisor.numero_legajo IN ('1740','1512','1797','1965')
AND empleado.presente_en_origen = TRUE
AND supervisor.presente_en_origen = TRUE
ON CONFLICT (empleado2_id, supervisor_empleado2_id) DO UPDATE
SET activo = TRUE, fecha_hasta = NULL, origen = EXCLUDED.origen;
