-- Ejecutar después de 20261126_recibos_passkeys.sql.
-- Permite registrar la clave desde Mi perfil sin necesitar un recibo pendiente.
BEGIN;
ALTER TABLE rrhh.recibo_desafios ALTER COLUMN recibo_id DROP NOT NULL;
COMMIT;
