import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import load_settings, validate_settings
from app.db.session import SessionLocal, run_migrations
from app.observability import init_sentry
from app.routers import matters, public, reports, users
from app.services.matter_service import matter_service

app = FastAPI(title="Charter Law API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    if os.getenv("RUN_MIGRATIONS_ON_STARTUP", "true").lower() == "true":
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


app.include_router(users.router, prefix="/v1")
app.include_router(matters.router, prefix="/v1")
app.include_router(reports.router, prefix="/v1")
app.include_router(public.router, prefix="/v1")
