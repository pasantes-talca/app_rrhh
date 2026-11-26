BEGIN;

UPDATE rrhh.usuarios AS u
SET usuario = 'gbonora'
FROM rrhh.empleados2 AS e
WHERE u.empleado2_id = e.id
  AND e.id_usuario = 1510
  AND NOT EXISTS (
      SELECT 1 FROM rrhh.usuarios existente
      WHERE lower(existente.usuario) = 'gbonora'
        AND existente.id <> u.id
  );

COMMIT;
