"""Persistencia de claves públicas y constancias WebAuthn; nunca datos biométricos."""
from datetime import datetime

from extensions import db


class ReceiptCredential(db.Model):
    __tablename__ = 'recibo_credenciales'
    __table_args__ = {'schema': 'rrhh'}
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'), nullable=False, unique=True, index=True)
    credential_id = db.Column(db.Text, unique=True, nullable=False)
    public_key = db.Column(db.LargeBinary, nullable=False)
    sign_count = db.Column(db.BigInteger, nullable=False, default=0)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ReceiptChallenge(db.Model):
    __tablename__ = 'recibo_desafios'
    __table_args__ = {'schema': 'rrhh'}
    id = db.Column(db.String(64), primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'), nullable=False)
    recibo_id = db.Column(db.Integer, db.ForeignKey('rrhh.recibos_sueldo.id'), nullable=True)
    purpose = db.Column(db.String(16), nullable=False)
    challenge = db.Column(db.LargeBinary, nullable=False)
    session_binding = db.Column(db.String(64), nullable=False)
    respuesta = db.Column(db.String(20))
    observacion = db.Column(db.Text)
    document_hash = db.Column(db.String(64), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    consumed_at = db.Column(db.DateTime)


class ReceiptSignature(db.Model):
    __tablename__ = 'recibo_firmas'
    __table_args__ = {'schema': 'rrhh'}
    id = db.Column(db.Integer, primary_key=True)
    recibo_id = db.Column(db.Integer, db.ForeignKey('rrhh.recibos_sueldo.id'), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('rrhh.usuarios.id'), nullable=False)
    credencial_id = db.Column(db.Integer, db.ForeignKey('rrhh.recibo_credenciales.id'), nullable=False)
    desafio_id = db.Column(db.String(64), db.ForeignKey('rrhh.recibo_desafios.id'), unique=True, nullable=False)
    document_hash = db.Column(db.String(64), nullable=False)
    respuesta = db.Column(db.String(20), nullable=False)
    observacion = db.Column(db.Text)
    evidencia = db.Column(db.JSON, nullable=False)
    origin = db.Column(db.Text, nullable=False)
    rp_id = db.Column(db.Text, nullable=False)
    firmado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
