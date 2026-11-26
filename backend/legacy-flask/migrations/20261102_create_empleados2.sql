-- Replica limpia de erp.dbo.Usuario. No modifica rrhh.empleados.
BEGIN;
CREATE TABLE IF NOT EXISTS rrhh.empleados2 (
 id BIGSERIAL PRIMARY KEY, id_usuario INTEGER NOT NULL UNIQUE, cod_usuario VARCHAR(20),
 telefono VARCHAR(15), telefono_alternativo VARCHAR(15), telefono_otro VARCHAR(50), correo VARCHAR(120), correo_alternativo VARCHAR(120),
 tipo_documento VARCHAR(20), numero_documento VARCHAR(20), sexo VARCHAR(1), nivel VARCHAR(100), numero_nivel INTEGER,
 nombre VARCHAR(50), apellido VARCHAR(250), codigo_jerarquia_superior INTEGER, numero_legajo VARCHAR(20), estado_salud VARCHAR(1),
 codigo_dato_empleado INTEGER, cuil VARCHAR(13), numero_jubilacion VARCHAR(10), foto VARCHAR(100), estado INTEGER, razon VARCHAR(100),
 nacionalidad VARCHAR(50), fecha_nacimiento DATE, fecha_ingreso DATE, fecha_egreso DATE, codigo_estado_civil INTEGER,
 calle VARCHAR(30), numero_casa VARCHAR(10), numero_departamento VARCHAR(10), manzana VARCHAR(10), barrio VARCHAR(30), torre VARCHAR(15), piso VARCHAR(20),
 pais VARCHAR(50), localidad VARCHAR(70), provincia VARCHAR(30), telefono_laboral VARCHAR(100), horas_extra DOUBLE PRECISION, horas_normales DOUBLE PRECISION,
 codigo_jerarquia INTEGER, codigo_pais INTEGER, codigo_tipo_documento INTEGER, nombre_documento VARCHAR(20), curp VARCHAR(15), numero_seguro_social VARCHAR(50),
 fecha_efectivizacion DATE, codigo_localidad INTEGER, codigo_provincia INTEGER, jerarquia_padre INTEGER,
 huella_origen VARCHAR(64) NOT NULL, presente_en_origen BOOLEAN NOT NULL DEFAULT TRUE,
 ultima_sincronizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_empleados2_id_usuario ON rrhh.empleados2 (id_usuario);
COMMIT;
