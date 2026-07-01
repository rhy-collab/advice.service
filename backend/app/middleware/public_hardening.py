from __future__ import annotations

from dataclasses import dataclass, field
import os
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from app.services.document_checker import MAX_CHECK_BYTES

MAX_PUBLIC_UPLOAD_BODY_BYTES = MAX_CHECK_BYTES + 1_000_000
PUBLIC_RATE_LIMIT_WINDOW_SECONDS = 60


@dataclass
class PublicRateLimiter:
    hits: dict[tuple[str, str], list[float]] = field(default_factory=dict)

    def allow(self, key: str, path: str, limit: int, now: float | None = None) -> bool:
        if limit <= 0:
            return True
        current = time.monotonic() if now is None else now
        bucket_key = (key, path)
        window_start = current - PUBLIC_RATE_LIMIT_WINDOW_SECONDS
        recent = [hit for hit in self.hits.get(bucket_key, []) if hit >= window_start]
        if len(recent) >= limit:
            self.hits[bucket_key] = recent
            return False
        recent.append(current)
        self.hits[bucket_key] = recent
        return True

    def clear(self) -> None:
        self.hits.clear()


public_rate_limiter = PublicRateLimiter()


class PublicEndpointHardeningMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.url.path.startswith("/v1/public/"):
            return await call_next(request)

        if request.url.path == "/v1/public/check-contract":
            content_length = request.headers.get("content-length")
            if content_length and content_length.isdigit() and int(content_length) > public_upload_body_limit():
                return JSONResponse(
                    {"detail": "Document is too large for the free checker"},
                    status_code=413,
                )

        if not public_rate_limiter.allow(client_key(request), request.url.path, public_rate_limit()):
            return JSONResponse(
                {"detail": "Too many public requests. Please try again later."},
                status_code=429,
            )

        return await call_next(request)


def public_rate_limit() -> int:
    return int(os.getenv("PUBLIC_RATE_LIMIT_PER_MINUTE", "60"))


def public_upload_body_limit() -> int:
    return int(os.getenv("PUBLIC_UPLOAD_BODY_LIMIT_BYTES", str(MAX_PUBLIC_UPLOAD_BODY_BYTES)))


def client_key(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
