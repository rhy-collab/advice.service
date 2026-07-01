"""Env-guarded Sentry init. No-op (and never crashes) when SENTRY_DSN is unset."""
import os


def init_sentry() -> bool:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return False
    try:
        import sentry_sdk

        sentry_sdk.init(dsn=dsn, traces_sample_rate=0.0)
        return True
    except Exception:
        return False
