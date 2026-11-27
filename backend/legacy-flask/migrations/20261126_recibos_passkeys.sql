-- Aditiva. Ejecutar únicamente después de respaldar y aprobar el ambiente destino.
BEGIN;
CREATE TABLE IF NOT EXISTS rrhh.recibo_credenciales (
 id SERIAL PRIMARY KEY,
 usuario_id INTEGER NOT NULL REFERENCES rrhh.usuarios(id),
 credential_id TEXT NOT NULL UNIQUE,
 public_key BYTEA NOT NULL,
 sign_count BIGINT NOT NULL DEFAULT 0,
 creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_recibo_credenciales_usuario_id ON rrhh.recibo_credenciales(usuario_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_recibo_credenciales_usuario ON rrhh.recibo_credenciales(usuario_id);
CREATE TABLE IF NOT EXISTS rrhh.recibo_desafios (
 id VARCHAR(64) PRIMARY KEY,
 usuario_id INTEGER NOT NULL REFERENCES rrhh.usuarios(id),
 recibo_id INTEGER NOT NULL REFERENCES rrhh.recibos_sueldo(id),
 purpose VARCHAR(16) NOT NULL,
 challenge BYTEA NOT NULL,
 session_binding VARCHAR(64) NOT NULL,
 respuesta VARCHAR(20), observacion TEXT,
 document_hash VARCHAR(64) NOT NULL,
 expires_at TIMESTAMP NOT NULL, consumed_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS rrhh.recibo_firmas (
 id SERIAL PRIMARY KEY,
 recibo_id INTEGER NOT NULL UNIQUE REFERENCES rrhh.recibos_sueldo(id),
 usuario_id INTEGER NOT NULL REFERENCES rrhh.usuarios(id),
 credencial_id INTEGER NOT NULL REFERENCES rrhh.recibo_credenciales(id),
 desafio_id VARCHAR(64) NOT NULL UNIQUE REFERENCES rrhh.recibo_desafios(id),
 document_hash VARCHAR(64) NOT NULL,
 respuesta VARCHAR(20) NOT NULL, observacion TEXT,
 evidencia JSON NOT NULL, origin TEXT NOT NULL, rp_id TEXT NOT NULL,
 firmado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMIT;
