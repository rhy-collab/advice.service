from datetime import datetime, timedelta, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MatterStatus = Literal[
    "intake",
    "ai_review",
    "attorney_queue",
    "attorney_review",
    "delivered",
    "completed",
]

ServiceTier = Literal["simple_review", "standard_redline", "full_negotiation"]
AssistantMode = Literal["ai_preparation", "attorney"]
UploadStatus = Literal["awaiting_upload", "uploaded"]
PaymentStatus = Literal["unpaid", "checkout_pending", "paid", "failed", "refunded"]


class MatterSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    file_name: str = Field(serialization_alias="fileName")
    service_tier: ServiceTier = Field(serialization_alias="serviceTier")
    contract_type: str = Field(serialization_alias="contractType")
    status: MatterStatus
    upload_status: UploadStatus = Field(serialization_alias="uploadStatus")
    payment_status: PaymentStatus = Field(serialization_alias="paymentStatus")
    submitted_at: datetime = Field(serialization_alias="submittedAt")
    next_update_eta_minutes: int | None = Field(default=None, serialization_alias="nextUpdateEtaMinutes")
    deliverable_available: bool = Field(default=False, serialization_alias="deliverableAvailable")


class MatterEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str
    actor: str
    occurred_at: datetime = Field(serialization_alias="occurredAt")
    note: str


class MatterDetailResponse(BaseModel):
    matter: MatterSummary
    events: list[MatterEvent]


class MatterListResponse(BaseModel):
    matters: list[MatterSummary]


class AttorneyQueueResponse(BaseModel):
    matters: list[MatterSummary]


class CreateMatterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    file_name: str = Field(validation_alias="fileName")
    service_tier: ServiceTier = Field(validation_alias="serviceTier")
    contract_type: str = Field(validation_alias="contractType")
    notes: str = ""


class UploadTarget(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    method: Literal["PUT"]
    url: str
    expires_at: datetime = Field(serialization_alias="expiresAt")
    mode: Literal["gcs", "demo"]


class CreateMatterResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    matter_id: str = Field(serialization_alias="matterId")
    status: MatterStatus
    upload: UploadTarget


class CheckoutResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    checkout_url: str = Field(serialization_alias="checkoutUrl")
    mode: Literal["stripe", "demo"]
    session_id: str = Field(serialization_alias="sessionId")


class UploadCompleteResponse(BaseModel):
    matter: MatterSummary


class AttorneyApprovalRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    deliverable_file_name: str = Field(validation_alias="deliverableFileName")
    note: str = "Attorney approved the redline for client delivery."


class AttorneyApprovalResponse(BaseModel):
    matter: MatterSummary


class StripeWebhookResponse(BaseModel):
    received: bool
    matter_id: str | None = Field(default=None, serialization_alias="matterId")
    payment_status: PaymentStatus | None = Field(default=None, serialization_alias="paymentStatus")


class SignedUrlResponse(BaseModel):
    url: str


class AssistantMessageRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    matter_id: str = Field(validation_alias="matterId")
    mode: AssistantMode
    message: str


class AssistantMessageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mode: AssistantMode
    answer: str
    routed_to_attorney: bool = Field(serialization_alias="routedToAttorney")


def demo_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=15)


class TransitionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: MatterStatus


class MatterEventsResponse(BaseModel):
    events: list[MatterEvent]
