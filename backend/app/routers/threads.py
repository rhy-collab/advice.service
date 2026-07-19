from fastapi import APIRouter, Depends, HTTPException

from app.schemas.boards import (
    AddConsultantRequest,
    AdviserDirectoryResponse,
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


@router.post("/threads/{thread_id}/charter", response_model=ThreadDetail)
def charter_message(
    thread_id: str,
    auth: AuthContext = Depends(require_auth_context),
) -> ThreadDetail:
    """Founder engages Charter Consultancy's triage team (reveals the §6 budget estimate)."""
    thread = board_service.charter_message(thread_id, auth.organisation_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.post("/threads/{thread_id}/consultants", response_model=ThreadDetail)
def add_consultant(
    thread_id: str,
    request: AddConsultantRequest,
    auth: AuthContext = Depends(require_auth_context),
) -> ThreadDetail:
    """Add a marketplace consultant into the chat."""
    thread = board_service.add_consultant(
        thread_id, auth.organisation_id, request.name, request.title, request.hourly_rate
    )
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.get("/advisers", response_model=AdviserDirectoryResponse)
def list_advisers(auth: AuthContext = Depends(require_auth_context)) -> AdviserDirectoryResponse:
    """Browseable adviser directory across all seven services (demo data)."""
    return board_service.list_advisers()


@router.get("/threads-diagnostics/anthropic")
def anthropic_diagnostics(auth: AuthContext = Depends(require_auth_context)) -> dict:
    """Temporary: report whether the Anthropic API is reachable and why not. No secrets returned."""
    import os
    from urllib import error as urlerror

    from app.services.ai_prep_service import AnthropicMessageClient

    key = os.getenv("ANTHROPIC_API_KEY", "")
    info: dict = {
        "key_present": bool(key),
        "key_shape": f"{key[:7]}…len{len(key)}" if key else None,
        "model_env": os.getenv("ANTHROPIC_MODEL"),
    }
    if not key:
        return info
    try:
        response = AnthropicMessageClient().create_message(
            {
                "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
                "max_tokens": 16,
                "messages": [{"role": "user", "content": "Say ok"}],
            }
        )
        info["ok"] = True
        info["reply"] = "".join(p.get("text", "") for p in response.get("content", []))[:40]
    except urlerror.HTTPError as exc:
        info["ok"] = False
        info["http_status"] = exc.code
        try:
            info["error_body"] = exc.read().decode("utf-8", "replace")[:300]
        except Exception:
            pass
    except Exception as exc:
        info["ok"] = False
        info["error"] = str(exc)[:300]
    return info


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
