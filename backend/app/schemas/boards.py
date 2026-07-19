from pydantic import BaseModel, Field


class ContextProfile(BaseModel):
    users_customers: str | None = None
    revenue_or_funding_stage: str | None = None
    customer_profile: str | None = None
    team_size: str | None = None
    goals: str | None = None

    def missing_fields(self) -> list[str]:
        labels = {
            "users_customers": "how many users or customers you have today",
            "revenue_or_funding_stage": "your current MRR or funding stage",
            "customer_profile": "who exactly the customer is",
            "team_size": "your team size",
            "goals": "what success looks like",
        }
        return [labels[k] for k, v in self.model_dump().items() if not (v and v.strip())]


class AdvisorPosition(BaseModel):
    advisor_name: str
    persona: str
    position: str
    cross_examination: str | None = None


class Verdict(BaseModel):
    ruling: str
    assumptions: list[str] = Field(default_factory=list)
    dissent: str | None = None
    validation_plan: str | None = None
    follow_up_questions: list[str] = Field(default_factory=list)
    # price_tier / estimated_cost are intentionally NOT exposed here (invariant 7).


class BoardView(BaseModel):
    id: str
    round: int
    domain: str | None = None
    status: str
    positions: list[AdvisorPosition] = Field(default_factory=list)
    verdict: Verdict | None = None


class ThreadMessage(BaseModel):
    role: str
    content: str
    created_at: str


class ThreadSummary(BaseModel):
    id: str
    title: str
    status: str
    domain: str | None = None
    created_at: str


class ThreadDetail(BaseModel):
    id: str
    title: str
    problem_text: str
    status: str
    domain: str | None = None
    boards: list[BoardView] = Field(default_factory=list)
    messages: list[ThreadMessage] = Field(default_factory=list)
    context_profile: ContextProfile
    context_sufficient: bool


class ThreadListResponse(BaseModel):
    threads: list[ThreadSummary]


class CreateThreadRequest(BaseModel):
    problem_text: str = Field(min_length=1, max_length=8000)


class UpdateContextRequest(BaseModel):
    users_customers: str | None = None
    revenue_or_funding_stage: str | None = None
    customer_profile: str | None = None
    team_size: str | None = None
    goals: str | None = None


class PostMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class PostMessageResponse(BaseModel):
    reply: ThreadMessage


class AdviserQuote(BaseModel):
    """Shown only when the founder explicitly asks to be matched (invariant 7)."""

    adviser_id: str
    name: str
    metro: str
    hourly_rate: int
    skills_profile: str
    estimated_hours: str
    estimated_total: int
    platform_fee_pct: int
    not_to_exceed: int


class AdviserQuotesResponse(BaseModel):
    domain: str
    quotes: list[AdviserQuote]
