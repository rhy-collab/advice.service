from fastapi import APIRouter, Depends, HTTPException

from app.schemas.boards import (
    AdviserQuotesResponse,
    CreateThreadRequest,
    PostMessageRequest,
    PostMessageResponse,
    ThreadDetail,
    ThreadListResponse,
    UpdateContextRequest,
)
from app.services.auth import AuthContext, require_auth_context
from app.services.board_service import board_service

router = APIRouter(tags=["threads"])


@router.get("/threads", response_model=ThreadListResponse)
def list_threads(auth: AuthContext = Depends(require_auth_context)) -> ThreadListResponse:
    return board_service.list_threads(auth.organisation_id)


@router.post("/threads", response_model=ThreadDetail)
def create_thread(
    request: CreateThreadRequest,
    auth: AuthContext = Depends(require_auth_context),
) -> ThreadDetail:
    return board_service.create_thread(request, auth.organisation_id)


@router.get("/threads/{thread_id}", response_model=ThreadDetail)
def get_thread(
    thread_id: str,
    auth: AuthContext = Depends(require_auth_context),
) -> ThreadDetail:
    thread = board_service.get_thread(thread_id, auth.organisation_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.post("/threads/{thread_id}/context", response_model=ThreadDetail)
def update_context(
    thread_id: str,
    request: UpdateContextRequest,
    auth: AuthContext = Depends(require_auth_context),
) -> ThreadDetail:
    thread = board_service.update_context(thread_id, request, auth.organisation_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.post("/threads/{thread_id}/messages", response_model=PostMessageResponse)
def post_message(
    thread_id: str,
    request: PostMessageRequest,
    auth: AuthContext = Depends(require_auth_context),
) -> PostMessageResponse:
    response = board_service.post_message(thread_id, request.content, auth.organisation_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return response


@router.get("/threads/{thread_id}/adviser-quotes", response_model=AdviserQuotesResponse)
def adviser_quotes(
    thread_id: str,
    auth: AuthContext = Depends(require_auth_context),
) -> AdviserQuotesResponse:
    """The explicit 'match me with a real adviser' request — the only paid path."""
    response = board_service.adviser_quotes(thread_id, auth.organisation_id)
    if response is None:
        raise HTTPException(
            status_code=409,
            detail="Thread has no routed domain yet — the panel must run before advisers can be matched",
        )
    return response
