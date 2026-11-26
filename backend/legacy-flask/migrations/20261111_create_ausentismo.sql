CREATE TABLE IF NOT EXISTS rrhh.tipos_ausencia (
    codigo INTEGER PRIMARY KEY,
    categoria VARCHAR(100) NOT NULL,
    descripcion VARCHAR(200) NOT NULL,
    impacto_productividad VARCHAR(100),
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rrhh.ausencias (
    id BIGSERIAL PRIMARY KEY,
    empleado2_id BIGINT REFERENCES rrhh.empleados2(id) ON DELETE RESTRICT,
    tipo_codigo INTEGER NOT NULL REFERENCES rrhh.tipos_ausencia(codigo) ON DELETE RESTRICT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    dias_calendario INTEGER NOT NULL,
    legajo_origen VARCHAR(100) NOT NULL,
    nombre_origen VARCHAR(350),
    area_origen VARCHAR(150),
    planta_origen VARCHAR(150),
    tipo_descripcion_origen VARCHAR(200),
    origen VARCHAR(30) NOT NULL DEFAULT 'SISTEMA',
    referencia_origen VARCHAR(150) NOT NULL,
    archivo_origen VARCHAR(255),
    fila_excel INTEGER,
    observaciones_importacion TEXT,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_ausencias_origen_referencia UNIQUE (origen, referencia_origen),
    CONSTRAINT ck_ausencias_fechas CHECK (fecha_fin >= fecha_inicio)
);

CREATE INDEX IF NOT EXISTS ix_ausencias_empleado2_id ON rrhh.ausencias (empleado2_id);
CREATE INDEX IF NOT EXISTS ix_ausencias_tipo_codigo ON rrhh.ausencias (tipo_codigo);
CREATE INDEX IF NOT EXISTS ix_ausencias_fecha_inicio ON rrhh.ausencias (fecha_inicio);
CREATE INDEX IF NOT EXISTS ix_ausencias_fecha_fin ON rrhh.ausencias (fecha_fin);

-- Compatibilidad si la primera versión de la migración ya fue ejecutada.
ALTER TABLE rrhh.ausencias ALTER COLUMN empleado2_id DROP NOT NULL;
ALTER TABLE rrhh.ausencias ADD COLUMN IF NOT EXISTS observaciones_importacion TEXT;
