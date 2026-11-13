BEGIN;

-- Duplicados confirmados por RR. HH.; se conserva idUsuario 94 (pnicastro).
DELETE FROM rrhh.usuarios
WHERE empleado2_id IN (
    SELECT id FROM rrhh.empleados2 WHERE id_usuario IN (1381, 1382)
);

-- Los saldos de vacaciones asociados se eliminan por ON DELETE CASCADE.
DELETE FROM rrhh.empleados2
WHERE id_usuario IN (1381, 1382);

COMMIT;
