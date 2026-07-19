from collections.abc import Iterator

import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
import app.models.board  # noqa: F401
import app.models.intake  # noqa: F401
import app.models.matter  # noqa: F401
import app.models.playbook  # noqa: F401
from app.schemas.boards import CreateThreadRequest, UpdateContextRequest
from app.services.board_service import BoardService

ORG = "org_test"
OTHER_ORG = "org_other"

FULL_CONTEXT = UpdateContextRequest(
    users_customers="120 paying customers",
    revenue_or_funding_stage="$8k MRR, pre-seed",
    customer_profile="Seed-stage B2B founders",
    team_size="3 (2 eng, 1 founder)",
    goals="Reach $25k MRR in 6 months",
    adviser_budget_per_hour="around $300/hr",
)


@pytest.fixture()
def service() -> Iterator[BoardService]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield BoardService(session_factory=factory)
    engine.dispose()


def test_thin_profile_stops_at_round1_with_follow_ups(service: BoardService) -> None:
    detail = service.create_thread(CreateThreadRequest(problem_text="How should I price my SaaS?"), ORG)
    assert detail.status == "context_pending"
    assert detail.context_sufficient is False
    round1 = next(b for b in detail.boards if b.round == 1)
    assert round1.verdict is not None
    assert len(round1.verdict.follow_up_questions) == 6
    # Rounds 2-3 must NOT run on a thin profile (roadmap §1 step 4).
    assert all(b.round == 1 for b in detail.boards)


def test_full_context_runs_all_rounds(service: BoardService) -> None:
    detail = service.create_thread(CreateThreadRequest(problem_text="How should I price my SaaS?"), ORG)
    detail = service.update_context(detail.id, FULL_CONTEXT, ORG)
    assert detail is not None
    assert detail.status == "agent_ready"
    rounds = sorted({b.round for b in detail.boards})
    assert rounds == [1, 2, 3]
    assert detail.domain == "pricing"


def test_round3_has_four_independent_positions_and_dissent(service: BoardService) -> None:
    service.update_context(
        service.create_thread(CreateThreadRequest(problem_text="warmup"), ORG).id, FULL_CONTEXT, ORG
    )
    detail = service.create_thread(
        CreateThreadRequest(problem_text="Should we raise a seed round or bootstrap?"), ORG
    )
    assert detail.domain == "fundraising"
    round3 = next(b for b in detail.boards if b.round == 3)
    assert len(round3.positions) == 4
    assert all(p.cross_examination for p in round3.positions)
    verdict = round3.verdict
    assert verdict is not None
    # Invariants 2 and 4: dissent preserved, assumptions named.
    assert verdict.dissent
    assert len(verdict.assumptions) >= 1
    assert verdict.validation_plan


def test_price_tier_never_exposed_on_free_path(service: BoardService) -> None:
    service.update_context(
        service.create_thread(CreateThreadRequest(problem_text="warmup"), ORG).id, FULL_CONTEXT, ORG
    )
    detail = service.create_thread(CreateThreadRequest(problem_text="Review my NDA please"), ORG)
    payload = detail.model_dump_json()
    assert "price_tier" not in payload
    assert "estimated_cost" not in payload


def test_context_profile_shared_across_threads(service: BoardService) -> None:
    first = service.create_thread(CreateThreadRequest(problem_text="How do I price this?"), ORG)
    service.update_context(first.id, FULL_CONTEXT, ORG)
    # Second thread skips straight past Round 1 (roadmap §1 step 8 / Phase 9).
    second = service.create_thread(CreateThreadRequest(problem_text="Fix my pitch deck narrative"), ORG)
    assert second.status == "agent_ready"
    assert second.domain == "pitch"


def test_tenant_isolation(service: BoardService) -> None:
    detail = service.create_thread(CreateThreadRequest(problem_text="Price my product"), ORG)
    assert service.get_thread(detail.id, OTHER_ORG) is None
    assert service.update_context(detail.id, FULL_CONTEXT, OTHER_ORG) is None
    assert service.post_message(detail.id, "hello", OTHER_ORG) is None


def test_perfect_agent_chat_replies(service: BoardService) -> None:
    detail = service.create_thread(CreateThreadRequest(problem_text="How should I price my SaaS?"), ORG)
    service.update_context(detail.id, FULL_CONTEXT, ORG)
    response = service.post_message(detail.id, "What should I test first?", ORG)
    assert response is not None
    assert response.reply.role == "agent"
    assert response.reply.content
    refreshed = service.get_thread(detail.id, ORG)
    assert refreshed is not None
    roles = [m.role for m in refreshed.messages]
    assert "founder" in roles and "agent" in roles


def test_adviser_quotes_ranked_and_capped(service: BoardService) -> None:
    detail = service.create_thread(CreateThreadRequest(problem_text="warmup"), ORG)
    service.update_context(detail.id, FULL_CONTEXT, ORG)
    priced = service.create_thread(CreateThreadRequest(problem_text="Review my NDA please"), ORG)
    quotes = service.adviser_quotes(priced.id, ORG)
    assert quotes is not None
    assert quotes.domain == "legal"
    assert 1 <= len(quotes.quotes) <= 3
    for quote in quotes.quotes:
        assert quote.platform_fee_pct == 10
        assert quote.not_to_exceed == quote.estimated_total  # invariant 8
        assert quote.metro == "San Francisco"


def test_adviser_quotes_require_routed_domain(service: BoardService) -> None:
    detail = service.create_thread(CreateThreadRequest(problem_text="Price my product"), ORG)
    # Thin profile -> no domain yet -> no quotes.
    assert service.adviser_quotes(detail.id, ORG) is None
