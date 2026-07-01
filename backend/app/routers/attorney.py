from fastapi import APIRouter, Depends

from app.schemas.matters import (
    AttorneyApprovalRequest,
    AttorneyApprovalResponse,
    AttorneyQueueResponse,
)
from app.services.auth import AuthContext, require_attorney_context
from app.services.matter_service import matter_service

router = APIRouter(prefix="/attorney", tags=["attorney"])


@router.get("/queue", response_model=AttorneyQueueResponse)
def list_attorney_queue(auth: AuthContext = Depends(require_attorney_context)) -> AttorneyQueueResponse:
    return AttorneyQueueResponse(matters=matter_service.list_attorney_queue(auth.organisation_id))


@router.post("/matters/{matter_id}/approve", response_model=AttorneyApprovalResponse)
def approve_attorney_matter(
    matter_id: str,
    request: AttorneyApprovalRequest,
    auth: AuthContext = Depends(require_attorney_context),
) -> AttorneyApprovalResponse:
    return AttorneyApprovalResponse(
        matter=matter_service.approve_deliverable(matter_id, auth.organisation_id, request)
    )
