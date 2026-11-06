BEGIN;
ALTER TABLE rrhh.usuarios ADD COLUMN IF NOT EXISTS empleado2_id BIGINT;
ALTER TABLE rrhh.usuarios ADD COLUMN IF NOT EXISTS debe_cambiar_password BOOLEAN NOT NULL DEFAULT FALSE;
DO $$ BEGIN
  ALTER TABLE rrhh.usuarios ADD CONSTRAINT fk_usuarios_empleado2
    FOREIGN KEY (empleado2_id) REFERENCES rrhh.empleados2(id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_empleado2_id
  ON rrhh.usuarios (empleado2_id) WHERE empleado2_id IS NOT NULL;
COMMIT;
