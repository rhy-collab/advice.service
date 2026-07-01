from fastapi import APIRouter, Depends, HTTPException, Request

from app.schemas.matters import (
    AssistantMessageRequest,
    AssistantMessageResponse,
    AttorneyApprovalRequest,
    AttorneyApprovalResponse,
    CheckoutResponse,
    CreateMatterRequest,
    CreateMatterResponse,
    MatterDetailResponse,
    MatterEventsResponse,
    MatterListResponse,
    MatterSummary,
    SignedUrlResponse,
    StripeWebhookResponse,
    TransitionRequest,
    UploadCompleteResponse,
)
from app.services.auth import AuthContext, require_attorney_context, require_auth_context
from app.services.checkout_service import checkout_service
from app.services.matter_service import matter_service

router = APIRouter(tags=["matters"])


@router.get("/matters", response_model=MatterListResponse)
def list_matters(auth: AuthContext = Depends(require_auth_context)) -> MatterListResponse:
    return MatterListResponse(matters=matter_service.list_matters(auth.organisation_id))


@router.post("/matters", response_model=CreateMatterResponse)
def create_matter(
    request: CreateMatterRequest,
    auth: AuthContext = Depends(require_auth_context),
) -> CreateMatterResponse:
    return matter_service.create_matter(request, auth.organisation_id)


@router.get("/matters/{matter_id}", response_model=MatterDetailResponse)
def get_matter(
    matter_id: str,
    auth: AuthContext = Depends(require_auth_context),
) -> MatterDetailResponse:
    matter = matter_service.get_matter(matter_id, auth.organisation_id)
    if matter is None:
        raise HTTPException(status_code=404, detail="Matter not found")
    return matter


@router.post("/matters/{matter_id}/checkout", response_model=CheckoutResponse)
def create_checkout(
    matter_id: str,
    auth: AuthContext = Depends(require_auth_context),
) -> CheckoutResponse:
    matter = matter_service.require_matter(matter_id, auth.organisation_id)
    checkout = checkout_service.create_checkout_url(matter.id, matter.service_tier, auth.email)
    matter_service.mark_checkout_created(matter.id, auth.organisation_id, checkout.session_id)
    return checkout


@router.post("/matters/{matter_id}/upload-complete", response_model=UploadCompleteResponse)
def complete_upload(
    matter_id: str,
    auth: AuthContext = Depends(require_auth_context),
) -> UploadCompleteResponse:
    return UploadCompleteResponse(matter=matter_service.mark_upload_complete(matter_id, auth.organisation_id))


@router.get("/matters/{matter_id}/download", response_model=SignedUrlResponse)
def download_matter(
    matter_id: str,
    auth: AuthContext = Depends(require_auth_context),
) -> SignedUrlResponse:
    return SignedUrlResponse(url=matter_service.delivery_download_url(matter_id, auth.organisation_id))


@router.post("/matters/{matter_id}/attorney-approval", response_model=AttorneyApprovalResponse)
def approve_matter(
    matter_id: str,
    request: AttorneyApprovalRequest,
    auth: AuthContext = Depends(require_attorney_context),
) -> AttorneyApprovalResponse:
    return AttorneyApprovalResponse(
        matter=matter_service.approve_deliverable(matter_id, auth.organisation_id, request)
    )


@router.get("/matters/{matter_id}/events", response_model=MatterEventsResponse)
def list_matter_events(
    matter_id: str,
    auth: AuthContext = Depends(require_auth_context),
) -> MatterEventsResponse:
    return MatterEventsResponse(events=matter_service.list_events(matter_id, auth.organisation_id))


@router.post("/matters/{matter_id}/transition", response_model=MatterSummary)
def transition_matter(
    matter_id: str,
    request: TransitionRequest,
    auth: AuthContext = Depends(require_attorney_context),
) -> MatterSummary:
    if request.status == "delivered":
        raise HTTPException(status_code=400, detail="Use the attorney-approval endpoint to deliver")
    return matter_service.transition_status(matter_id, auth.organisation_id, request.status)


@router.post("/assistant/messages", response_model=AssistantMessageResponse)
def post_assistant_message(
    request: AssistantMessageRequest,
    auth: AuthContext = Depends(require_auth_context),
) -> AssistantMessageResponse:
    matter_service.require_matter(request.matter_id, auth.organisation_id)
    routed_to_attorney = request.mode == "attorney"
    answer = (
        "Your question has been routed to the reviewing attorney."
        if routed_to_attorney
        else "This is preparation only, not legal advice. Key risks will be summarised after attorney review."
    )
    return AssistantMessageResponse(
        mode=request.mode,
        answer=answer,
        routed_to_attorney=routed_to_attorney,
    )


@router.post("/stripe/webhook", response_model=StripeWebhookResponse)
async def stripe_webhook(request: Request) -> StripeWebhookResponse:
    event = checkout_service.construct_webhook_event(
        await request.body(),
        request.headers.get("stripe-signature"),
    )

    if _stripe_value(event, "type") != "checkout.session.completed":
        return StripeWebhookResponse(received=True)

    session = _stripe_value(_stripe_value(event, "data", {}), "object", {})
    metadata = _stripe_value(session, "metadata", {})
    matter_id = _stripe_value(metadata, "matter_id") or _stripe_value(session, "client_reference_id")
    checkout_session_id = _stripe_value(session, "id")

    if not matter_id:
        return StripeWebhookResponse(received=True)

    matter = matter_service.mark_payment_status(
        matter_id=matter_id,
        payment_status="paid",
        checkout_session_id=checkout_session_id,
    )

    return StripeWebhookResponse(
        received=True,
        matter_id=matter.id if matter else matter_id,
        payment_status=matter.payment_status if matter else None,
    )


def _stripe_value(obj: object, key: str, default: object | None = None) -> object | None:
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return obj[key]  # type: ignore[index]
    except (KeyError, TypeError):
        return default
