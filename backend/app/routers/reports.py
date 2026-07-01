from fastapi import APIRouter, Depends

from app.services.auth import AuthContext, require_auth_context
from app.services.matter_service import matter_service

router = APIRouter(tags=["reports"])


@router.get("/reports/activity")
def activity(auth: AuthContext = Depends(require_auth_context)) -> dict:
    """Org-scoped activity summary: counts by matter status."""
    return matter_service.activity_report(auth.organisation_id)
