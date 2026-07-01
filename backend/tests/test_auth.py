import pytest
from fastapi import HTTPException

from app.services.auth import require_auth_context


def test_demo_auth_allows_local_requests_without_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLERK_DEMO_AUTH", "true")

    auth = require_auth_context(None)

    assert auth.organisation_id == "org_demo"


def test_missing_header_is_rejected_when_demo_auth_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLERK_DEMO_AUTH", "false")

    with pytest.raises(HTTPException) as exc_info:
        require_auth_context(None)

    assert exc_info.value.status_code == 401


def test_malformed_authorization_header_is_rejected() -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_auth_context("Token nope")

    assert exc_info.value.status_code == 401


def _ctx(role: str):
    from app.services.auth import AuthContext

    return AuthContext(
        user_id="u",
        email="e@example.com",
        name="n",
        organisation_id="org_demo",
        organisation_name="Acme",
        role=role,
    )


def test_require_attorney_context_rejects_non_attorney() -> None:
    from app.services.auth import require_attorney_context

    with pytest.raises(HTTPException) as exc_info:
        require_attorney_context(_ctx("member"))

    assert exc_info.value.status_code == 403


def test_require_attorney_context_allows_attorney() -> None:
    from app.services.auth import require_attorney_context

    assert require_attorney_context(_ctx("attorney")).role == "attorney"
