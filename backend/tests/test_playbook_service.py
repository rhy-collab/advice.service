import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from app.schemas.playbook import PlaybookCheckCreate, PlaybookCreate
from app.services.playbook_service import PlaybookService


def test_playbook_crud_persists_structured_checks(session_factory: sessionmaker[Session]) -> None:
    service = PlaybookService(session_factory)

    playbook = service.create_playbook(
        PlaybookCreate(name="Vendor SaaS baseline", contract_type="vendor_saas", jurisdiction="general")
    )
    updated = service.add_check(
        playbook.id,
        PlaybookCheckCreate(
            key="liability_cap",
            title="Check liability cap",
            detection="Look for liability cap, exclusions, and super-cap wording.",
            severity="high",
            remediation_intent="Align cap with contract value and preserve key carve-outs.",
            preferred_language="Cap liability at fees paid in the prior 12 months with standard carve-outs.",
            acceptable_fallback="Cap liability at annual fees with confidentiality and IP carve-outs.",
            unacceptable_fallback="Unlimited customer liability while vendor liability is narrowly capped.",
        ),
    )

    fetched = service.get_playbook(playbook.id)

    assert updated.id == playbook.id
    assert fetched.contract_type == "vendor_saas"
    assert len(fetched.checks) == 1
    assert fetched.checks[0].key == "liability_cap"
    assert fetched.checks[0].severity == "high"
    assert fetched.checks[0].accuracy_total == 0


def test_playbook_list_filters_by_contract_type(session_factory: sessionmaker[Session]) -> None:
    service = PlaybookService(session_factory)
    service.create_playbook(PlaybookCreate(name="NDA", contract_type="nda"))
    service.create_playbook(PlaybookCreate(name="MSA", contract_type="msa"))

    results = service.list_playbooks(contract_type="nda")

    assert len(results) == 1
    assert results[0].contract_type == "nda"


def test_missing_playbook_returns_404(session_factory: sessionmaker[Session]) -> None:
    service = PlaybookService(session_factory)

    with pytest.raises(HTTPException) as exc_info:
        service.get_playbook("missing")

    assert exc_info.value.status_code == 404


def test_seed_nda_playbook_is_idempotent(session_factory: sessionmaker[Session]) -> None:
    service = PlaybookService(session_factory)

    first = service.seed_nda_playbook()
    second = service.seed_nda_playbook()

    assert first.id == second.id
    assert first.contract_type == "nda"
    assert first.checks[0].key == "mutuality"


def test_resolve_for_contract_prefers_organisation_overlay(session_factory: sessionmaker[Session]) -> None:
    service = PlaybookService(session_factory)
    base = service.create_playbook(PlaybookCreate(name="Base NDA", contract_type="nda"))
    overlay = service.create_playbook(
        PlaybookCreate(name="Client NDA", contract_type="nda", organisationId="org_alpha")
    )

    resolved = service.resolve_for_contract("nda", organisation_id="org_alpha")
    fallback = service.resolve_for_contract("nda", organisation_id="org_beta")

    assert resolved is not None
    assert resolved.id == overlay.id
    assert fallback is not None
    assert fallback.id == base.id
