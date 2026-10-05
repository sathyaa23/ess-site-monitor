"""
Integration tests - test the API endpoints end to end (routing, request
parsing, validation, storage, response) using FastAPI's TestClient.

These are slower than unit tests and fewer in number (middle of the pyramid).
They catch wiring bugs that unit tests can't - e.g. a validator that works
but is never called by the endpoint.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Smoke-style check that the app is alive."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_valid_reading_is_saved():
    resp = client.post("/telemetry", json={
        "site_id": "SITE-TX-01",
        "voltage": 400.0,
        "temperature": 25.0,
        "state_of_charge": 80.0,
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "saved"
    assert body["valid"] is True


def test_bad_voltage_is_rejected():
    resp = client.post("/telemetry", json={
        "site_id": "SITE-TX-01",
        "voltage": 5000.0,   # out of range
        "temperature": 25.0,
        "state_of_charge": 80.0,
    })
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert "voltage" in detail["failed_fields"]


def test_bad_temperature_is_rejected():
    resp = client.post("/telemetry", json={
        "site_id": "SITE-TX-01",
        "voltage": 400.0,
        "temperature": 90.0,   # thermal runaway range
        "state_of_charge": 80.0,
    })
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert "temperature" in detail["failed_fields"]
    assert detail["severity"] == "critical"


def test_malformed_payload_is_rejected():
    """Missing fields -> FastAPI/Pydantic returns 422 automatically."""
    resp = client.post("/telemetry", json={"site_id": "SITE-TX-01"})
    assert resp.status_code == 422


def test_dashboard_serves_html():
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert "ESS Site Monitor" in resp.text
    assert 'id="submit-btn"' in resp.text
