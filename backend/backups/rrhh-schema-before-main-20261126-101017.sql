--
-- PostgreSQL database dump
--

\restrict YxonnTgsQtbDBjz0Xz23RPfkwsP1ssO6rlKgvwOyehGOSstZyBHZ9eDEzkpoU18

-- Dumped from database version 13.23
-- Dumped by pg_dump version 13.23

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: rrhh; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA rrhh;


ALTER SCHEMA rrhh OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: documentos_rrhh; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.documentos_rrhh (
    id integer NOT NULL,
    empleado_id integer,
    tipo_documento_id integer,
    nombre_documento character varying(200) NOT NULL,
    nombre_archivo character varying(255),
    ruta_archivo text NOT NULL,
    visible_empleado boolean,
    observaciones text,
    estado character varying(50),
    cargado_por integer,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.documentos_rrhh OWNER TO postgres;

--
-- Name: documentos_rrhh_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.documentos_rrhh_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.documentos_rrhh_id_seq OWNER TO postgres;

--
-- Name: documentos_rrhh_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.documentos_rrhh_id_seq OWNED BY rrhh.documentos_rrhh.id;


--
-- Name: empleados; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.empleados (
    id integer NOT NULL,
    nombre_apellido character varying(150) NOT NULL,
    dni character varying(20) NOT NULL,
    cuil character varying(30),
    legajo character varying(50),
    empresa_id integer,
    sector_id integer,
    puesto_id integer,
    supervisor_id integer,
    jornada_id integer,
    jornada_horas numeric(4,2),
    fecha_nacimiento date,
    domicilio character varying(200),
    telefono character varying(50),
    correo character varying(150),
    provincia character varying(100),
    codigo_postal character varying(20),
    fecha_ingreso date,
    licencia_conducir character varying(100),
    genero character varying(50),
    estado character varying(50),
    creado_en timestamp without time zone,
    actualizado_en timestamp without time zone
);


ALTER TABLE rrhh.empleados OWNER TO postgres;

--
-- Name: empleados_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.empleados_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.empleados_id_seq OWNER TO postgres;

--
-- Name: empleados_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.empleados_id_seq OWNED BY rrhh.empleados.id;


--
-- Name: empresas; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.empresas (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    tarifa_lav numeric(10,2),
    tarifa_sab numeric(10,2),
    tarifa_dom_fer numeric(10,2),
    activo boolean,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.empresas OWNER TO postgres;

--
-- Name: empresas_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.empresas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.empresas_id_seq OWNER TO postgres;

--
-- Name: empresas_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.empresas_id_seq OWNED BY rrhh.empresas.id;


--
-- Name: evaluaciones_desempeno; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.evaluaciones_desempeno (
    id integer NOT NULL,
    empleado_id integer,
    evaluador_id integer,
    fecha_evaluacion date,
    periodo_evaluado character varying(100),
    puntaje_general numeric(5,2),
    fortalezas text,
    aspectos_mejorar text,
    observaciones text,
    archivo_adjunto text,
    visible_empleado boolean,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.evaluaciones_desempeno OWNER TO postgres;

--
-- Name: evaluaciones_desempeno_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.evaluaciones_desempeno_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.evaluaciones_desempeno_id_seq OWNER TO postgres;

--
-- Name: evaluaciones_desempeno_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.evaluaciones_desempeno_id_seq OWNED BY rrhh.evaluaciones_desempeno.id;


--
-- Name: familiares; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.familiares (
    id integer NOT NULL,
    empleado_id integer,
    nombre_apellido character varying(150) NOT NULL,
    parentesco character varying(100),
    dni character varying(20),
    fecha_nacimiento date,
    telefono character varying(50),
    contacto_emergencia boolean,
    observaciones text,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.familiares OWNER TO postgres;

--
-- Name: familiares_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.familiares_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.familiares_id_seq OWNER TO postgres;

--
-- Name: familiares_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.familiares_id_seq OWNED BY rrhh.familiares.id;


--
-- Name: feriados; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.feriados (
    id integer NOT NULL,
    fecha date NOT NULL,
    descripcion character varying(200),
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.feriados OWNER TO postgres;

--
-- Name: feriados_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.feriados_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.feriados_id_seq OWNER TO postgres;

--
-- Name: feriados_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.feriados_id_seq OWNED BY rrhh.feriados.id;


--
-- Name: horas_extra; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.horas_extra (
    id integer NOT NULL,
    empleado_id integer,
    fecha date NOT NULL,
    hora_desde time without time zone,
    hora_hasta time without time zone,
    cantidad_horas numeric(10,2),
    motivo text,
    sector_id integer,
    supervisor_id integer,
    estado character varying(50),
    observaciones text,
    cargado_por integer,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.horas_extra OWNER TO postgres;

--
-- Name: horas_extra_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.horas_extra_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.horas_extra_id_seq OWNER TO postgres;

--
-- Name: horas_extra_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.horas_extra_id_seq OWNED BY rrhh.horas_extra.id;


--
-- Name: jornadas; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.jornadas (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    activo boolean,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.jornadas OWNER TO postgres;

--
-- Name: jornadas_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.jornadas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.jornadas_id_seq OWNER TO postgres;

--
-- Name: jornadas_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.jornadas_id_seq OWNED BY rrhh.jornadas.id;


--
-- Name: licencias; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.licencias (
    id integer NOT NULL,
    empleado_id integer,
    tipo_licencia_id integer,
    fecha_desde date NOT NULL,
    fecha_hasta date NOT NULL,
    cantidad_dias numeric(10,2),
    motivo text,
    archivo_adjunto text,
    estado character varying(50),
    aprobado_por integer,
    fecha_resolucion timestamp without time zone,
    observacion_rrhh text,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.licencias OWNER TO postgres;

--
-- Name: licencias_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.licencias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.licencias_id_seq OWNER TO postgres;

--
-- Name: licencias_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.licencias_id_seq OWNED BY rrhh.licencias.id;


--
-- Name: noticias; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.noticias (
    id integer NOT NULL,
    titulo character varying(200) NOT NULL,
    contenido text NOT NULL,
    imagen text,
    estado character varying(50),
    visible_todos boolean,
    empresa_id integer,
    sector_id integer,
    publicado_por integer,
    fecha_publicacion timestamp without time zone,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.noticias OWNER TO postgres;

--
-- Name: noticias_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.noticias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.noticias_id_seq OWNER TO postgres;

--
-- Name: noticias_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.noticias_id_seq OWNED BY rrhh.noticias.id;


--
-- Name: notificaciones; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.notificaciones (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    titulo character varying(200) NOT NULL,
    mensaje text NOT NULL,
    tipo character varying(50) NOT NULL,
    referencia_tipo character varying(50),
    referencia_id integer,
    leida boolean NOT NULL,
    leida_en timestamp without time zone,
    creado_en timestamp without time zone NOT NULL
);


ALTER TABLE rrhh.notificaciones OWNER TO postgres;

--
-- Name: notificaciones_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.notificaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.notificaciones_id_seq OWNER TO postgres;

--
-- Name: notificaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.notificaciones_id_seq OWNED BY rrhh.notificaciones.id;


--
-- Name: puestos; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.puestos (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    activo boolean,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.puestos OWNER TO postgres;

--
-- Name: puestos_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.puestos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.puestos_id_seq OWNER TO postgres;

--
-- Name: puestos_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.puestos_id_seq OWNED BY rrhh.puestos.id;


--
-- Name: roles; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.roles (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion text,
    activo boolean,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.roles_id_seq OWNED BY rrhh.roles.id;


--
-- Name: sanciones_disciplinarias; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.sanciones_disciplinarias (
    id integer NOT NULL,
    empleado_id integer NOT NULL,
    tipo character varying(50) NOT NULL,
    fecha date NOT NULL,
    fecha_desde date,
    fecha_hasta date,
    cantidad_dias numeric(6,2),
    motivo character varying(200) NOT NULL,
    descripcion text,
    observaciones text,
    nombre_archivo character varying(255),
    ruta_archivo text,
    estado character varying(50) NOT NULL,
    notificado_en timestamp without time zone,
    creado_por integer NOT NULL,
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone
);


ALTER TABLE rrhh.sanciones_disciplinarias OWNER TO postgres;

--
-- Name: sanciones_disciplinarias_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.sanciones_disciplinarias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.sanciones_disciplinarias_id_seq OWNER TO postgres;

--
-- Name: sanciones_disciplinarias_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.sanciones_disciplinarias_id_seq OWNED BY rrhh.sanciones_disciplinarias.id;


--
-- Name: sectores; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.sectores (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    activo boolean,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.sectores OWNER TO postgres;

--
-- Name: sectores_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.sectores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.sectores_id_seq OWNER TO postgres;

--
-- Name: sectores_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.sectores_id_seq OWNED BY rrhh.sectores.id;


--
-- Name: tipos_documento; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.tipos_documento (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    activo boolean,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.tipos_documento OWNER TO postgres;

--
-- Name: tipos_documento_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.tipos_documento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.tipos_documento_id_seq OWNER TO postgres;

--
-- Name: tipos_documento_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.tipos_documento_id_seq OWNED BY rrhh.tipos_documento.id;


--
-- Name: tipos_licencia; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.tipos_licencia (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    requiere_adjunto boolean,
    activo boolean,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.tipos_licencia OWNER TO postgres;

--
-- Name: tipos_licencia_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.tipos_licencia_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.tipos_licencia_id_seq OWNER TO postgres;

--
-- Name: tipos_licencia_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.tipos_licencia_id_seq OWNED BY rrhh.tipos_licencia.id;


--
-- Name: usuarios; Type: TABLE; Schema: rrhh; Owner: postgres
--

CREATE TABLE rrhh.usuarios (
    id integer NOT NULL,
    empleado_id integer,
    rol_id integer NOT NULL,
    usuario character varying(100) NOT NULL,
    correo character varying(150),
    password_hash text NOT NULL,
    activo boolean,
    ultimo_acceso timestamp without time zone,
    creado_en timestamp without time zone
);


ALTER TABLE rrhh.usuarios OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: rrhh; Owner: postgres
--

CREATE SEQUENCE rrhh.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rrhh.usuarios_id_seq OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: rrhh; Owner: postgres
--

ALTER SEQUENCE rrhh.usuarios_id_seq OWNED BY rrhh.usuarios.id;


--
-- Name: documentos_rrhh id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.documentos_rrhh ALTER COLUMN id SET DEFAULT nextval('rrhh.documentos_rrhh_id_seq'::regclass);


--
-- Name: empleados id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empleados ALTER COLUMN id SET DEFAULT nextval('rrhh.empleados_id_seq'::regclass);


--
-- Name: empresas id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empresas ALTER COLUMN id SET DEFAULT nextval('rrhh.empresas_id_seq'::regclass);


--
-- Name: evaluaciones_desempeno id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.evaluaciones_desempeno ALTER COLUMN id SET DEFAULT nextval('rrhh.evaluaciones_desempeno_id_seq'::regclass);


--
-- Name: familiares id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.familiares ALTER COLUMN id SET DEFAULT nextval('rrhh.familiares_id_seq'::regclass);


--
-- Name: feriados id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.feriados ALTER COLUMN id SET DEFAULT nextval('rrhh.feriados_id_seq'::regclass);


--
-- Name: horas_extra id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.horas_extra ALTER COLUMN id SET DEFAULT nextval('rrhh.horas_extra_id_seq'::regclass);


--
-- Name: jornadas id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.jornadas ALTER COLUMN id SET DEFAULT nextval('rrhh.jornadas_id_seq'::regclass);


--
-- Name: licencias id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.licencias ALTER COLUMN id SET DEFAULT nextval('rrhh.licencias_id_seq'::regclass);


--
-- Name: noticias id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.noticias ALTER COLUMN id SET DEFAULT nextval('rrhh.noticias_id_seq'::regclass);


--
-- Name: notificaciones id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.notificaciones ALTER COLUMN id SET DEFAULT nextval('rrhh.notificaciones_id_seq'::regclass);


--
-- Name: puestos id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.puestos ALTER COLUMN id SET DEFAULT nextval('rrhh.puestos_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.roles ALTER COLUMN id SET DEFAULT nextval('rrhh.roles_id_seq'::regclass);


--
-- Name: sanciones_disciplinarias id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.sanciones_disciplinarias ALTER COLUMN id SET DEFAULT nextval('rrhh.sanciones_disciplinarias_id_seq'::regclass);


--
-- Name: sectores id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.sectores ALTER COLUMN id SET DEFAULT nextval('rrhh.sectores_id_seq'::regclass);


--
-- Name: tipos_documento id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.tipos_documento ALTER COLUMN id SET DEFAULT nextval('rrhh.tipos_documento_id_seq'::regclass);


--
-- Name: tipos_licencia id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.tipos_licencia ALTER COLUMN id SET DEFAULT nextval('rrhh.tipos_licencia_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.usuarios ALTER COLUMN id SET DEFAULT nextval('rrhh.usuarios_id_seq'::regclass);


--
-- Name: documentos_rrhh documentos_rrhh_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.documentos_rrhh
    ADD CONSTRAINT documentos_rrhh_pkey PRIMARY KEY (id);


--
-- Name: empleados empleados_cuil_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empleados
    ADD CONSTRAINT empleados_cuil_key UNIQUE (cuil);


--
-- Name: empleados empleados_dni_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empleados
    ADD CONSTRAINT empleados_dni_key UNIQUE (dni);


--
-- Name: empleados empleados_legajo_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empleados
    ADD CONSTRAINT empleados_legajo_key UNIQUE (legajo);


--
-- Name: empleados empleados_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empleados
    ADD CONSTRAINT empleados_pkey PRIMARY KEY (id);


--
-- Name: empresas empresas_nombre_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empresas
    ADD CONSTRAINT empresas_nombre_key UNIQUE (nombre);


--
-- Name: empresas empresas_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empresas
    ADD CONSTRAINT empresas_pkey PRIMARY KEY (id);


--
-- Name: evaluaciones_desempeno evaluaciones_desempeno_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.evaluaciones_desempeno
    ADD CONSTRAINT evaluaciones_desempeno_pkey PRIMARY KEY (id);


--
-- Name: familiares familiares_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.familiares
    ADD CONSTRAINT familiares_pkey PRIMARY KEY (id);


--
-- Name: feriados feriados_fecha_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.feriados
    ADD CONSTRAINT feriados_fecha_key UNIQUE (fecha);


--
-- Name: feriados feriados_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.feriados
    ADD CONSTRAINT feriados_pkey PRIMARY KEY (id);


--
-- Name: horas_extra horas_extra_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.horas_extra
    ADD CONSTRAINT horas_extra_pkey PRIMARY KEY (id);


--
-- Name: jornadas jornadas_nombre_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.jornadas
    ADD CONSTRAINT jornadas_nombre_key UNIQUE (nombre);


--
-- Name: jornadas jornadas_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.jornadas
    ADD CONSTRAINT jornadas_pkey PRIMARY KEY (id);


--
-- Name: licencias licencias_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.licencias
    ADD CONSTRAINT licencias_pkey PRIMARY KEY (id);


--
-- Name: noticias noticias_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.noticias
    ADD CONSTRAINT noticias_pkey PRIMARY KEY (id);


--
-- Name: notificaciones notificaciones_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.notificaciones
    ADD CONSTRAINT notificaciones_pkey PRIMARY KEY (id);


--
-- Name: puestos puestos_nombre_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.puestos
    ADD CONSTRAINT puestos_nombre_key UNIQUE (nombre);


--
-- Name: puestos puestos_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.puestos
    ADD CONSTRAINT puestos_pkey PRIMARY KEY (id);


--
-- Name: roles roles_nombre_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.roles
    ADD CONSTRAINT roles_nombre_key UNIQUE (nombre);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: sanciones_disciplinarias sanciones_disciplinarias_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.sanciones_disciplinarias
    ADD CONSTRAINT sanciones_disciplinarias_pkey PRIMARY KEY (id);


--
-- Name: sectores sectores_nombre_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.sectores
    ADD CONSTRAINT sectores_nombre_key UNIQUE (nombre);


--
-- Name: sectores sectores_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.sectores
    ADD CONSTRAINT sectores_pkey PRIMARY KEY (id);


--
-- Name: tipos_documento tipos_documento_nombre_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.tipos_documento
    ADD CONSTRAINT tipos_documento_nombre_key UNIQUE (nombre);


--
-- Name: tipos_documento tipos_documento_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.tipos_documento
    ADD CONSTRAINT tipos_documento_pkey PRIMARY KEY (id);


--
-- Name: tipos_licencia tipos_licencia_nombre_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.tipos_licencia
    ADD CONSTRAINT tipos_licencia_nombre_key UNIQUE (nombre);


--
-- Name: tipos_licencia tipos_licencia_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.tipos_licencia
    ADD CONSTRAINT tipos_licencia_pkey PRIMARY KEY (id);


--
-- Name: notificaciones uq_notificacion_referencia_usuario; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.notificaciones
    ADD CONSTRAINT uq_notificacion_referencia_usuario UNIQUE (usuario_id, referencia_tipo, referencia_id);


--
-- Name: usuarios usuarios_correo_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.usuarios
    ADD CONSTRAINT usuarios_correo_key UNIQUE (correo);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_usuario_key; Type: CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.usuarios
    ADD CONSTRAINT usuarios_usuario_key UNIQUE (usuario);


--
-- Name: documentos_rrhh documentos_rrhh_cargado_por_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.documentos_rrhh
    ADD CONSTRAINT documentos_rrhh_cargado_por_fkey FOREIGN KEY (cargado_por) REFERENCES rrhh.usuarios(id);


--
-- Name: documentos_rrhh documentos_rrhh_empleado_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.documentos_rrhh
    ADD CONSTRAINT documentos_rrhh_empleado_id_fkey FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id) ON DELETE CASCADE;


--
-- Name: documentos_rrhh documentos_rrhh_tipo_documento_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.documentos_rrhh
    ADD CONSTRAINT documentos_rrhh_tipo_documento_id_fkey FOREIGN KEY (tipo_documento_id) REFERENCES rrhh.tipos_documento(id);


--
-- Name: empleados empleados_empresa_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empleados
    ADD CONSTRAINT empleados_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES rrhh.empresas(id);


--
-- Name: empleados empleados_jornada_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empleados
    ADD CONSTRAINT empleados_jornada_id_fkey FOREIGN KEY (jornada_id) REFERENCES rrhh.jornadas(id);


--
-- Name: empleados empleados_puesto_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empleados
    ADD CONSTRAINT empleados_puesto_id_fkey FOREIGN KEY (puesto_id) REFERENCES rrhh.puestos(id);


--
-- Name: empleados empleados_sector_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empleados
    ADD CONSTRAINT empleados_sector_id_fkey FOREIGN KEY (sector_id) REFERENCES rrhh.sectores(id);


--
-- Name: empleados empleados_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.empleados
    ADD CONSTRAINT empleados_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES rrhh.empleados(id);


--
-- Name: evaluaciones_desempeno evaluaciones_desempeno_empleado_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.evaluaciones_desempeno
    ADD CONSTRAINT evaluaciones_desempeno_empleado_id_fkey FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id) ON DELETE CASCADE;


--
-- Name: evaluaciones_desempeno evaluaciones_desempeno_evaluador_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.evaluaciones_desempeno
    ADD CONSTRAINT evaluaciones_desempeno_evaluador_id_fkey FOREIGN KEY (evaluador_id) REFERENCES rrhh.usuarios(id);


--
-- Name: familiares familiares_empleado_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.familiares
    ADD CONSTRAINT familiares_empleado_id_fkey FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id) ON DELETE CASCADE;


--
-- Name: horas_extra horas_extra_cargado_por_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.horas_extra
    ADD CONSTRAINT horas_extra_cargado_por_fkey FOREIGN KEY (cargado_por) REFERENCES rrhh.usuarios(id);


--
-- Name: horas_extra horas_extra_empleado_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.horas_extra
    ADD CONSTRAINT horas_extra_empleado_id_fkey FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id) ON DELETE CASCADE;


--
-- Name: horas_extra horas_extra_sector_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.horas_extra
    ADD CONSTRAINT horas_extra_sector_id_fkey FOREIGN KEY (sector_id) REFERENCES rrhh.sectores(id);


--
-- Name: horas_extra horas_extra_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.horas_extra
    ADD CONSTRAINT horas_extra_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES rrhh.empleados(id);


--
-- Name: licencias licencias_aprobado_por_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.licencias
    ADD CONSTRAINT licencias_aprobado_por_fkey FOREIGN KEY (aprobado_por) REFERENCES rrhh.usuarios(id);


--
-- Name: licencias licencias_empleado_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.licencias
    ADD CONSTRAINT licencias_empleado_id_fkey FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id) ON DELETE CASCADE;


--
-- Name: licencias licencias_tipo_licencia_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.licencias
    ADD CONSTRAINT licencias_tipo_licencia_id_fkey FOREIGN KEY (tipo_licencia_id) REFERENCES rrhh.tipos_licencia(id);


--
-- Name: noticias noticias_empresa_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.noticias
    ADD CONSTRAINT noticias_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES rrhh.empresas(id);


--
-- Name: noticias noticias_publicado_por_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.noticias
    ADD CONSTRAINT noticias_publicado_por_fkey FOREIGN KEY (publicado_por) REFERENCES rrhh.usuarios(id);


--
-- Name: noticias noticias_sector_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.noticias
    ADD CONSTRAINT noticias_sector_id_fkey FOREIGN KEY (sector_id) REFERENCES rrhh.sectores(id);


--
-- Name: notificaciones notificaciones_usuario_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.notificaciones
    ADD CONSTRAINT notificaciones_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES rrhh.usuarios(id) ON DELETE CASCADE;


--
-- Name: sanciones_disciplinarias sanciones_disciplinarias_creado_por_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.sanciones_disciplinarias
    ADD CONSTRAINT sanciones_disciplinarias_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES rrhh.usuarios(id);


--
-- Name: sanciones_disciplinarias sanciones_disciplinarias_empleado_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.sanciones_disciplinarias
    ADD CONSTRAINT sanciones_disciplinarias_empleado_id_fkey FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id) ON DELETE CASCADE;


--
-- Name: usuarios usuarios_empleado_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.usuarios
    ADD CONSTRAINT usuarios_empleado_id_fkey FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id);


--
-- Name: usuarios usuarios_rol_id_fkey; Type: FK CONSTRAINT; Schema: rrhh; Owner: postgres
--

ALTER TABLE ONLY rrhh.usuarios
    ADD CONSTRAINT usuarios_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES rrhh.roles(id);


--
-- PostgreSQL database dump complete
--

\unrestrict YxonnTgsQtbDBjz0Xz23RPfkwsP1ssO6rlKgvwOyehGOSstZyBHZ9eDEzkpoU18

