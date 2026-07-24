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
    rol_id = db.Column(db.Integer, db.ForeignKey('rrhh.roles.id'), nullable=False)
    usuario = db.Column(db.String(100), unique=True, nullable=False)
    correo = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    ultimo_acceso = db.Column(db.DateTime)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    empleado = db.relationship('Empleado')

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
    estado = db.Column(db.String(50), default='Borrador')
    visible_todos = db.Column(db.Boolean, default=True)
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
