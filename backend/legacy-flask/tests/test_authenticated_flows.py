"""Flujos Flask autenticados con datos sintéticos y SQLite efímero."""
import pytest
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

from app import create_app
from database.models import DocumentoRRHH, Empleado, Rol, TipoDocumento, Usuario
from extensions import db
from modules.security.hardening import apply_flask_security


class IsolatedConfig:
    TESTING = True
    SECRET_KEY = "synthetic-auth-tests"
    SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": StaticPool,
        "connect_args": {"check_same_thread": False},
    }
    WTF_CSRF_ENABLED = False
    TRILAY_SYNC_ENABLED = False
    UPLOAD_FOLDER = ".test-artifacts/uploads"


@pytest.fixture()
def synthetic_app():
    app = create_app(IsolatedConfig)
    with app.app_context():
        @event.listens_for(db.engine, "connect")
        def attach_schema(dbapi_connection, connection_record):
            dbapi_connection.execute("ATTACH DATABASE ':memory:' AS rrhh")

        db.create_all()
        roles = {
            name: Rol(nombre=name, descripcion=f"Rol sintético {name}")
            for name in ("empleado", "recursos_humanos", "administrador")
        }
        db.session.add_all(roles.values())
        own = Empleado(nombre_apellido="Persona Propia", dni="10000001", legajo="T-1")
        other = Empleado(nombre_apellido="Persona Ajena", dni="10000002", legajo="T-2")
        db.session.add_all([own, other])
        db.session.flush()
        db.session.add_all([
            Usuario(
                empleado_id=own.id, rol=roles["empleado"], usuario="synthetic.employee",
                password_hash=generate_password_hash("Synthetic!2026"), activo=True,
            ),
            Usuario(
                empleado_id=other.id, rol=roles["empleado"], usuario="synthetic.other",
                password_hash=generate_password_hash("Synthetic!2026"), activo=True,
            ),
            Usuario(
                rol=roles["empleado"], usuario="synthetic.inactive",
                password_hash=generate_password_hash("Synthetic!2026"), activo=False,
            ),
            Usuario(
                rol=roles["recursos_humanos"], usuario="synthetic.hr",
                password_hash=generate_password_hash("Synthetic!2026"), activo=True,
            ),
        ])
        db.session.commit()
        yield app, own.id, other.id
        db.session.remove()
        db.drop_all()


def login(client, username, password="Synthetic!2026"):
    return client.post("/auth/login", data={"usuario": username, "password": password})


def test_login_logout_and_session_record(synthetic_app):
    app, _, _ = synthetic_app
    client = app.test_client()
    response = login(client, " SYNTHETIC.EMPLOYEE ")
    assert response.status_code == 302
    assert response.location.endswith("/dashboard/")
    response = client.get("/auth/logout")
    assert response.status_code == 302
    assert response.location.endswith("/auth/login")


def test_invalid_password_does_not_authenticate(synthetic_app):
    app, _, _ = synthetic_app
    client = app.test_client()
    response = login(client, "synthetic.employee", "wrong")
    assert response.status_code == 200
    assert b"incorrectos" in response.data


def test_inactive_account_is_rejected(synthetic_app):
    app, _, _ = synthetic_app
    client = app.test_client()
    response = login(client, "synthetic.inactive")
    assert response.status_code == 302
    assert response.location.endswith("/auth/login")


def test_employee_can_view_own_record_but_not_other(synthetic_app):
    app, own_id, other_id = synthetic_app
    client = app.test_client()
    login(client, "synthetic.employee")
    own = client.get(f"/empleados/{own_id}")
    assert own.status_code == 200
    denied = client.get(f"/empleados/{other_id}")
    assert denied.status_code == 302
    assert denied.location.endswith("/dashboard/")


def test_hr_can_list_employees(synthetic_app):
    app, _, _ = synthetic_app
    client = app.test_client()
    login(client, "synthetic.hr")
    response = client.get("/empleados/")
    assert response.status_code == 200
    assert b"Persona Propia" in response.data


def test_employee_cannot_read_other_private_document(synthetic_app):
    app, own_id, other_id = synthetic_app
    with app.app_context():
        document_type = TipoDocumento(nombre="Documento sintético", activo=True)
        uploader = Usuario.query.filter_by(usuario="synthetic.hr").one()
        document = DocumentoRRHH(
            empleado_id=other_id, tipo_documento=document_type,
            nombre_documento="Privado ajeno", nombre_archivo="synthetic.pdf",
            ruta_archivo="not-read-in-this-test.pdf", visible_empleado=True,
            estado="Activo", cargado_por=uploader.id,
        )
        db.session.add(document)
        db.session.commit()
        document_id = document.id
    client = app.test_client()
    login(client, "synthetic.employee")
    response = client.get(f"/documentos/{document_id}")
    assert response.status_code == 403


@pytest.mark.xfail(strict=True, reason="SEC-003: no existe CSRFProtect global")
def test_current_app_target_rejects_login_without_csrf_token():
    class CsrfConfig(IsolatedConfig):
        WTF_CSRF_ENABLED = True

    app = create_app(CsrfConfig)
    response = app.test_client().post(
        "/auth/login", data={"usuario": "synthetic", "password": "Synthetic!2026"},
    )
    assert response.status_code == 400


def test_hardening_prototype_rejects_login_without_csrf_token():
    class CsrfConfig(IsolatedConfig):
        WTF_CSRF_ENABLED = True

    app = apply_flask_security(create_app(CsrfConfig))
    response = app.test_client().post(
        "/auth/login", data={"usuario": "synthetic", "password": "Synthetic!2026"},
    )
    assert response.status_code == 400


@pytest.mark.xfail(strict=True, reason="SEC-002: logout actual permite GET")
def test_logout_target_requires_post_only(synthetic_app):
    app, _, _ = synthetic_app
    methods = app.url_map._rules_by_endpoint["auth.logout"][0].methods
    assert "GET" not in methods

