import pytest

from app.config import Settings, load_settings, validate_settings


def _prod(**over) -> Settings:
    base = dict(
        app_env="production",
        clerk_demo_auth=False,
        database_url="postgres://db",
        clerk_jwks_url="https://clerk/jwks",
        clerk_jwt_issuer="https://clerk",
        stripe_secret_key="sk_test",
        gcs_bucket="bucket",
        sentry_dsn=None,
    )
    base.update(over)
    return Settings(**base)


def test_dev_validation_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    validate_settings(load_settings())  # must not raise


def test_prod_requires_secrets() -> None:
    with pytest.raises(RuntimeError):
        validate_settings(_prod(database_url=None))


def test_prod_rejects_demo_auth() -> None:
    with pytest.raises(RuntimeError):
        validate_settings(_prod(clerk_demo_auth=True))


def test_prod_valid_config_ok() -> None:
    validate_settings(_prod())
