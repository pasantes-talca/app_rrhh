INSERT INTO rrhh.roles (nombre, descripcion, activo, creado_en)
VALUES
    ('supervisor', 'Colaborador con personal a cargo y facultad de revisar solicitudes de su equipo.', TRUE, CURRENT_TIMESTAMP),
    ('gerencia', 'Perfil de consulta ejecutiva para indicadores y reportes de Recursos Humanos.', TRUE, CURRENT_TIMESTAMP)
ON CONFLICT (nombre) DO UPDATE
SET descripcion = EXCLUDED.descripcion,
    activo = TRUE;

UPDATE rrhh.usuarios
SET rol_id = (SELECT id FROM rrhh.roles WHERE nombre = 'supervisor')
WHERE usuario = 'mpaez';

UPDATE rrhh.usuarios
SET rol_id = (SELECT id FROM rrhh.roles WHERE nombre = 'gerencia')
WHERE usuario IN ('drinaldi', 'idbraceli', 'lliguori', 'salonso', 'jdistefano');
