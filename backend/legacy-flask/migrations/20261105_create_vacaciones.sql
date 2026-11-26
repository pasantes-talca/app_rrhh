CREATE TABLE IF NOT EXISTS rrhh.vacaciones_saldos (
    id BIGSERIAL PRIMARY KEY,
    empleado2_id BIGINT NOT NULL REFERENCES rrhh.empleados2(id) ON DELETE CASCADE,
    periodo INTEGER NOT NULL,
    fecha_ingreso_calculo DATE,
    antiguedad_meses INTEGER,
    dias_correspondientes NUMERIC(8,2) NOT NULL DEFAULT 0,
    saldo_base NUMERIC(8,2) NOT NULL DEFAULT 0,
    ajustes NUMERIC(8,2) NOT NULL DEFAULT 0,
    saldo_disponible NUMERIC(8,2) NOT NULL DEFAULT 0,
    origen VARCHAR(30) NOT NULL DEFAULT 'CALCULO',
    fila_excel INTEGER,
    fecha_corte DATE,
    observaciones TEXT,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_vacaciones_saldo_empleado_periodo UNIQUE (empleado2_id, periodo)
);

CREATE INDEX IF NOT EXISTS ix_vacaciones_saldos_empleado2_id ON rrhh.vacaciones_saldos (empleado2_id);
CREATE INDEX IF NOT EXISTS ix_vacaciones_saldos_periodo ON rrhh.vacaciones_saldos (periodo);

CREATE TABLE IF NOT EXISTS rrhh.vacaciones_movimientos (
    id BIGSERIAL PRIMARY KEY,
    empleado2_id BIGINT NOT NULL REFERENCES rrhh.empleados2(id) ON DELETE CASCADE,
    saldo_id BIGINT REFERENCES rrhh.vacaciones_saldos(id) ON DELETE SET NULL,
    licencia_id INTEGER REFERENCES rrhh.licencias(id) ON DELETE SET NULL,
    tipo VARCHAR(40) NOT NULL,
    fecha_desde DATE,
    fecha_hasta DATE,
    fecha_reintegro DATE,
    dias NUMERIC(8,2) NOT NULL DEFAULT 0,
    saldo_resultante NUMERIC(8,2),
    detalle TEXT,
    observaciones TEXT,
    origen VARCHAR(30) NOT NULL DEFAULT 'SISTEMA',
    referencia_origen VARCHAR(100) NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_vacaciones_movimiento_origen UNIQUE (origen, referencia_origen)
);

CREATE INDEX IF NOT EXISTS ix_vacaciones_movimientos_empleado2_id ON rrhh.vacaciones_movimientos (empleado2_id);
