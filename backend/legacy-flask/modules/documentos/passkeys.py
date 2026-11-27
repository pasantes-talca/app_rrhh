"""Ceremonias WebAuthn para recibos del sistema Flask operativo."""
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlparse

from flask import abort, current_app, jsonify, request, session
from flask_login import current_user, login_required
from flask_wtf.csrf import validate_csrf
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from wtforms.validators import ValidationError

from database.models import ReciboSueldo
from extensions import db
from .passkey_models import ReceiptChallenge, ReceiptCredential, ReceiptSignature


def _context():
    if not current_app.config.get('RECEIPT_PASSKEY_ENABLED'):
        abort(503, description='La firma con passkey todavía no está habilitada.')
    origin = current_app.config['WEBAUTHN_ORIGIN'].rstrip('/')
    rp_id = current_app.config['WEBAUTHN_RP_ID']
    parsed = urlparse(origin)
    if (parsed.hostname != rp_id or parsed.path not in ('', '/') or parsed.query
            or parsed.fragment or parsed.username or parsed.password
            or (parsed.scheme != 'https' and not (
                parsed.scheme == 'http' and rp_id in ('localhost', '127.0.0.1')))):
        abort(503, description='La configuración del dominio WebAuthn es inválida.')
    if request.headers.get('Origin') != origin:
        abort(403, description='Origen no autorizado para firmar.')
    try:
        validate_csrf(request.headers.get('X-CSRFToken'))
    except ValidationError:
        abort(400, description='La sesión del formulario venció. Recargá la página.')
    if request.content_length is None or request.content_length > 32768:
        abort(413)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        abort(400)
    session.setdefault('receipt_binding', secrets.token_hex(32))
    return payload, origin, rp_id


def _owned_receipt(receipt_id, lock=False):
    query = ReciboSueldo.query.filter_by(id=receipt_id)
    if lock:
        query = query.with_for_update()
    receipt = query.first_or_404()
    if not current_user.empleado_id or receipt.empleado_id != current_user.empleado_id:
        abort(403)
    if receipt.estado != 'Pendiente':
        abort(409, description='Este recibo ya fue respondido.')
    return receipt


def _digest(receipt):
    from .routes import hash_archivo
    value = hash_archivo(receipt.documento.ruta_archivo)
    if not secrets.compare_digest(value, receipt.hash_archivo):
        abort(409, description='El PDF cambió. RR. HH. debe revisar el recibo.')
    return value


def _consume(challenge_id, receipt, purpose):
    challenge = ReceiptChallenge.query.filter_by(
        id=challenge_id, usuario_id=current_user.id, recibo_id=receipt.id,
        purpose=purpose,
    ).with_for_update().first()
    if (not challenge or challenge.consumed_at or challenge.expires_at <= datetime.utcnow()
            or challenge.session_binding != session['receipt_binding']):
        abort(400, description='La verificación venció o ya fue utilizada.')
    challenge.consumed_at = datetime.utcnow()
    return challenge


def register_routes(blueprint):
    @blueprint.route('/recibos/<int:id>/passkey/opciones', methods=['POST'])
    @login_required
    def passkey_options(id):
        from webauthn import generate_authentication_options, generate_registration_options
        from webauthn.helpers import base64url_to_bytes, options_to_json
        from webauthn.helpers.structs import (
            AuthenticatorAttachment, AuthenticatorSelectionCriteria,
            PublicKeyCredentialDescriptor, UserVerificationRequirement,
        )
        payload, _, rp_id = _context()
        receipt = _owned_receipt(id)
        purpose = payload.get('purpose')
        if purpose not in ('register', 'sign'):
            abort(400)
        now = datetime.utcnow()
        recent = ReceiptChallenge.query.filter(
            ReceiptChallenge.usuario_id == current_user.id,
            ReceiptChallenge.expires_at > now - timedelta(minutes=7),
        ).count()
        if recent >= 10:
            abort(429, description='Demasiados intentos. Esperá unos minutos.')
        credentials = ReceiptCredential.query.filter_by(usuario_id=current_user.id).all()
        digest = _digest(receipt)
        challenge = ReceiptChallenge(
            id=secrets.token_hex(32), usuario_id=current_user.id, recibo_id=id,
            purpose=purpose, challenge=secrets.token_bytes(32),
            session_binding=session['receipt_binding'], document_hash=digest,
            expires_at=now + timedelta(minutes=3),
        )
        db.session.add(challenge)
        if purpose == 'register':
            # Un usuario no puede reemplazar la clave existente desde una sesión robada.
            if credentials:
                abort(409, description='Ya tenés una passkey registrada. Usala para firmar.')
            password = payload.get('password')
            if not isinstance(password, str) or not check_password_hash(current_user.password_hash, password):
                challenge.consumed_at = now
                db.session.commit()
                abort(403, description='La contraseña actual no es correcta.')
            options = generate_registration_options(
                rp_id=rp_id, rp_name='Talca Personas',
                user_id=hashlib.sha256(f'talca-user:{current_user.id}'.encode()).digest(),
                user_name=current_user.usuario, challenge=challenge.challenge,
                authenticator_selection=AuthenticatorSelectionCriteria(
                    authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                    user_verification=UserVerificationRequirement.REQUIRED,
                ),
            )
        else:
            if not credentials:
                abort(409, description='Registrá primero tu dispositivo.')
            answer = payload.get('respuesta')
            observation = payload.get('observacion', '')
            if (answer not in ('Conforme', 'Disconforme') or not isinstance(observation, str)
                    or len(observation) > 2000 or (answer == 'Disconforme' and not observation.strip())):
                abort(400, description='Revisá la respuesta y la observación (máximo 2000 caracteres).')
            challenge.respuesta = answer
            challenge.observacion = observation.strip()
            options = generate_authentication_options(
                rp_id=rp_id, challenge=challenge.challenge,
                allow_credentials=[PublicKeyCredentialDescriptor(
                    id=base64url_to_bytes(c.credential_id)
                ) for c in credentials],
                user_verification=UserVerificationRequirement.REQUIRED,
            )
        db.session.commit()
        response = jsonify(challenge_id=challenge.id, publicKey=json.loads(options_to_json(options)))
        response.headers['Cache-Control'] = 'no-store'
        return response

    @blueprint.route('/recibos/<int:id>/passkey/verificar', methods=['POST'])
    @login_required
    def passkey_verify(id):
        from webauthn import verify_authentication_response, verify_registration_response
        from webauthn.helpers import bytes_to_base64url
        from webauthn.helpers.exceptions import WebAuthnException
        payload, origin, rp_id = _context()
        receipt = _owned_receipt(id, lock=True)
        purpose = payload.get('purpose')
        if purpose not in ('register', 'sign') or not isinstance(payload.get('challenge_id'), str):
            abort(400)
        challenge = _consume(payload['challenge_id'], receipt, purpose)
        credential = payload.get('credential')
        if not isinstance(credential, dict):
            abort(400)
        digest = _digest(receipt)
        if not secrets.compare_digest(challenge.document_hash, digest):
            abort(409)
        try:
            if purpose == 'register':
                if ReceiptCredential.query.filter_by(usuario_id=current_user.id).first():
                    abort(409)
                result = verify_registration_response(
                    credential=credential, expected_challenge=challenge.challenge,
                    expected_rp_id=rp_id, expected_origin=origin, require_user_verification=True,
                )
                db.session.add(ReceiptCredential(
                    usuario_id=current_user.id, credential_id=bytes_to_base64url(result.credential_id),
                    public_key=result.credential_public_key, sign_count=result.sign_count,
                ))
            else:
                stored = ReceiptCredential.query.filter_by(
                    credential_id=credential.get('id'), usuario_id=current_user.id,
                ).with_for_update().first()
                if not stored:
                    abort(403)
                result = verify_authentication_response(
                    credential=credential, expected_challenge=challenge.challenge,
                    expected_rp_id=rp_id, expected_origin=origin,
                    credential_public_key=stored.public_key,
                    credential_current_sign_count=stored.sign_count, require_user_verification=True,
                )
                stored.sign_count = result.new_sign_count
                db.session.add(ReceiptSignature(
                    recibo_id=id, usuario_id=current_user.id, credencial_id=stored.id,
                    desafio_id=challenge.id, document_hash=digest,
                    respuesta=challenge.respuesta, observacion=challenge.observacion,
                    evidencia=credential, origin=origin, rp_id=rp_id,
                ))
        except (WebAuthnException, ValueError, TypeError, KeyError):
            # El desafío rechazado se consume sin guardar una firma ni una respuesta.
            db.session.commit()
            abort(400, description='No se pudo verificar el dispositivo. Intentá nuevamente.')
        if purpose == 'sign':
            from .routes import record_receipt_response
            record_receipt_response(receipt, challenge.respuesta, challenge.observacion)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, description='La operación ya fue registrada. Recargá la página.')
        return jsonify(ok=True)
