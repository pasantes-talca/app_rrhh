CREATE TABLE IF NOT EXISTS rrhh.ausentismo_empleados (
    id BIGSERIAL PRIMARY KEY,
    empleado2_id BIGINT REFERENCES rrhh.empleados2(id) ON DELETE SET NULL,
    legajo VARCHAR(100) NOT NULL UNIQUE,
    nombre VARCHAR(350) NOT NULL,
    area VARCHAR(150),
    planta VARCHAR(150),
    fecha_ingreso DATE,
    fecha_baja DATE,
    fecha_nacimiento DATE,
    archivo_origen VARCHAR(255),
    fila_excel INTEGER,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_ausentismo_empleados_empleado2 ON rrhh.ausentismo_empleados (empleado2_id);
CREATE INDEX IF NOT EXISTS ix_ausentismo_empleados_legajo ON rrhh.ausentismo_empleados (legajo);
CREATE INDEX IF NOT EXISTS ix_ausentismo_empleados_planta ON rrhh.ausentismo_empleados (planta);
