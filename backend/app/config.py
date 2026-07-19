"""Typed application settings + production validation (fail closed)."""
import os
from dataclasses import dataclass
from pathlib import Path


def load_env_file(path: Path | None = None) -> None:
    """Minimal .env loader (stdlib only). Real environment variables always win."""
    env_path = path or Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()

REQUIRED_IN_PRODUCTION = (
    "database_url",
    "clerk_jwks_url",
    "clerk_jwt_issuer",
    "stripe_secret_key",
    "gcs_bucket",
)


@dataclass(frozen=True)
class Settings:
    app_env: str
    clerk_demo_auth: bool
    database_url: str | None
    clerk_jwks_url: str | None
    clerk_jwt_issuer: str | None
    stripe_secret_key: str | None
    gcs_bucket: str | None
    sentry_dsn: str | None

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


def load_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        clerk_demo_auth=os.getenv("CLERK_DEMO_AUTH", "false").lower() == "true",
        database_url=os.getenv("DATABASE_URL"),
        clerk_jwks_url=os.getenv("CLERK_JWKS_URL"),
        clerk_jwt_issuer=os.getenv("CLERK_JWT_ISSUER"),
        stripe_secret_key=os.getenv("STRIPE_SECRET_KEY"),
        gcs_bucket=os.getenv("GCS_BUCKET"),
        sentry_dsn=os.getenv("SENTRY_DSN"),
    )


def validate_settings(settings: Settings) -> None:
    """Raise in production if the config is unsafe/incomplete. No-op in dev."""
    if not settings.is_production:
        return
    if settings.clerk_demo_auth:
        raise RuntimeError("CLERK_DEMO_AUTH must be false in production")
    missing = [f for f in REQUIRED_IN_PRODUCTION if not getattr(settings, f)]
    if missing:
        raise RuntimeError(f"Missing required production config: {', '.join(missing)}")
