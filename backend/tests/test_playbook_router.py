from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.main import app
from app.services.auth import AuthContext, require_auth_context
from app.services.playbook_service import PlaybookService
import app.routers.playbooks as playbook_router


def test_attorney_can_author_playbook_checks(session_factory: sessionmaker[Session]) -> None:
    original_service = playbook_router.playbook_service
    playbook_router.playbook_service = PlaybookService(session_factory)

    def auth() -> AuthContext:
        return AuthContext(
            user_id="attorney_1",
            email="attorney@example.com",
            name="Reviewing Attorney",
            organisation_id="org_alpha",
            organisation_name="Alpha Co",
            role="attorney",
        )

    app.dependency_overrides[require_auth_context] = auth
    try:
        client = TestClient(app)
        created = client.post(
            "/v1/attorney/playbooks",
            json={"name": "Alpha NDA", "contract_type": "nda", "jurisdiction": "general"},
        )
        assert created.status_code == 200
        playbook = created.json()
        assert playbook["organisationId"] == "org_alpha"

        updated = client.post(
            f"/v1/attorney/playbooks/{playbook['id']}/checks",
            json={
                "key": "mutuality",
                "title": "Confirm mutuality",
                "detection": "Find whether obligations are mutual.",
                "severity": "medium",
                "remediation_intent": "Make obligations reciprocal unless one-way treatment is justified.",
                "preferred_language": "Both parties protect confidential information.",
                "acceptable_fallback": "One-way is acceptable only for a clear business reason.",
                "unacceptable_fallback": "Founder discloses sensitive information without reciprocal protection.",
            },
        )
        assert updated.status_code == 200
        assert updated.json()["checks"][0]["key"] == "mutuality"

        edited = client.patch(
            f"/v1/attorney/playbooks/checks/{updated.json()['checks'][0]['id']}",
            json={"severity": "high", "acceptable_fallback": "Escalate one-way NDAs unless the founder only receives data."},
        )
        assert edited.status_code == 200
        assert edited.json()["severity"] == "high"
    finally:
        app.dependency_overrides.clear()
        playbook_router.playbook_service = original_service
