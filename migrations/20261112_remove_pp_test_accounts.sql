BEGIN;

-- Cuentas PP de prueba confirmadas por RR. HH.
-- Se conserva idUsuario 258 (mpappalardo), cuyo apellido contiene "pp" naturalmente.
DELETE FROM rrhh.usuarios
WHERE empleado2_id IN (
    SELECT id
    FROM rrhh.empleados2
    WHERE id_usuario IN (313, 325, 328, 329, 330, 331, 1354, 1503, 1531, 1532)
);

-- Los saldos vacacionales automáticos se eliminan por ON DELETE CASCADE.
DELETE FROM rrhh.empleados2
WHERE id_usuario IN (313, 325, 328, 329, 330, 331, 1354, 1503, 1531, 1532);

COMMIT;
