from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.main import app
from app.models.intake import PublicIntakeModel
from app.schemas.public import PublicIntakeRequest
from app.services.intake_service import IntakeService


def test_public_intake_persists_lead(session_factory: sessionmaker[Session]) -> None:
    service = IntakeService(session_factory)

    response = service.create_public_intake(
        PublicIntakeRequest(
            name="Maya Founder",
            email="MAYA@EXAMPLE.COM",
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
