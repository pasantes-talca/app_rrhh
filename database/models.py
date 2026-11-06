from extensions import db
from flask_login import UserMixin
from datetime import datetime

class Rol(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

class Empresa(db.Model):
    __tablename__ = 'empresas'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    tarifa_lav = db.Column(db.Numeric(10, 2), default=0.0)
    tarifa_sab = db.Column(db.Numeric(10, 2), default=0.0)
    tarifa_dom_fer = db.Column(db.Numeric(10, 2), default=0.0)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class Sector(db.Model):
    __tablename__ = 'sectores'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class Puesto(db.Model):
    __tablename__ = 'puestos'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class Jornada(db.Model):
    __tablename__ = 'jornadas'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class Empleado(db.Model):
    __tablename__ = 'empleados'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_apellido = db.Column(db.String(150), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    cuil = db.Column(db.String(30), unique=True)
    legajo = db.Column(db.String(50), unique=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('rrhh.empresas.id'))
    sector_id = db.Column(db.Integer, db.ForeignKey('rrhh.sectores.id'))
    puesto_id = db.Column(db.Integer, db.ForeignKey('rrhh.puestos.id'))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('rrhh.empleados.id'))
    jornada_id = db.Column(db.Integer, db.ForeignKey('rrhh.jornadas.id'))
    jornada_horas = db.Column(db.Numeric(4, 2), default=9.0)
    fecha_nacimiento = db.Column(db.Date)
    domicilio = db.Column(db.String(200))
    telefono = db.Column(db.String(50))
    correo = db.Column(db.String(150))
    provincia = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(20))
    fecha_ingreso = db.Column(db.Date)
    licencia_conducir = db.Column(db.String(100))
    genero = db.Column(db.String(50))
    estado = db.Column(db.String(50), default='Activo')
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    empresa = db.relationship('Empresa')
    sector = db.relationship('Sector')
    puesto = db.relationship('Puesto')
    jornada = db.relationship('Jornada')
    supervisor = db.relationship('Empleado', remote_side=[id])

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('rrhh.empleados.id'))
    empleado2_id = db.Column(db.BigInteger, db.ForeignKey('rrhh.empleados2.id'))
    rol_id = db.Column(db.Integer, db.ForeignKey('rrhh.roles.id'), nullable=False)
    usuario = db.Column(db.String(100), unique=True, nullable=False)
    nombre_mostrar = db.Column(db.String(150))
    correo = db.Column(db.String(150), unique=True)
    foto_perfil = db.Column(db.String(255))
    cuenta_protegida = db.Column(db.Boolean, default=False, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    debe_cambiar_password = db.Column(db.Boolean, default=False, nullable=False)
    ultimo_acceso = db.Column(db.DateTime)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    empleado = db.relationship('Empleado')
    empleado2 = db.relationship('Empleado2', foreign_keys=[empleado2_id])

class Familiar(db.Model):
    __tablename__ = 'familiares'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('rrhh.empleados.id', ondelete='CASCADE'))
    nombre_apellido = db.Column(db.String(150), nullable=False)
    parentesco = db.Column(db.String(100))
    dni = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.Date)
    telefono = db.Column(db.String(50))
    contacto_emergencia = db.Column(db.Boolean, default=False)
    observaciones = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    empleado = db.relationship('Empleado', backref=db.backref('familiares', cascade='all, delete-orphan'))

class TipoLicencia(db.Model):
    __tablename__ = 'tipos_licencia'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    requiere_adjunto = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class Licencia(db.Model):
    __tablename__ = 'licencias'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('rrhh.empleados.id', ondelete='CASCADE'))
    tipo_licencia_id = db.Column(db.Integer, db.ForeignKey('rrhh.tipos_licencia.id'))
    fecha_desde = db.Column(db.Date, nullable=False)
    fecha_hasta = db.Column(db.Date, nullable=False)
    cantidad_dias = db.Column(db.Numeric(10, 2))
    motivo = db.Column(db.Text)
    archivo_adjunto = db.Column(db.Text)
    estado = db.Column(db.String(50), default='Pendiente')
    aprobado_por = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    fecha_resolucion = db.Column(db.DateTime)
    observacion_rrhh = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    empleado = db.relationship('Empleado', backref=db.backref('licencias', lazy=True))
    tipo_licencia = db.relationship('TipoLicencia')
    aprobador = db.relationship('Usuario', foreign_keys=[aprobado_por])

class Noticia(db.Model):
    __tablename__ = 'noticias'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    imagen = db.Column(db.Text)
    estado = db.Column(db.String(50), default='Publicada')
    visible_todos = db.Column(db.Boolean, default=True)
    es_fecha_importante = db.Column(db.Boolean, default=False, nullable=False)
    fecha_importante = db.Column(db.Date)
    empresa_id = db.Column(db.Integer, db.ForeignKey('rrhh.empresas.id'))
    sector_id = db.Column(db.Integer, db.ForeignKey('rrhh.sectores.id'))
    publicado_por = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    fecha_publicacion = db.Column(db.DateTime)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    empresa = db.relationship('Empresa')
    sector = db.relationship('Sector')
    publicador = db.relationship('Usuario', foreign_keys=[publicado_por])

class EvaluacionDesempeno(db.Model):
    __tablename__ = 'evaluaciones_desempeno'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('rrhh.empleados.id', ondelete='CASCADE'))
    evaluador_id = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    fecha_evaluacion = db.Column(db.Date)
    periodo_evaluado = db.Column(db.String(100))
    puntaje_general = db.Column(db.Numeric(5, 2))
    fortalezas = db.Column(db.Text)
    aspectos_mejorar = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    archivo_adjunto = db.Column(db.Text)
    visible_empleado = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    empleado = db.relationship('Empleado', backref=db.backref('evaluaciones', lazy=True))
    evaluador = db.relationship('Usuario', foreign_keys=[evaluador_id])

class HorasExtra(db.Model):
    __tablename__ = 'horas_extra'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('rrhh.empleados.id', ondelete='CASCADE'))
    fecha = db.Column(db.Date, nullable=False)
    hora_desde = db.Column(db.Time)
    hora_hasta = db.Column(db.Time)
    cantidad_horas = db.Column(db.Numeric(10, 2))
    motivo = db.Column(db.Text)
    sector_id = db.Column(db.Integer, db.ForeignKey('rrhh.sectores.id'))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('rrhh.empleados.id'))
    estado = db.Column(db.String(50), default='Pendiente')
    observaciones = db.Column(db.Text)
    cargado_por = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    empleado = db.relationship('Empleado', foreign_keys=[empleado_id], backref=db.backref('horas_extra', lazy=True))
    sector = db.relationship('Sector')
    supervisor = db.relationship('Empleado', foreign_keys=[supervisor_id])
    cargador = db.relationship('Usuario', foreign_keys=[cargado_por])

class Feriado(db.Model):
    __tablename__ = 'feriados'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class TipoDocumento(db.Model):
    __tablename__ = 'tipos_documento'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class DocumentoRRHH(db.Model):
    __tablename__ = 'documentos_rrhh'
    __table_args__ = {'schema': 'rrhh'}
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('rrhh.empleados.id', ondelete='CASCADE'))
    tipo_documento_id = db.Column(db.Integer, db.ForeignKey('rrhh.tipos_documento.id'))
    nombre_documento = db.Column(db.String(200), nullable=False)
    nombre_archivo = db.Column(db.String(255))
    ruta_archivo = db.Column(db.Text, nullable=False)
    visible_empleado = db.Column(db.Boolean, default=False)
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(50), default='Activo')
    cargado_por = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    empleado = db.relationship('Empleado', backref=db.backref('documentos', lazy=True))
    tipo_documento = db.relationship('TipoDocumento')
    cargador = db.relationship('Usuario', foreign_keys=[cargado_por])


class ReciboSueldo(db.Model):
    __tablename__ = 'recibos_sueldo'
    __table_args__ = (
        db.UniqueConstraint('empleado_id', 'periodo', name='uq_recibo_empleado_periodo'),
        {'schema': 'rrhh'},
    )

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('rrhh.documentos_rrhh.id', ondelete='CASCADE'), unique=True, nullable=False)
    empleado_id = db.Column(db.Integer, db.ForeignKey('rrhh.empleados.id', ondelete='CASCADE'), nullable=False)
    periodo = db.Column(db.String(7), nullable=False)
    fecha_limite = db.Column(db.Date)
    estado = db.Column(db.String(30), default='Pendiente', nullable=False)
    visualizado_en = db.Column(db.DateTime)
    respondido_en = db.Column(db.DateTime)
    respuesta = db.Column(db.String(20))
    observacion_empleado = db.Column(db.Text)
    hash_archivo = db.Column(db.String(64), nullable=False)
    ip_respuesta = db.Column(db.String(64))
    agente_usuario = db.Column(db.Text)
    publicado_por = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    documento = db.relationship('DocumentoRRHH', backref=db.backref('recibo_sueldo', uselist=False, cascade='all, delete-orphan'))
    empleado = db.relationship('Empleado', backref=db.backref('recibos_sueldo', lazy=True, cascade='all, delete-orphan'))
    publicador = db.relationship('Usuario', foreign_keys=[publicado_por])


class SancionDisciplinaria(db.Model):
    __tablename__ = 'sanciones_disciplinarias'
    __table_args__ = {'schema': 'rrhh'}

    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('rrhh.empleados.id', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    fecha_desde = db.Column(db.Date)
    fecha_hasta = db.Column(db.Date)
    cantidad_dias = db.Column(db.Numeric(6, 2))
    motivo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    nombre_archivo = db.Column(db.String(255))
    ruta_archivo = db.Column(db.Text)
    estado = db.Column(db.String(50), default='Borrador', nullable=False)
    notificado_en = db.Column(db.DateTime)
    creado_por = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(db.DateTime, onupdate=datetime.utcnow)

    empleado = db.relationship('Empleado', backref=db.backref('sanciones_disciplinarias', lazy=True))
    creador = db.relationship('Usuario', foreign_keys=[creado_por])


class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'referencia_tipo', 'referencia_id', name='uq_notificacion_referencia_usuario'),
        {'schema': 'rrhh'},
    )

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id', ondelete='CASCADE'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), default='informacion', nullable=False)
    referencia_tipo = db.Column(db.String(50))
    referencia_id = db.Column(db.Integer)
    leida = db.Column(db.Boolean, default=False, nullable=False)
    leida_en = db.Column(db.DateTime)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('notificaciones', lazy=True, cascade='all, delete-orphan'))


class TareaChecklist(db.Model):
    __tablename__ = 'tareas_checklist'
    __table_args__ = {'schema': 'rrhh'}

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id', ondelete='CASCADE'), nullable=False)
    descripcion = db.Column(db.String(250), nullable=False)
    completada = db.Column(db.Boolean, default=False, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completado_en = db.Column(db.DateTime)

    usuario = db.relationship('Usuario', backref=db.backref('tareas_checklist', lazy=True, cascade='all, delete-orphan'))


class PermisoUsuario(db.Model):
    __tablename__ = 'permisos_usuario'
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'modulo', 'accion', name='uq_permiso_usuario_modulo_accion'),
        {'schema': 'rrhh'},
    )
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id', ondelete='CASCADE'), nullable=False)
    modulo = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.String(30), nullable=False)
    permitido = db.Column(db.Boolean, default=True, nullable=False)
    asignado_por = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref=db.backref('permisos', lazy=True, cascade='all, delete-orphan'))
    asignador = db.relationship('Usuario', foreign_keys=[asignado_por])


class Auditoria(db.Model):
    __tablename__ = 'auditoria'
    __table_args__ = {'schema': 'rrhh'}
    id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    usuario_nombre = db.Column(db.String(100))
    modulo = db.Column(db.String(60), nullable=False)
    accion = db.Column(db.String(40), nullable=False)
    endpoint = db.Column(db.String(150))
    metodo = db.Column(db.String(10))
    detalle = db.Column(db.Text)
    ip = db.Column(db.String(64))
    estado_http = db.Column(db.Integer)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])


class ErrorSistema(db.Model):
    __tablename__ = 'errores_sistema'
    __table_args__ = {'schema': 'rrhh'}
    id = db.Column(db.BigInteger, primary_key=True)
    codigo = db.Column(db.Integer)
    endpoint = db.Column(db.String(150))
    metodo = db.Column(db.String(10))
    mensaje = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    ip = db.Column(db.String(64))
    revisado = db.Column(db.Boolean, default=False, nullable=False)
    revisado_por = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    revisado_en = db.Column(db.DateTime)
    motivo_revision = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)


class ConfiguracionSistema(db.Model):
    __tablename__ = 'configuracion_sistema'
    __table_args__ = {'schema': 'rrhh'}
    clave = db.Column(db.String(80), primary_key=True)
    valor = db.Column(db.String(250), nullable=False)
    descripcion = db.Column(db.String(250))
    actualizado_por = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SesionUsuario(db.Model):
    __tablename__ = 'sesiones_usuario'
    __table_args__ = {'schema': 'rrhh'}
    id = db.Column(db.String(64), primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id', ondelete='CASCADE'), nullable=False)
    ip = db.Column(db.String(64))
    agente = db.Column(db.Text)
    iniciada_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultima_actividad = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cerrada_en = db.Column(db.DateTime)
    cerrada_por = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'))
    motivo_cierre = db.Column(db.String(200))
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref=db.backref('sesiones', lazy=True, cascade='all, delete-orphan'))


class Empleado2(db.Model):
    """Replica limpia de Trilay; no reemplaza ni modifica rrhh.empleados."""
    __tablename__ = 'empleados2'
    __table_args__ = {'schema': 'rrhh'}
    id = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.Integer, unique=True, nullable=True, index=True)
    cod_usuario = db.Column(db.String(20))
    telefono = db.Column(db.String(100)); telefono_alternativo = db.Column(db.String(15)); telefono_otro = db.Column(db.String(50))
    correo = db.Column(db.String(120)); correo_alternativo = db.Column(db.String(120))
    tipo_documento = db.Column(db.String(20)); numero_documento = db.Column(db.String(100)); sexo = db.Column(db.String(50))
    nivel = db.Column(db.String(100)); numero_nivel = db.Column(db.Integer); nombre = db.Column(db.String(50)); apellido = db.Column(db.String(250))
    codigo_jerarquia_superior = db.Column(db.Integer); numero_legajo = db.Column(db.String(100)); estado_salud = db.Column(db.String(1))
    codigo_dato_empleado = db.Column(db.Integer); cuil = db.Column(db.String(100)); numero_jubilacion = db.Column(db.String(10))
    foto = db.Column(db.String(100)); estado = db.Column(db.Integer); razon = db.Column(db.String(100)); nacionalidad = db.Column(db.String(50))
    fecha_nacimiento = db.Column(db.Date); fecha_ingreso = db.Column(db.Date); fecha_egreso = db.Column(db.Date)
    codigo_estado_civil = db.Column(db.Integer); calle = db.Column(db.String(30)); numero_casa = db.Column(db.String(10))
    numero_departamento = db.Column(db.String(10)); manzana = db.Column(db.String(10)); barrio = db.Column(db.String(30))
    torre = db.Column(db.String(15)); piso = db.Column(db.String(20)); pais = db.Column(db.String(50)); localidad = db.Column(db.String(70))
    provincia = db.Column(db.String(100)); telefono_laboral = db.Column(db.String(100)); horas_extra = db.Column(db.Float); horas_normales = db.Column(db.Float)
    codigo_jerarquia = db.Column(db.Integer); codigo_pais = db.Column(db.Integer); codigo_tipo_documento = db.Column(db.Integer)
    nombre_documento = db.Column(db.String(20)); curp = db.Column(db.String(15)); numero_seguro_social = db.Column(db.String(50))
    fecha_efectivizacion = db.Column(db.Date); codigo_localidad = db.Column(db.Integer); codigo_provincia = db.Column(db.Integer)
    jerarquia_padre = db.Column(db.Integer); huella_origen = db.Column(db.String(64), nullable=False)
    presente_en_origen = db.Column(db.Boolean, nullable=False, default=True); ultima_sincronizacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    nombre_completo = db.Column(db.String(350)); nivel_estudios = db.Column(db.String(150)); grupo_sanguineo = db.Column(db.String(20)); pasaporte = db.Column(db.String(50))
    domicilio = db.Column(db.String(300)); codigo_postal = db.Column(db.String(20)); antiguedad_registrada = db.Column(db.String(100))
    categoria_laboral = db.Column(db.String(150)); codigo_categoria = db.Column(db.String(50)); contrato = db.Column(db.String(100))
    jornada_laboral = db.Column(db.String(100)); horas_jornada = db.Column(db.Numeric(8, 2)); situacion_laboral = db.Column(db.String(100))
    empresa = db.Column(db.String(150)); departamento_area = db.Column(db.String(150)); sector = db.Column(db.String(150)); puesto = db.Column(db.String(150))
    rol_laboral = db.Column(db.String(150)); supervisor = db.Column(db.String(200)); ubicacion_principal = db.Column(db.String(200)); gremio = db.Column(db.String(150))
    movilidad_empleado = db.Column(db.String(100)); licencia_conducir = db.Column(db.String(100))
    sueldo = db.Column(db.Numeric(16, 2)); banco = db.Column(db.String(150)); cuenta_bancaria = db.Column(db.String(100)); cbu = db.Column(db.String(50))
    alias_bancario = db.Column(db.String(100)); moneda = db.Column(db.String(100)); forma_pago = db.Column(db.String(100)); obra_social = db.Column(db.String(150))
    indicador_jubilado = db.Column(db.Boolean); contacto_emergencia_nombre = db.Column(db.String(200)); contacto_emergencia_telefono = db.Column(db.String(100))
    contacto_emergencia_correo = db.Column(db.String(150)); contacto_emergencia_dni = db.Column(db.String(30)); marcacion_web = db.Column(db.Boolean)
    acceso_plataforma_web = db.Column(db.Boolean); id_empleado_postgresql = db.Column(db.Integer); fuentes_origen = db.Column(db.String(250))
    cantidad_fuentes = db.Column(db.Integer); nomina_referencia = db.Column(db.String(500), unique=True); estado_vinculacion = db.Column(db.String(100))
    cantidad_conflictos = db.Column(db.Integer); observaciones_integracion = db.Column(db.Text); origen_nomina = db.Column(db.Boolean, nullable=False, default=False)
    nomina_actualizada_en = db.Column(db.DateTime)


class VacacionSaldo(db.Model):
    """Saldo vacacional consolidado por empleado y período de cálculo."""
    __tablename__ = 'vacaciones_saldos'
    __table_args__ = (
        db.UniqueConstraint('empleado2_id', 'periodo', name='uq_vacaciones_saldo_empleado_periodo'),
        {'schema': 'rrhh'},
    )

    id = db.Column(db.BigInteger, primary_key=True)
    empleado2_id = db.Column(db.BigInteger, db.ForeignKey('rrhh.empleados2.id', ondelete='CASCADE'), nullable=False, index=True)
    periodo = db.Column(db.Integer, nullable=False, index=True)
    fecha_ingreso_calculo = db.Column(db.Date)
    antiguedad_meses = db.Column(db.Integer)
    dias_correspondientes = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    saldo_base = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    ajustes = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    saldo_disponible = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    origen = db.Column(db.String(30), nullable=False, default='CALCULO')
    fila_excel = db.Column(db.Integer)
    fecha_corte = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    empleado2 = db.relationship('Empleado2', backref=db.backref('saldos_vacaciones', lazy=True, cascade='all, delete-orphan'))


class VacacionMovimiento(db.Model):
    """Historial importado y operativo que explica el saldo vacacional."""
    __tablename__ = 'vacaciones_movimientos'
    __table_args__ = (
        db.UniqueConstraint('origen', 'referencia_origen', name='uq_vacaciones_movimiento_origen'),
        {'schema': 'rrhh'},
    )

    id = db.Column(db.BigInteger, primary_key=True)
    empleado2_id = db.Column(db.BigInteger, db.ForeignKey('rrhh.empleados2.id', ondelete='CASCADE'), nullable=False, index=True)
    saldo_id = db.Column(db.BigInteger, db.ForeignKey('rrhh.vacaciones_saldos.id', ondelete='SET NULL'))
    licencia_id = db.Column(db.Integer, db.ForeignKey('rrhh.licencias.id', ondelete='SET NULL'))
    tipo = db.Column(db.String(40), nullable=False)
    fecha_desde = db.Column(db.Date)
    fecha_hasta = db.Column(db.Date)
    fecha_reintegro = db.Column(db.Date)
    dias = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    saldo_resultante = db.Column(db.Numeric(8, 2))
    detalle = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    origen = db.Column(db.String(30), nullable=False, default='SISTEMA')
    referencia_origen = db.Column(db.String(100), nullable=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    empleado2 = db.relationship('Empleado2', backref=db.backref('movimientos_vacaciones', lazy=True, cascade='all, delete-orphan'))
    saldo = db.relationship('VacacionSaldo', backref=db.backref('movimientos', lazy=True))
    licencia = db.relationship('Licencia')
