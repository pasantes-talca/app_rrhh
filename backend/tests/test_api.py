from fastapi.testclient import TestClient

from app.main import create_app


def test_health_contract():
    response = TestClient(create_app()).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok", "service": "talca-rrhh-api", "version": "v1",
    }
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert response.headers["cache-control"] == "no-store"


def test_employees_is_default_denied_without_session():
    response = TestClient(create_app()).get("/api/v1/employees")
    assert response.status_code == 401
    assert response.json()["detail"] == "authentication_required"


def test_private_documents_and_receipts_are_default_denied_without_session():
    client = TestClient(create_app())
    for path in ("/api/v1/documents", "/api/v1/documents/folders", "/api/v1/documents/receipts/list"):
        response = client.get(path)
        assert response.status_code == 401
        assert response.json()["detail"] == "authentication_required"

