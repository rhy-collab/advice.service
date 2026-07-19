import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import load_settings, validate_settings
from app.db.session import SessionLocal, run_migrations
from app.middleware.public_hardening import PublicEndpointHardeningMiddleware
from app.observability import RequestIdMiddleware, init_sentry
from app.routers import attorney, matters, playbooks, public, reports, threads, users
from app.services.matter_service import matter_service

app = FastAPI(title="Charter Law API", version="0.1.0")

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=os.getenv("ALLOWED_ORIGIN_REGEX", r"https://.*\.vercel\.app"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PublicEndpointHardeningMiddleware)
app.add_middleware(RequestIdMiddleware)


def database_ready(session_factory=SessionLocal) -> bool:
    try:
        with session_factory() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@app.on_event("startup")
def startup() -> None:
    validate_settings(load_settings())
    init_sentry()
    if os.getenv("RUN_MIGRATIONS_ON_STARTUP", "false").lower() == "true":
        run_migrations()
    if os.getenv("SEED_DEMO_DATA", "false").lower() == "true":
        matter_service.seed_demo_data()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready() -> dict[str, str]:
    if not database_ready():
        raise HTTPException(status_code=503, detail="database not ready")
    return {"status": "ready"}


# "/v1" for direct access; "/api/v1" so the same app works behind Vercel's
# "/api(/.*)" service rewrite, which forwards the original path.
for _prefix in ("/v1", "/api/v1"):
    app.include_router(users.router, prefix=_prefix)
    app.include_router(attorney.router, prefix=_prefix)
    app.include_router(playbooks.router, prefix=_prefix)
    app.include_router(matters.router, prefix=_prefix)
    app.include_router(reports.router, prefix=_prefix)
    app.include_router(public.router, prefix=_prefix)
    app.include_router(threads.router, prefix=_prefix)
