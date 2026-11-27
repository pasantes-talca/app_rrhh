"""Pruebas aisladas de recibos con firmas ES256 reales y datos sintéticos."""
import base64
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

import cbor2
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from flask import Flask, g
from itsdangerous import URLSafeTimedSerializer
from jinja2 import ChoiceLoader, DictLoader, FileSystemLoader
from sqlalchemy import event

from database.models import DocumentoRRHH, Empleado, ReciboSueldo, Rol, TipoDocumento, Usuario
from extensions import db, login_manager
from modules.documentos.passkey_models import ReceiptChallenge, ReceiptCredential, ReceiptSignature
from modules.documentos.routes import documentos_bp


def b64(value):
    return base64.urlsafe_b64encode(value).decode().rstrip('=')


@pytest.fixture()
def receipt_env():
    app = Flask(__name__)
    app.config.update(TESTING=True, SECRET_KEY='synthetic-receipt-tests',
                      SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
                      RECEIPT_PASSKEY_ENABLED=True, WEBAUTHN_RP_ID='localhost',
                      WEBAUTHN_ORIGIN='http://localhost:5000', TRILAY_SYNC_ENABLED=False)
    db.init_app(app)
    login_manager.init_app(app)
    previous_login_view = login_manager.login_view
    login_manager.login_view = None
    app.register_blueprint(documentos_bp)
    app.add_url_rule('/auth/perfil', endpoint='auth.perfil', view_func=lambda: 'Perfil sintético')
    app.jinja_loader = ChoiceLoader([
        DictLoader({'base.html': '{% block content %}{% endblock %}{% block scripts %}{% endblock %}'}),
        FileSystemLoader(str(Path(__file__).resolve().parents[1] / 'templates')),
    ])

    @app.before_request
    def refresh_test_identity():
        # El fixture mantiene el contexto ORM; cada solicitud debe cargar su propia identidad.
        g.pop('_login_user', None)

    with app.app_context():
        @event.listens_for(db.engine, 'connect')
        def attach(connection, _):
            connection.execute("ATTACH DATABASE ':memory:' AS rrhh")

        @login_manager.user_loader
        def load(user_id):
            return db.session.get(Usuario, int(user_id))

        db.create_all()
        role = Rol(id=1, nombre='empleado')
        owner = Empleado(id=1, nombre_apellido='Persona Sintética', dni='TEST-1')
        other = Empleado(id=2, nombre_apellido='Otra Persona', dni='TEST-2')
        db.session.add_all([role, owner, other])
        db.session.flush()
        from werkzeug.security import generate_password_hash
        db.session.add_all([
            Usuario(id=1, empleado_id=1, rol_id=1, usuario='synthetic1', password_hash=generate_password_hash('Synthetic!2026')),
            Usuario(id=2, empleado_id=2, rol_id=1, usuario='synthetic2', password_hash=generate_password_hash('Synthetic!2026')),
            TipoDocumento(id=1, nombre='Recibo'),
        ])
        db.session.flush()
        db.session.add(DocumentoRRHH(id=1, empleado_id=1, tipo_documento_id=1,
                                    nombre_documento='Synthetic PDF', nombre_archivo='test.pdf',
                                    ruta_archivo='test.pdf', cargado_por=1))
        db.session.flush()
        db.session.add(ReciboSueldo(id=1, documento_id=1, empleado_id=1, periodo='2026-11',
                                   hash_archivo='a' * 64, publicado_por=1))
        key = ec.generate_private_key(ec.SECP256R1())
        numbers = key.public_key().public_numbers()
        public = cbor2.dumps({1: 2, 3: -7, -1: 1,
                            -2: numbers.x.to_bytes(32, 'big'), -3: numbers.y.to_bytes(32, 'big')})
        db.session.add(ReceiptCredential(usuario_id=1, credential_id=b64(b'credential-test'),
                                         public_key=public, sign_count=0))
        db.session.commit()
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['_user_id'] = '1'
            sess['_fresh'] = True
            sess['csrf_token'] = 'synthetic-csrf'
        token = URLSafeTimedSerializer(app.secret_key, salt='wtf-csrf-token').dumps('synthetic-csrf')
        headers = {'Origin': 'http://localhost:5000', 'X-CSRFToken': token}
        with patch('modules.documentos.routes.hash_archivo', return_value='a' * 64):
            yield app, client, headers, key
        db.session.remove()
        db.drop_all()
        login_manager.login_view = previous_login_view


def options(client, headers, **changes):
    return client.post('/documentos/recibos/1/passkey/opciones', headers=headers,
                       json={'purpose': 'sign', 'respuesta': 'Conforme', 'observacion': '', **changes})


def assertion(result, key, uv=True, origin='http://localhost:5000'):
    data = json.dumps({'type': 'webauthn.get', 'challenge': result['publicKey']['challenge'],
                       'origin': origin}).encode()
    auth = hashlib.sha256(b'localhost').digest() + bytes([5 if uv else 1]) + (1).to_bytes(4, 'big')
    signature = key.sign(auth + hashlib.sha256(data).digest(), ec.ECDSA(hashes.SHA256()))
    return {'id': b64(b'credential-test'), 'rawId': b64(b'credential-test'), 'type': 'public-key',
            'response': {'clientDataJSON': b64(data), 'authenticatorData': b64(auth),
                         'signature': b64(signature), 'userHandle': None}}


def verify(client, headers, result, credential):
    return client.post('/documentos/recibos/1/passkey/verificar', headers=headers,
                       json={'purpose': 'sign', 'challenge_id': result['challenge_id'], 'credential': credential})


def test_real_signature_atomically_records_receipt_and_evidence(receipt_env):
    _, client, headers, key = receipt_env
    result = options(client, headers).get_json()
    assert verify(client, headers, result, assertion(result, key)).status_code == 200
    assert db.session.get(ReciboSueldo, 1).estado == 'Conforme'
    assert ReceiptSignature.query.one().document_hash == 'a' * 64
    assert ReceiptCredential.query.one().sign_count == 1


@pytest.mark.parametrize('case', ['missing_uv', 'wrong_origin', 'wrong_key', 'tampered_challenge'])
def test_invalid_assertions_never_respond_or_store_signature(receipt_env, case):
    _, client, headers, key = receipt_env
    result = options(client, headers).get_json()
    signed = result.copy()
    if case == 'tampered_challenge':
        signed = {**result, 'publicKey': {**result['publicKey'], 'challenge': b64(b'wrong-challenge')}}
    credential = assertion(signed, ec.generate_private_key(ec.SECP256R1()) if case == 'wrong_key' else key,
                           uv=case != 'missing_uv', origin='https://evil.invalid' if case == 'wrong_origin' else 'http://localhost:5000')
    assert verify(client, headers, result, credential).status_code == 400
    assert ReceiptSignature.query.count() == 0
    assert db.session.get(ReciboSueldo, 1).estado == 'Pendiente'
    assert ReceiptChallenge.query.one().consumed_at is not None


@pytest.mark.parametrize('case', ['expired', 'replayed', 'different_session'])
def test_expired_consumed_and_other_session_challenges_rejected(receipt_env, case):
    _, client, headers, key = receipt_env
    result = options(client, headers).get_json()
    challenge = ReceiptChallenge.query.one()
    if case == 'expired':
        challenge.expires_at = datetime.utcnow() - timedelta(seconds=1)
    elif case == 'replayed':
        challenge.consumed_at = datetime.utcnow()
    else:
        challenge.session_binding = 'another-session'
    db.session.commit()
    assert verify(client, headers, result, assertion(result, key)).status_code == 400
    assert ReceiptSignature.query.count() == 0


def test_foreign_employee_and_legacy_bypass_rejected(receipt_env):
    _, client, headers, _ = receipt_env
    assert client.post('/documentos/recibos/1/responder', data={'respuesta': 'Conforme'}).status_code == 403
    with client.session_transaction() as sess:
        sess['_user_id'] = '2'
    assert options(client, headers).status_code == 403


def test_csrf_origin_and_observation_required(receipt_env):
    _, client, headers, _ = receipt_env
    assert options(client, {'Origin': headers['Origin']}).status_code == 400
    assert options(client, {**headers, 'Origin': 'https://evil.invalid'}).status_code == 403
    assert options(client, headers, respuesta='Disconforme').status_code == 400
    assert options(client, headers, observacion='x' * 2001).status_code == 400


def test_pdf_change_blocks_verification(receipt_env):
    _, client, headers, key = receipt_env
    result = options(client, headers).get_json()
    with patch('modules.documentos.routes.hash_archivo', return_value='b' * 64):
        assert verify(client, headers, result, assertion(result, key)).status_code == 409
    assert ReceiptSignature.query.count() == 0


def test_registration_requires_password_and_device_verification(receipt_env):
    _, client, headers, _ = receipt_env
    ReceiptCredential.query.delete()
    db.session.commit()
    assert options(client, headers, purpose='register', password='wrong').status_code == 403
    response = options(client, headers, purpose='register', password='Synthetic!2026')
    assert response.status_code == 200
    assert response.json['publicKey']['authenticatorSelection']['userVerification'] == 'required'
    assert response.json['publicKey']['authenticatorSelection']['authenticatorAttachment'] == 'platform'


def test_feature_disabled_and_anonymous_access_fail_closed(receipt_env):
    app, client, headers, _ = receipt_env
    app.config['RECEIPT_PASSKEY_ENABLED'] = False
    assert options(client, headers).status_code == 503
    with client.session_transaction() as sess:
        sess.clear()
    assert options(client, headers).status_code == 401


@pytest.mark.parametrize('enabled', [False, True])
def test_receipt_screen_renders_with_csrf_and_matching_flow(receipt_env, enabled):
    app, client, _, _ = receipt_env
    app.config['RECEIPT_PASSKEY_ENABLED'] = enabled
    response = client.get('/documentos/recibos/1')
    assert response.status_code == 200
    assert (b'receipt-passkey.js' in response.data) == enabled
    assert (b'id="receipt-csrf"' in response.data) == enabled
    assert b'Undefined' not in response.data


@pytest.mark.parametrize('uv', [True, False])
@pytest.mark.parametrize('from_profile', [False, True])
def test_real_device_registration_verifies_attestation_and_user_verification(receipt_env, uv, from_profile):
    _, client, headers, key = receipt_env
    ReceiptCredential.query.delete()
    db.session.commit()
    if from_profile:
        result = client.post('/documentos/passkey/opciones', headers=headers,
                             json={'purpose': 'register', 'password': 'Synthetic!2026'}).json
        assert ReceiptChallenge.query.one().recibo_id is None
    else:
        result = options(client, headers, purpose='register', password='Synthetic!2026').json
    numbers = key.public_key().public_numbers()
    public = cbor2.dumps({1: 2, 3: -7, -1: 1,
                        -2: numbers.x.to_bytes(32, 'big'), -3: numbers.y.to_bytes(32, 'big')})
    credential_id = b'new-credential'
    auth = (hashlib.sha256(b'localhost').digest() + bytes([0x45 if uv else 0x41])
            + bytes(4) + bytes(16) + len(credential_id).to_bytes(2, 'big') + credential_id + public)
    client_data = json.dumps({'type': 'webauthn.create', 'challenge': result['publicKey']['challenge'],
                              'origin': 'http://localhost:5000'}).encode()
    credential = {'id': b64(credential_id), 'rawId': b64(credential_id), 'type': 'public-key',
                  'response': {'clientDataJSON': b64(client_data),
                               'attestationObject': b64(cbor2.dumps({'fmt': 'none', 'attStmt': {}, 'authData': auth}))}}
    url = '/documentos/passkey/verificar' if from_profile else '/documentos/recibos/1/passkey/verificar'
    response = client.post(url, headers=headers,
                           json={'purpose': 'register', 'challenge_id': result['challenge_id'], 'credential': credential})
    assert response.status_code == (200 if uv else 400)
    assert ReceiptCredential.query.count() == (1 if uv else 0)
    assert db.session.get(ReciboSueldo, 1).estado == 'Pendiente'


def test_disabled_signing_never_falls_back_to_password_or_button(receipt_env):
    app, client, _, _ = receipt_env
    app.config['RECEIPT_PASSKEY_ENABLED'] = False
    assert client.post('/documentos/recibos/1/responder', data={'respuesta': 'Conforme'}).status_code == 403
    page = client.get('/documentos/recibos/1')
    assert page.status_code == 200
    assert b'name="respuesta"' not in page.data
    assert db.session.get(ReciboSueldo, 1).estado == 'Pendiente'


def test_profile_endpoint_cannot_sign_receipts(receipt_env):
    _, client, headers, _ = receipt_env
    response = client.post('/documentos/passkey/opciones', headers=headers,
                           json={'purpose': 'sign', 'respuesta': 'Conforme'})
    assert response.status_code == 400


def test_profile_registration_is_bound_to_user_and_not_receipt(receipt_env):
    _, client, headers, _ = receipt_env
    ReceiptCredential.query.delete()
    db.session.commit()
    with client.session_transaction() as sess:
        sess['_user_id'] = '2'
    result = client.post('/documentos/passkey/opciones', headers=headers,
                         json={'purpose': 'register', 'password': 'Synthetic!2026'})
    assert result.status_code == 200
    challenge = ReceiptChallenge.query.one()
    assert challenge.usuario_id == 2
    assert challenge.recibo_id is None
