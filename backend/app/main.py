import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import run_migrations
from app.routers import matters, public, users
from app.services.matter_service import matter_service

app = FastAPI(title="Charter Law API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    if os.getenv("RUN_MIGRATIONS_ON_STARTUP", "true").lower() == "true":
        run_migrations()
    if os.getenv("SEED_DEMO_DATA", "false").lower() == "true":
        matter_service.seed_demo_data()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(users.router, prefix="/v1")
app.include_router(matters.router, prefix="/v1")
app.include_router(public.router, prefix="/v1")
