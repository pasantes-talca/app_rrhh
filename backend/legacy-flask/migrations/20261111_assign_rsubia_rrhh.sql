UPDATE rrhh.usuarios
SET rol_id = (SELECT id FROM rrhh.roles WHERE nombre = 'recursos_humanos')
WHERE usuario = 'rsubia' AND activo = TRUE;
