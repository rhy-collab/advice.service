"""Board orchestration — Rounds 1-3 plus the Stage 4 perfect agent.

Implements charter-consultancy-roadmap.md §1 (user flow), §3 items 1-3 and 6, and the
§5 invariants that apply at this layer:

- Round 1: context-sufficiency check against the founder context profile.
- Round 2: problem definition & triage to one of the fixed seven domains.
- Round 3: four opposed-priors advisors draft *independent* positions (invariant 3),
  cross-examine once, then a Chair rules preserving dissent (invariant 2) and naming
  assumptions with a validation plan (invariant 4). The verdict also carries the
  internal price_tier / estimated_cost / real_hours_estimate (§6) which is never
  exposed through the free-path API (invariant 7).
- Stage 4: a perfect agent synthesized from the panel, free and unlimited
  (invariant 6), plus adviser matching (hours x self-set hourly rate, 10% platform
  fee, ranked top ~3) behind the explicit "match me" request.

Uses Anthropic when ANTHROPIC_API_KEY is set (same client pattern as
ai_prep_service); otherwise falls back to deterministic content so local demo mode
works end to end — mirroring the existing AI prep service's stub discipline.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import SessionLocal
from app.models.board import (
    DOMAINS,
    AdviserModel,
    AdvisorPositionModel,
    BoardModel,
    FounderContextProfileModel,
    ProblemThreadModel,
    ThreadMessageModel,
    VerdictModel,
)
from app.schemas.boards import (
    AdviserQuote,
    AdviserQuotesResponse,
    AdvisorPosition,
    BoardView,
    ContextProfile,
    CreateThreadRequest,
    PostMessageResponse,
    ThreadDetail,
    ThreadListResponse,
    ThreadMessage,
    ThreadSummary,
    UpdateContextRequest,
    Verdict,
)
from urllib import request as _urllib_request
import json as _json

from app.services.ai_prep_service import AnthropicMessageClient


class BoardAnthropicClient(AnthropicMessageClient):
    """Same wire format, longer timeout — board calls digest whole debates."""

    def create_message(self, payload: dict) -> dict:
        api_key = os.environ["ANTHROPIC_API_KEY"]
        base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        req = _urllib_request.Request(
            f"{base_url.rstrip('/')}/v1/messages",
            data=_json.dumps(payload).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01"),
            },
            method="POST",
        )
        with _urllib_request.urlopen(req, timeout=120) as response:
            return _json.loads(response.read().decode("utf-8"))

PLATFORM_FEE_PCT = 10

DOMAIN_LABELS: dict[str, str] = {
    "pricing": "Pricing strategy",
    "fundraising": "Fundraising",
    "gtm": "Go-to-market",
    "pitch": "Pitch & messaging",
    "legal": "Legal & compliance",
    "ecosystem": "Resources & location",
    "engineering": "Developer / engineering",
}

# Four genuinely opposed lenses per domain (roadmap §1 step 6).
DOMAIN_PANELS: dict[str, list[tuple[str, str]]] = {
    "pricing": [
        ("Maya Chen — Value Pricer", "Ex-Stripe monetisation lead. Price against the economic value created for the customer, never against cost or competitors."),
        ("Danny Kovacs — PLG Advocate", "Growth operator from two product-led rockets. Price low or free to maximise adoption; monetise expansion, not entry."),
        ("Ingrid Halvorsen — Unit-Economics Hawk", "Former CFO. No price is right if contribution margin is negative; model CAC payback before anything else."),
        ("Ed Barrera — Enterprise Deal-Maker", "20 years of six-figure contracts. Fewer, bigger deals; price high and negotiate — discounts buy commitment, not adoption."),
    ],
    "fundraising": [
        ("Ben Okoye — Bootstrapper", "Built to $10M ARR with no outside money. Raising is a last resort; revenue is cheaper than equity and disciplines the product."),
        ("Vic Tanaka — Venture Maximalist", "Ex-VC partner. In a winner-take-most market, under-raising is the biggest risk; speed beats dilution math."),
        ("Ana Petrov — Angel-Round Pragmatist", "Operator-angel with 40 checks written. Small round from operators who open doors; keep optionality for the next 18 months."),
        ("Rory Feldman — Revenue-First Operator", "Three-time founder. Fund the raise with traction: close three more customers before any partner meeting."),
    ],
    "gtm": [
        ("Poppy Lindqvist — PLG Strategist", "Scaled activation at two devtools startups. The product is the funnel; instrument activation and let usage sell."),
        ("Sal Moreno — Enterprise Sales Lead", "Carried a bag for a decade. High-ACV problems are sold, not signed up for; founder-led sales until repeatable."),
        ("Cass Wright — Community Builder", "Grew a 100k-member developer community. Trust compounds; build the audience the product sells into before scaling spend."),
        ("Pete Aldana — Paid-Acquisition Skeptic", "Performance marketer turned apostate. Paid channels flatter early metrics and hide weak retention; earn organic proof first."),
    ],
    "pitch": [
        ("Nadia Rahman — Narrative Purist", "Speechwriter turned pitch coach. Investors buy a story about inevitability; the deck is theatre for one idea."),
        ("Mick Delaney — Metrics-First Realist", "Ex-growth VC. Traction slides raise rounds; strip adjectives, show the graph."),
        ("Dee Chow — Design Minimalist", "Brand designer for 30+ seed decks. Ten slides, one point each; anything the eye can't parse in three seconds goes."),
        ("Ivy Sorensen — Investor-Psychology Reader", "Former fund CoS. Pitch to the partner meeting you're not in; arm your champion with ammunition."),
    ],
    "legal": [
        ("Ruth Calloway — Risk-Averse Counsel", "25 years of startup wreckage seen. Cap liability, protect IP, assume the relationship sours; paper for the divorce."),
        ("Dev Malik — Deal-Velocity Pragmatist", "Ex-BigLaw, allergic to overlawyering. The best contract is the one that closes this week; negotiate the two terms that matter."),
        ("Fay Ibarra — Founder-Protection Advocate", "Represents founders only. Founders sign away leverage early; vesting, IP assignment and control terms first."),
        ("Cole Whitfield — Compliance Hawk", "Privacy and employment specialist. Data, privacy and employment rules bite later; the cheap fix is now."),
    ],
    "ecosystem": [
        ("Sofia Marsh — SF Maximalist", "Two exits, both built in SoMa. Talent density and capital proximity compound; be where the market is."),
        ("Remy Okafor — Remote-First Advocate", "Built a 9-timezone team. Burn rate is strategy; hire the best person anywhere and bank the difference."),
        ("Cara Bly — Capital-Efficiency Regionalist", "Runway mathematician. Second cities give runway and loyalty; arbitrage cost of living."),
        ("Tal Vardi — Talent-Density Analyst", "Labour-market researcher. Go where your specific talent pool is, not where startups in general are."),
    ],
    "engineering": [
        ("Shay Donnelly — Ship-It Advocate", "CTO of three pre-PMF startups. Speed of iteration is the only moat pre-product-market-fit; duct tape is a feature."),
        ("Skye Ambrose — Scalability Hawk", "Lived through two rewrite deaths. Rewrites kill startups; the shortcuts you take now are the outages you debug later."),
        ("Bo Lindgren — Buy-Don't-Build Pragmatist", "Integration-first architect. Every line of code is a liability; integrate before you author."),
        ("Selin Acar — Security & Compliance Lens", "Security engineer for early B2B. One breach ends an early company; auth, secrets and data handling are not later problems."),
    ],
}

CHAIR_NAME = "Eleanor Voss — Chair of the Board"

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "pricing": ["pricing", "price", "charge", "subscription", "monetis", "monetiz", "plan tier"],
    "fundraising": ["raise", "fundrais", "investor", "seed", "series a", "valuation", "term sheet", "safe", "equity", "dilution", "cofounder", "co-founder"],
    "gtm": ["go-to-market", "gtm", "marketing", "channel", "growth", "acquisition", "launch", "customers", "sales"],
    "pitch": ["pitch", "deck", "slide", "narrative", "messaging", "story"],
    "legal": ["contract", "nda", "legal", "terms", "agreement", "lawyer", "compliance", "privacy", "gdpr", "incorporat", "trademark", "ip "],
    "ecosystem": ["relocat", "location", "city", "san francisco", "remote", "office", "visa", "where to build", "hub"],
    "engineering": ["build vs buy", "architecture", "tech stack", "hire engineer", "developer", "technical", "backend", "frontend", "infra", "database", "scale the system"],
}

PRICE_TIER_TABLE = {
    "simple": (250, "0.5–1"),
    "standard": (500, "1–2"),
    "negotiation": (1000, "3–5"),
    "drafting": (2000, "5–8"),
}


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _post(db: Session, thread: ProblemThreadModel, role: str, content: str) -> None:
    """Append a conversational message to the thread. role: founder | agent | board | chair | advisor:<Name>."""
    db.add(ThreadMessageModel(thread_id=thread.id, role=role, content=content))
    db.flush()


class BoardService:
    def __init__(
        self,
        session_factory: Callable[[], Session] | sessionmaker[Session] = SessionLocal,
        anthropic_client: AnthropicMessageClient | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._anthropic_client = anthropic_client or BoardAnthropicClient()

    # ------------------------------------------------------------------ threads

    def create_thread(self, request: CreateThreadRequest, organisation_id: str) -> ThreadDetail:
        problem = request.problem_text.strip()
        title = problem if len(problem) <= 64 else problem[:64] + "…"
        with self._session_factory() as db:
            thread = ProblemThreadModel(
                id=_new_id("thread"),
                organisation_id=organisation_id,
                title=title,
                problem_text=problem,
                status="context_pending",
            )
            db.add(thread)
            profile = self._get_or_create_profile(db, organisation_id)
            self._run_round1(db, thread, profile)
            if thread.status != "context_pending":
                self._run_round2(db, thread, profile)
                self._run_round3(db, thread, profile)
            db.commit()
            return self._thread_detail(db, thread.id, organisation_id)

    def list_threads(self, organisation_id: str) -> ThreadListResponse:
        with self._session_factory() as db:
            rows = db.execute(
                select(ProblemThreadModel)
                .where(ProblemThreadModel.organisation_id == organisation_id)
                .order_by(ProblemThreadModel.created_at.desc())
            ).scalars()
            return ThreadListResponse(
                threads=[
                    ThreadSummary(
                        id=t.id,
                        title=t.title,
                        status=t.status,
                        domain=t.domain,
                        created_at=t.created_at.isoformat() if t.created_at else "",
                    )
                    for t in rows
                ]
            )

    def get_thread(self, thread_id: str, organisation_id: str) -> ThreadDetail | None:
        with self._session_factory() as db:
            thread = self._get_thread(db, thread_id, organisation_id)
            if thread is None:
                return None
            return self._thread_detail(db, thread_id, organisation_id)

    def update_context(
        self, thread_id: str, request: UpdateContextRequest, organisation_id: str
    ) -> ThreadDetail | None:
        with self._session_factory() as db:
            thread = self._get_thread(db, thread_id, organisation_id)
            if thread is None:
                return None
            profile = self._get_or_create_profile(db, organisation_id)
            for field, value in request.model_dump().items():
                if value and value.strip():
                    setattr(profile, field, value.strip())
            # Re-run the sufficiency check; if satisfied, continue to Rounds 2-3.
            self._run_round1(db, thread, profile, rerun=True)
            if thread.status != "context_pending" and thread.domain is None:
                self._run_round2(db, thread, profile)
                self._run_round3(db, thread, profile)
            db.commit()
            return self._thread_detail(db, thread_id, organisation_id)

    # -------------------------------------------------------------- stage 4 chat

    def post_message(
        self, thread_id: str, content: str, organisation_id: str
    ) -> PostMessageResponse | None:
        with self._session_factory() as db:
            thread = self._get_thread(db, thread_id, organisation_id)
            if thread is None:
                return None
            _post(db, thread, "founder", content)

            if thread.status == "context_pending":
                # Conversational Round 1: treat the founder's message as context answers.
                profile = self._get_or_create_profile(db, thread.organisation_id)
                self._absorb_context_message(db, profile, content)
                self._run_round1(db, thread, profile, rerun=True)
                if thread.status != "context_pending" and thread.domain is None:
                    self._run_round2(db, thread, profile)
                    self._run_round3(db, thread, profile)
                reply = thread.messages[-1] if thread.messages else None
                db.commit()
                return PostMessageResponse(
                    reply=ThreadMessage(
                        role=reply.role if reply else "board",
                        content=reply.content if reply else "",
                        created_at=reply.created_at.isoformat() if reply and reply.created_at else "",
                    )
                )

            reply_text = self._perfect_agent_reply(db, thread, content)
            reply = ThreadMessageModel(thread_id=thread.id, role="agent", content=reply_text)
            db.add(reply)
            db.commit()
            db.refresh(reply)
            return PostMessageResponse(
                reply=ThreadMessage(
                    role="agent",
                    content=reply_text,
                    created_at=reply.created_at.isoformat() if reply.created_at else "",
                )
            )

    def _absorb_context_message(
        self, db: Session, profile: FounderContextProfileModel, message: str
    ) -> None:
        """Map a free-text founder message onto the context profile fields."""
        fields = (
            "users_customers",
            "revenue_or_funding_stage",
            "customer_profile",
            "team_size",
            "goals",
        )
        if os.getenv("ANTHROPIC_API_KEY"):
            out = self._claude(
                "Extract founder business context from the message. Reply ONLY with JSON using any of "
                "these keys (omit keys the message says nothing about): users_customers, "
                "revenue_or_funding_stage, customer_profile, team_size, goals. Values are short strings "
                "quoting the founder's own facts.",
                message,
                max_tokens=300,
            )
            if out:
                try:
                    data = json.loads(out[out.index("{") : out.rindex("}") + 1])
                    for key in fields:
                        value = data.get(key)
                        if value and str(value).strip():
                            setattr(profile, key, str(value).strip())
                    db.flush()
                    return
                except Exception:
                    pass
        # Deterministic fallback: fill every still-missing field with the founder's words.
        for key in fields:
            if not (getattr(profile, key) or "").strip():
                setattr(profile, key, message.strip())
        db.flush()

    # ------------------------------------------------------- adviser matching

    def adviser_quotes(self, thread_id: str, organisation_id: str) -> AdviserQuotesResponse | None:
        """The one paid moment: only runs when the founder explicitly asks (invariant 7)."""
        with self._session_factory() as db:
            thread = self._get_thread(db, thread_id, organisation_id)
            if thread is None or thread.domain is None:
                return None
            verdict = self._round3_verdict(db, thread)
            tier = (verdict.price_tier if verdict else None) or "standard"
            budget, hours = PRICE_TIER_TABLE.get(tier, PRICE_TIER_TABLE["standard"])
            hours_hi = float(hours.split("–")[-1])

            if os.getenv("ANTHROPIC_API_KEY"):
                profile = self._get_or_create_profile(db, thread.organisation_id)
                generated = self._claude_adviser_matches(thread, profile, verdict, hours, hours_hi)
                if generated:
                    return AdviserQuotesResponse(domain=thread.domain, quotes=generated)
            self._seed_advisers_if_empty(db)
            advisers = db.execute(
                select(AdviserModel).where(AdviserModel.domain == thread.domain)
            ).scalars().all()
            quotes: list[AdviserQuote] = []
            for adviser in advisers:
                base = int(adviser.hourly_rate * hours_hi)
                total = int(base * (100 + PLATFORM_FEE_PCT) / 100)
                quotes.append(
                    AdviserQuote(
                        adviser_id=adviser.id,
                        name=adviser.name,
                        metro=adviser.metro,
                        hourly_rate=adviser.hourly_rate,
                        skills_profile=adviser.skills_profile,
                        estimated_hours=hours,
                        estimated_total=total,
                        platform_fee_pct=PLATFORM_FEE_PCT,
                        not_to_exceed=total,
                    )
                )
            # Filter to the budget band where possible, rank by fit (closest under budget first).
            in_band = [q for q in quotes if q.estimated_total <= budget * 2]
            ranked = sorted(in_band or quotes, key=lambda q: abs(q.estimated_total - budget))
            return AdviserQuotesResponse(domain=thread.domain, quotes=ranked[:3])

    # ------------------------------------------------------------------ round 1

    def _run_round1(
        self,
        db: Session,
        thread: ProblemThreadModel,
        profile: FounderContextProfileModel,
        rerun: bool = False,
    ) -> None:
        context = self._profile_schema(profile)
        missing = context.missing_fields()
        sufficient = len(missing) == 0
        board = BoardModel(id=_new_id("board"), thread_id=thread.id, round=1, status="complete")
        db.add(board)
        db.flush()
        for name, persona in (
            ("Completeness Check", "Argues the profile is thin until every basic is grounded."),
            ("Momentum Check", "Argues for proceeding once the material facts are in; perfect context is procrastination."),
        ):
            db.add(
                AdvisorPositionModel(
                    board_id=board.id,
                    advisor_name=name,
                    persona=persona,
                    position=self._round1_position(name, context, missing),
                )
            )
        if sufficient:
            ruling = (
                "The board is satisfied it understands this startup well enough to reason about it "
                "responsibly. Proceeding to problem definition and triage."
            )
            questions: list[str] = []
            thread.status = "triage"
            _post(
                db,
                thread,
                f"chair:{CHAIR_NAME}",
                "Round 1 — Context. We already hold your business-context profile ("
                + self._context_line(profile)
                + "), so the board is satisfied it understands your startup. Moving straight to triage.",
            )
        else:
            ruling = (
                "The board is not yet satisfied it fully understands this startup — proceeding on a "
                "thin profile would produce generic advice. Targeted follow-ups below."
            )
            questions = [f"Tell us {m}." for m in missing]
            thread.status = "context_pending"
            _post(
                db,
                thread,
                f"chair:{CHAIR_NAME}",
                "Round 1 — Context. Before we debate anything, we need to actually understand your "
                "startup — answering on a thin profile would be guesswork dressed as analysis. "
                "Tell us, right here in the chat: " + "; ".join(missing) + ". "
                "One message covering whatever you know is fine — we'll ask again if anything's missing.",
            )
        db.add(
            VerdictModel(
                board_id=board.id,
                ruling=ruling,
                assumptions_json="[]",
                follow_up_questions_json=json.dumps(questions),
            )
        )
        db.flush()

    @staticmethod
    def _round1_position(name: str, context: ContextProfile, missing: list[str]) -> str:
        known = {k: v for k, v in context.model_dump().items() if v}
        if name == "Completeness Check":
            if missing:
                return (
                    "We do not fully understand this startup yet. Missing: " + "; ".join(missing) + ". "
                    "Routing or advising on this would be guesswork dressed as analysis."
                )
            return "Every basic is grounded: " + "; ".join(f"{k}: {v}" for k, v in known.items()) + "."
        if missing:
            return (
                "Enough is known to begin, but the gaps named opposite are real — collect them before "
                "Round 3 stakes positions on them."
            )
        return "Context is sufficient and current; further questioning is stalling, not diligence."

    # ------------------------------------------------------------------ round 2

    def _run_round2(
        self, db: Session, thread: ProblemThreadModel, profile: FounderContextProfileModel
    ) -> None:
        domain = self._route_domain(thread.problem_text, profile)
        board = BoardModel(id=_new_id("board"), thread_id=thread.id, round=2, domain=domain, status="complete")
        db.add(board)
        db.flush()
        db.add(
            AdvisorPositionModel(
                board_id=board.id,
                advisor_name="Triage Board",
                persona="Sharpens the problem statement and routes it to the single domain that owns it.",
                position=self._round2_reasoning(thread.problem_text, domain),
            )
        )
        db.add(
            VerdictModel(
                board_id=board.id,
                ruling=(
                    f"Problem routed to {DOMAIN_LABELS[domain]} — the single domain that owns it, "
                    "from the fixed menu of seven. Round 3 convenes that domain's panel."
                ),
                assumptions_json=json.dumps(
                    ["If the sharpened problem statement misses the founder's real concern, re-route before Round 3."]
                ),
                follow_up_questions_json="[]",
            )
        )
        thread.domain = domain
        thread.status = "panel"
        _post(
            db,
            thread,
            f"chair:{CHAIR_NAME}",
            "Round 2 — Problem definition & triage. "
            + self._round2_reasoning(thread.problem_text, domain)
            + f" Routed to: {DOMAIN_LABELS[domain]}. If that framing misses what you're actually "
            "worried about, say so and we'll re-route before the panel convenes.",
        )
        db.flush()

    def _route_domain(self, problem_text: str, profile: FounderContextProfileModel) -> str:
        if os.getenv("ANTHROPIC_API_KEY"):
            routed = self._claude_route(problem_text, profile)
            if routed in DOMAINS:
                return routed
        text = problem_text.lower()
        scores = {
            domain: sum(1 for kw in keywords if kw in text)
            for domain, keywords in DOMAIN_KEYWORDS.items()
        }
        best = max(scores, key=lambda d: scores[d])
        return best if scores[best] > 0 else "gtm"

    @staticmethod
    def _round2_reasoning(problem_text: str, domain: str) -> str:
        return (
            f"Raw problem as stated: “{problem_text}”. Sharpened: this is fundamentally a "
            f"{DOMAIN_LABELS[domain].lower()} question — the other six domains touch it but do not own it. "
            "Routing is made visibly here rather than by a silent classifier so it can be challenged."
        )

    # ------------------------------------------------------------------ round 3

    def _run_round3(
        self, db: Session, thread: ProblemThreadModel, profile: FounderContextProfileModel
    ) -> None:
        domain = thread.domain or "gtm"
        panel = DOMAIN_PANELS[domain]
        board = BoardModel(id=_new_id("board"), thread_id=thread.id, round=3, domain=domain, status="complete")
        db.add(board)
        db.flush()

        _post(
            db,
            thread,
            f"chair:{CHAIR_NAME}",
            f"Round 3 — Domain board. Convening your {DOMAIN_LABELS[domain]} panel: "
            + ", ".join(name for name, _ in panel)
            + ". Each drafts an independent position first — none of them sees the others' work "
            "until cross-examination.",
        )

        # Independent first drafts (invariant 3): each position is produced without
        # sight of any other advisor's output.
        positions = self._independent_positions(thread, profile, panel)
        rows: list[AdvisorPositionModel] = []
        for (name, persona), position in zip(panel, positions):
            row = AdvisorPositionModel(
                board_id=board.id, advisor_name=name, persona=persona, position=position
            )
            db.add(row)
            rows.append(row)
            _post(db, thread, f"advisor:{name}", position)
        db.flush()

        _post(db, thread, f"chair:{CHAIR_NAME}", "Positions are in. One round of cross-examination — attack the weakest rival, concede what's stronger.")

        # One round of cross-examination — now (and only now) each sees the others.
        for i, row in enumerate(rows):
            others = [(r.advisor_name, r.position) for j, r in enumerate(rows) if j != i]
            row.cross_examination = self._cross_examination(row.advisor_name, row.position, others)
            _post(db, thread, f"advisor:{row.advisor_name}", row.cross_examination)

        tier = self._price_tier(thread.problem_text)
        cost, hours = PRICE_TIER_TABLE[tier]
        chair = self._chair_verdict(thread, profile, rows)
        db.add(
            VerdictModel(
                board_id=board.id,
                ruling=chair["ruling"],
                assumptions_json=json.dumps(chair["assumptions"]),
                dissent=chair["dissent"],
                validation_plan=chair["validation_plan"],
                follow_up_questions_json="[]",
                price_tier=tier,
                estimated_cost=cost,
                real_hours_estimate=hours,
            )
        )
        thread.status = "agent_ready"
        _post(
            db,
            thread,
            f"chair:{CHAIR_NAME}",
            chair["ruling"]
            + "\n\nAssumptions this stands on: "
            + " ".join(f"({i + 1}) {a}" for i, a in enumerate(chair["assumptions"]))
            + (f"\n\nPreserved dissent: {chair['dissent']}" if chair.get("dissent") else "")
            + (f"\n\nValidation plan: {chair['validation_plan']}" if chair.get("validation_plan") else ""),
        )
        _post(
            db,
            thread,
            "agent",
            "Your panel has ruled. I’m the advisor synthesized from its debate — ask me anything "
            "about the verdict, the dissent, or what to test first. This conversation is free and unlimited.",
        )
        db.flush()

    def _independent_positions(
        self,
        thread: ProblemThreadModel,
        profile: FounderContextProfileModel,
        panel: list[tuple[str, str]],
    ) -> list[str]:
        if os.getenv("ANTHROPIC_API_KEY"):
            with ThreadPoolExecutor(max_workers=len(panel)) as pool:
                futures = [
                    pool.submit(self._claude_position, thread, profile, name, persona)
                    for name, persona in panel
                ]
                return [f.result() for f in futures]
        context_line = self._context_line(profile)
        return [
            (
                f"Through the {name} lens — {persona} Applied to “{thread.problem_text}” "
                f"given {context_line}: my independent position is that the founder should act on this "
                f"priority first, and I will defend that against the rest of the panel."
            )
            for name, persona in panel
        ]

    def _cross_examination(
        self, name: str, position: str, others: list[tuple[str, str]]
    ) -> str:
        if os.getenv("ANTHROPIC_API_KEY"):
            return self._claude_cross_exam(name, position, others)
        rivals = ", ".join(other_name for other_name, _ in others)
        return (
            f"Against {rivals}: I hold my position. The strongest objection raised is real but priced in; "
            "where my prior fails, the conditions in the Chair's assumptions table say so explicitly."
        )

    def _chair_verdict(
        self,
        thread: ProblemThreadModel,
        profile: FounderContextProfileModel,
        rows: list[AdvisorPositionModel],
    ) -> dict:
        if os.getenv("ANTHROPIC_API_KEY"):
            verdict = self._claude_chair(thread, profile, rows)
            if verdict is not None:
                return verdict
        names = [r.advisor_name for r in rows]
        return {
            "ruling": (
                f"The Chair rules with the majority ({', '.join(names[:3])}): treat "
                f"“{thread.problem_text}” as the immediate priority and act on the panel's "
                "consensus direction this week rather than waiting for more information."
            ),
            "assumptions": [
                "If the founder's stated context is current, act on the ruling as written.",
                "If the key metric behind it moves >20% this month, re-convene the panel before acting.",
            ],
            "dissent": (
                f"{names[-1]} dissents and is preserved in full above: the majority is underweighting "
                "the risk named in that position. The dissent is part of the verdict, not a footnote."
            ),
            "validation_plan": (
                "Test the ruling within two weeks: pick the single cheapest experiment that would prove "
                "the majority wrong, run it, and bring the result back to this thread."
            ),
        }

    # ------------------------------------------------------------- perfect agent

    def _perfect_agent_reply(
        self, db: Session, thread: ProblemThreadModel, founder_message: str
    ) -> str:
        if thread.status != "agent_ready":
            missing = self._profile_schema(
                self._get_or_create_profile(db, thread.organisation_id)
            ).missing_fields()
            if missing:
                return (
                    "Before the panel convenes I still need: " + "; ".join(missing) + ". "
                    "Answer in the context form and Rounds 2–3 will run immediately."
                )
        if os.getenv("ANTHROPIC_API_KEY"):
            reply = self._claude_agent_reply(db, thread, founder_message)
            if reply:
                return reply
        verdict = self._round3_verdict(db, thread)
        ruling = verdict.ruling if verdict else "the panel's ruling"
        return (
            f"Grounded in your panel's verdict — {ruling} — here’s my read on "
            f"“{founder_message}”: start from the ruling, check it against the assumptions table, "
            "and if your situation matches the dissent's conditions, weigh that minority view seriously. "
            "Want a real human on this? Open the Adviser tab and I’ll show you matched individuals."
        )

    # ----------------------------------------------------------------- claude

    _resolved_model: str | None = None

    def _claude(self, system: str, user: str, max_tokens: int = 700) -> str | None:
        env_model = os.getenv("ANTHROPIC_MODEL", "").strip()
        candidates = [m for m in (
            self._resolved_model,
            env_model or None,
            "claude-sonnet-4-5",
            "claude-sonnet-4-20250514",
            "claude-3-7-sonnet-latest",
            "claude-3-5-sonnet-latest",
        ) if m]
        seen: set[str] = set()
        for model in candidates:
            if model in seen:
                continue
            seen.add(model)
            try:
                response = self._anthropic_client.create_message(
                    {
                        "model": model,
                        "max_tokens": max_tokens,
                        "system": system,
                        "messages": [{"role": "user", "content": user}],
                    }
                )
                text = "".join(
                    p.get("text", "") for p in response.get("content", []) if p.get("type") == "text"
                ).strip()
                if text:
                    self._resolved_model = model
                    return text
            except Exception as exc:  # log to stdout so serverless logs show the real failure
                detail = ""
                body = getattr(exc, "read", None)
                if callable(body):
                    try:
                        detail = body().decode("utf-8", "replace")[:300]
                    except Exception:
                        detail = ""
                print(f"[board_service] anthropic call failed model={model}: {exc} {detail}", flush=True)
        return None

    def _claude_route(self, problem_text: str, profile: FounderContextProfileModel) -> str | None:
        out = self._claude(
            "You are the triage board for a founder-advisory service. Route the problem to exactly one "
            "domain from this list and reply with only that token: "
            + ", ".join(DOMAINS),
            f"Problem: {problem_text}\nContext: {self._context_line(profile)}",
            max_tokens=10,
        )
        return out.strip().lower() if out else None

    def _claude_position(
        self, thread: ProblemThreadModel, profile: FounderContextProfileModel, name: str, persona: str
    ) -> str:
        out = self._claude(
            f"You are '{name}', one advisor on a four-person board with genuinely opposed priors. "
            f"Your fixed lens: {persona} Draft your independent position (150 words max) on the founder's "
            "problem. You have NOT seen any other advisor's position. Be concrete and evidence-minded; "
            "stake a real claim your lens demands, even if other lenses would disagree. "
            "Write plain conversational prose — no markdown, no headings, no bullet lists.",
            f"Problem: {thread.problem_text}\nFounder context: {self._context_line(profile)}",
        )
        return out or f"[{name}] position unavailable — model call failed; deterministic fallback applies."

    def _claude_cross_exam(self, name: str, position: str, others: list[tuple[str, str]]) -> str:
        rivals = "\n".join(f"- {other_name}: {other_position}" for other_name, other_position in others)
        out = self._claude(
            f"You are '{name}'. This is the single cross-examination round. In 80 words max: attack the "
            "weakest rival position, concede anything genuinely stronger than your own, and state whether "
            "you hold or amend your position. Plain conversational prose — no markdown formatting.",
            f"Your position: {position}\nRivals:\n{rivals}",
            max_tokens=300,
        )
        return out or "Cross-examination unavailable."

    def _claude_chair(
        self, thread: ProblemThreadModel, profile: FounderContextProfileModel, rows: list[AdvisorPositionModel]
    ) -> dict | None:
        debate = "\n\n".join(
            f"{r.advisor_name}:\nPosition: {r.position}\nCross-exam: {r.cross_examination}" for r in rows
        )
        out = self._claude(
            "You are the Chair of an advisory board. Rule on the debate. Reply as JSON with keys: "
            "ruling (string), assumptions (array of 'if X holds, do A; if it fails, do B' strings, min 1), "
            "dissent (string naming the strongest minority position — never smooth it away), "
            "validation_plan (string with a concrete cheap test). No other keys, no prose outside JSON.",
            f"Problem: {thread.problem_text}\nContext: {self._context_line(profile)}\n\nDebate:\n{debate}",
            max_tokens=800,
        )
        if not out:
            return None
        try:
            data = json.loads(out[out.index("{") : out.rindex("}") + 1])
            return {
                "ruling": str(data["ruling"]),
                "assumptions": [str(a) for a in data.get("assumptions", [])],
                "dissent": str(data.get("dissent") or ""),
                "validation_plan": str(data.get("validation_plan") or ""),
            }
        except Exception:
            return None

    def _claude_adviser_matches(
        self,
        thread: ProblemThreadModel,
        profile: FounderContextProfileModel,
        verdict: VerdictModel | None,
        hours: str,
        hours_hi: float,
    ) -> list[AdviserQuote] | None:
        """Generate ~10 matched adviser profiles for this exact problem (demo marketplace).

        Profiles are AI-generated placeholders standing in for the real recruited
        San Francisco adviser pool described in the roadmap (§3 item 6).
        """
        ruling = verdict.ruling if verdict else "(no verdict yet)"
        out = self._claude(
            "You generate a marketplace shortlist of expert advisers for a founder-advisory product. "
            "Create exactly 10 fictional but deeply credible individual advisers perfectly matched to "
            "the founder's specific problem, context, and their board's verdict. They must read as "
            "genuinely impressive domain experts (named operators, ex-companies, concrete track "
            "records) — no titled roles like 'Legal Lead', just real-sounding people. Vary seniority "
            "and hourly rates ($150–$500). Reply ONLY with a JSON array of 10 objects with keys: "
            "name, title (their real-world credential line, e.g. 'ex-Stripe pricing lead'), "
            "hourly_rate (integer), why_fit (ONE sentence, second person, referencing the founder's "
            "actual problem and numbers — why this specific person is the right match). No markdown.",
            f"Problem: {thread.problem_text}\nFounder context: {self._context_line(profile)}\n"
            f"Board verdict: {ruling[:600]}",
            max_tokens=1800,
        )
        if not out:
            return None
        try:
            data = json.loads(out[out.index("[") : out.rindex("]") + 1])
            quotes: list[AdviserQuote] = []
            for item in data[:10]:
                rate = int(item.get("hourly_rate") or 250)
                total = int(rate * hours_hi * (100 + PLATFORM_FEE_PCT) / 100)
                quotes.append(
                    AdviserQuote(
                        adviser_id=_new_id("adviser"),
                        name=str(item.get("name") or "Adviser"),
                        title=str(item.get("title") or ""),
                        metro="San Francisco",
                        hourly_rate=rate,
                        skills_profile=str(item.get("title") or ""),
                        why_fit=str(item.get("why_fit") or ""),
                        estimated_hours=hours,
                        estimated_total=total,
                        platform_fee_pct=PLATFORM_FEE_PCT,
                        not_to_exceed=total,
                    )
                )
            return quotes if len(quotes) >= 5 else None
        except Exception:
            return None

    def _claude_agent_reply(
        self, db: Session, thread: ProblemThreadModel, founder_message: str
    ) -> str | None:
        verdict = self._round3_verdict(db, thread)
        verdict_text = verdict.ruling if verdict else "(no verdict yet)"
        dissent = (verdict.dissent or "") if verdict else ""
        return self._claude(
            "You are the 'perfect agent' — a single advisor synthesized from a four-person opposed-priors "
            "panel. Answer the founder's question grounded in the panel's verdict and preserved dissent. "
            "Plain conversational prose — no markdown. "
            "Never mention prices, paywalls, or usage limits: this chat is free and unlimited. If they ask "
            "for a human, point them to the Adviser tab. 180 words max.",
            f"Problem: {thread.problem_text}\nVerdict: {verdict_text}\nDissent: {dissent}\n"
            f"Founder asks: {founder_message}",
        )

    # ----------------------------------------------------------------- helpers

    @staticmethod
    def _price_tier(problem_text: str) -> str:
        """Reactive-vs-originative x bounded-vs-open-ended (roadmap §6)."""
        text = problem_text.lower()
        reactive = any(
            kw in text for kw in ("review", "look at", "check", "existing", "our current", "this contract", "my deck", "nda")
        )
        open_ended = any(
            kw in text for kw in ("negotiat", "ongoing", "strategy", "roadmap", "raise", "launch", "build")
        )
        if reactive and not open_ended:
            return "simple" if len(problem_text) < 120 else "standard"
        if reactive and open_ended:
            return "negotiation"
        return "standard" if not open_ended else "drafting"

    @staticmethod
    def _context_line(profile: FounderContextProfileModel) -> str:
        parts = [
            f"users/customers: {profile.users_customers or 'unknown'}",
            f"stage: {profile.revenue_or_funding_stage or 'unknown'}",
            f"customer: {profile.customer_profile or 'unknown'}",
            f"team: {profile.team_size or 'unknown'}",
            f"goals: {profile.goals or 'unknown'}",
        ]
        return "; ".join(parts)

    @staticmethod
    def _profile_schema(profile: FounderContextProfileModel) -> ContextProfile:
        return ContextProfile(
            users_customers=profile.users_customers,
            revenue_or_funding_stage=profile.revenue_or_funding_stage,
            customer_profile=profile.customer_profile,
            team_size=profile.team_size,
            goals=profile.goals,
        )

    def _get_or_create_profile(self, db: Session, organisation_id: str) -> FounderContextProfileModel:
        profile = db.execute(
            select(FounderContextProfileModel).where(
                FounderContextProfileModel.organisation_id == organisation_id
            )
        ).scalar_one_or_none()
        if profile is None:
            profile = FounderContextProfileModel(id=_new_id("profile"), organisation_id=organisation_id)
            db.add(profile)
            db.flush()
        return profile

    @staticmethod
    def _get_thread(db: Session, thread_id: str, organisation_id: str) -> ProblemThreadModel | None:
        return db.execute(
            select(ProblemThreadModel).where(
                ProblemThreadModel.id == thread_id,
                ProblemThreadModel.organisation_id == organisation_id,
            )
        ).scalar_one_or_none()

    @staticmethod
    def _round3_verdict(db: Session, thread: ProblemThreadModel) -> VerdictModel | None:
        board = db.execute(
            select(BoardModel).where(BoardModel.thread_id == thread.id, BoardModel.round == 3)
        ).scalar_one_or_none()
        return board.verdict if board else None

    def _thread_detail(self, db: Session, thread_id: str, organisation_id: str) -> ThreadDetail:
        thread = self._get_thread(db, thread_id, organisation_id)
        assert thread is not None
        profile = self._get_or_create_profile(db, organisation_id)
        context = self._profile_schema(profile)
        boards = []
        for board in thread.boards:
            verdict = None
            if board.verdict is not None:
                verdict = Verdict(
                    ruling=board.verdict.ruling,
                    assumptions=json.loads(board.verdict.assumptions_json or "[]"),
                    dissent=board.verdict.dissent,
                    validation_plan=board.verdict.validation_plan,
                    follow_up_questions=json.loads(board.verdict.follow_up_questions_json or "[]"),
                )
            boards.append(
                BoardView(
                    id=board.id,
                    round=board.round,
                    domain=board.domain,
                    status=board.status,
                    positions=[
                        AdvisorPosition(
                            advisor_name=p.advisor_name,
                            persona=p.persona,
                            position=p.position,
                            cross_examination=p.cross_examination,
                        )
                        for p in board.positions
                    ],
                    verdict=verdict,
                )
            )
        return ThreadDetail(
            id=thread.id,
            title=thread.title,
            problem_text=thread.problem_text,
            status=thread.status,
            domain=thread.domain,
            boards=boards,
            messages=[
                ThreadMessage(
                    role=m.role,
                    content=m.content,
                    created_at=m.created_at.isoformat() if m.created_at else "",
                )
                for m in thread.messages
            ],
            context_profile=context,
            context_sufficient=len(context.missing_fields()) == 0,
        )

    def _seed_advisers_if_empty(self, db: Session) -> None:
        existing = db.execute(select(AdviserModel).limit(1)).scalar_one_or_none()
        if existing is not None:
            return
        seed: list[tuple[str, str, int, str]] = [
            ("Maya Chen", "pricing", 275, "Priced three PLG products through their first sales-assist motion; ex-Stripe monetisation."),
            ("Daniel Okafor", "pricing", 350, "Enterprise pricing and packaging; ran deal desks from Series A to IPO."),
            ("Sofia Reyes", "pricing", 195, "Early-stage pricing experiments on thin data; loves a good van Westendorp."),
            ("James Park", "fundraising", 300, "Closed two seeds and a Series A as founder; now helps founders run tight processes."),
            ("Aisha Patel", "fundraising", 400, "Ex-VC principal; knows what the Monday partner meeting actually asks."),
            ("Tom Nguyen", "fundraising", 225, "Angel-round specialist; SAFE mechanics and cap-table hygiene."),
            ("Lena Fischer", "gtm", 250, "Zero-to-first-100-customers operator across three B2B SaaS startups."),
            ("Marcus Hill", "gtm", 325, "Sales-led GTM; built the first repeatable enterprise playbook twice."),
            ("Priya Sharma", "gtm", 180, "Community-led growth; audiences before ads."),
            ("Nick Alvarez", "pitch", 220, "Deck surgeon; 40+ decks that closed. Narrative first, slides second."),
            ("Grace Liu", "pitch", 310, "Ex-founder, ex-VC; rehearses founders for the meeting they're not in."),
            ("Omar Haddad", "pitch", 175, "Messaging tests and positioning sprints for pre-seed teams."),
            ("Rachel Stone", "legal", 380, "Startup counsel; financings, IP assignment, first commercial contracts."),
            ("David Kim", "legal", 300, "Contract negotiation and vendor paper at speed; ex-BigLaw, allergic to overlawyering."),
            ("Elena Petrova", "legal", 260, "Privacy and compliance for data-heavy products; GDPR/CCPA pragmatist."),
            ("Sam Torres", "ecosystem", 200, "SF ecosystem navigator: intros, spaces, visas, first hires."),
            ("Hannah Wright", "ecosystem", 240, "Remote-first ops; built distributed teams across nine time zones."),
            ("Leo Martins", "ecosystem", 165, "Second-city arbitrage; runway math for relocation decisions."),
            ("Ava Robinson", "engineering", 350, "Fractional CTO; build-vs-buy calls and first-team hiring."),
            ("Chris Doyle", "engineering", 290, "Scalability and infra; keeps the duct tape from becoming the architecture."),
            ("Yuki Tanaka", "engineering", 310, "Security and compliance engineering for early B2B; SOC 2 without the agony."),
        ]
        for name, domain, rate, skills in seed:
            db.add(
                AdviserModel(
                    id=_new_id("adviser"),
                    name=name,
                    domain=domain,
                    metro="San Francisco",
                    hourly_rate=rate,
                    skills_profile=skills,
                )
            )
        db.flush()


board_service = BoardService()
