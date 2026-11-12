UPDATE rrhh.usuarios
SET rol_id = (SELECT id FROM rrhh.roles WHERE nombre = 'supervisor')
WHERE usuario IN ('mpaez', 'jsotelo', 'jsevilla', 'razzolina', 'fbarraquero')
  AND activo = TRUE;
