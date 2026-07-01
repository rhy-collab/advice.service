from fastapi import APIRouter, Depends

from app.schemas.playbook import (
    Playbook,
    PlaybookCheck,
    PlaybookCheckCreate,
    PlaybookCheckUpdate,
    PlaybookCreate,
    PlaybookListResponse,
)
from app.services.auth import AuthContext, require_attorney_context
from app.services.playbook_service import playbook_service

router = APIRouter(prefix="/attorney/playbooks", tags=["playbooks"])


@router.get("", response_model=PlaybookListResponse)
def list_playbooks(
    contract_type: str | None = None,
    auth: AuthContext = Depends(require_attorney_context),
) -> PlaybookListResponse:
    return PlaybookListResponse(
        playbooks=playbook_service.list_playbooks(contract_type=contract_type, organisation_id=auth.organisation_id)
    )


@router.post("", response_model=Playbook)
def create_playbook(
    request: PlaybookCreate,
    auth: AuthContext = Depends(require_attorney_context),
) -> Playbook:
    return playbook_service.create_playbook(
        PlaybookCreate(
            name=request.name,
            contract_type=request.contract_type,
            jurisdiction=request.jurisdiction,
            organisation_id=request.organisation_id or auth.organisation_id,
        )
    )


@router.post("/{playbook_id}/checks", response_model=Playbook)
def add_check(
    playbook_id: str,
    request: PlaybookCheckCreate,
    auth: AuthContext = Depends(require_attorney_context),
) -> Playbook:
    return playbook_service.add_check(playbook_id, request)


@router.patch("/checks/{check_id}", response_model=PlaybookCheck)
def update_check(
    check_id: str,
    request: PlaybookCheckUpdate,
    auth: AuthContext = Depends(require_attorney_context),
) -> PlaybookCheck:
    return playbook_service.update_check(check_id, request)
