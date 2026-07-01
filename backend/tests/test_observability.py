import json
import logging

from fastapi.testclient import TestClient

from app.main import app
from app.observability import init_sentry


def test_sentry_noop_without_dsn(monkeypatch) -> None:
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    assert init_sentry() is False


def test_request_id_header_and_structured_log(caplog) -> None:
    caplog.set_level(logging.INFO, logger="charter_law.request")

    response = TestClient(app).get("/health", headers={"x-request-id": "req_test_123"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req_test_123"
    records = [record for record in caplog.records if record.name == "charter_law.request"]
    assert records
    payload = json.loads(records[-1].message)
    assert payload["event"] == "request"
    assert payload["request_id"] == "req_test_123"
    assert payload["method"] == "GET"
    assert payload["path"] == "/health"
    assert payload["status_code"] == 200
    assert "body" not in payload
