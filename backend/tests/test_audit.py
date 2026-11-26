from starlette.requests import Request

from app.middleware.audit import _classification


def _request(method: str, path: str) -> Request:
    return Request({"type": "http", "method": method, "path": path, "raw_path": path.encode(), "query_string": b"", "headers": [], "client": ("127.0.0.1", 1), "server": ("test", 80), "scheme": "http"})


def test_audit_classification_does_not_capture_payloads():
    assert _classification(_request("GET", "/api/v1/employees")) == ("employees", "consultar")
    assert _classification(_request("POST", "/api/v1/documents")) == ("documents", "crear")
    assert _classification(_request("DELETE", "/api/v1/news/5")) == ("news", "anular")
