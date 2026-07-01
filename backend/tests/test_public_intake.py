from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.main import app
from app.middleware.public_hardening import public_rate_limiter
from app.models.intake import PublicIntakeModel
from app.schemas.public import PublicIntakeRequest
from app.services.intake_service import IntakeService


def setup_function() -> None:
    public_rate_limiter.clear()


def test_public_intake_persists_lead(session_factory: sessionmaker[Session]) -> None:
    service = IntakeService(session_factory)

    response = service.create_public_intake(
        PublicIntakeRequest(
            name="Maya Founder",
            email=" MAYA@EXAMPLE.COM ",
            company="Acme Labs",
            contractType="vendor_saas",
            urgency="standard",
            serviceTier="standard_redline",
            notes="Need a clean redline before Friday.",
        )
    )

    assert response.intake_id.startswith("intake_")
    assert response.status == "new"
    assert "before any legal work begins" in response.message

    with session_factory() as db:
        row = db.scalar(select(PublicIntakeModel).where(PublicIntakeModel.id == response.intake_id))

    assert row is not None
    assert row.email == "maya@example.com"
    assert row.company == "Acme Labs"
    assert row.service_tier == "standard_redline"


def test_public_intake_endpoint_validates_required_fields() -> None:
    client = TestClient(app)

    response = client.post("/v1/public/intake", json={"email": "not-enough@example.com"})

    assert response.status_code == 422


def test_public_intake_endpoint_validates_email() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/public/intake",
        json={
            "name": "Maya Founder",
            "email": "not-an-email",
            "company": "Acme Labs",
            "contractType": "vendor_saas",
            "urgency": "standard",
            "serviceTier": "standard_redline",
        },
    )

    assert response.status_code == 422


def test_public_intake_rate_limits_by_client_ip(monkeypatch) -> None:
    monkeypatch.setenv("PUBLIC_RATE_LIMIT_PER_MINUTE", "1")
    client = TestClient(app)
    payload = {"email": "missing-required-fields@example.com"}

    first = client.post("/v1/public/intake", json=payload, headers={"x-forwarded-for": "203.0.113.11"})
    second = client.post("/v1/public/intake", json=payload, headers={"x-forwarded-for": "203.0.113.11"})

    assert first.status_code == 422
    assert second.status_code == 429
