from app.observability import init_sentry


def test_sentry_noop_without_dsn(monkeypatch) -> None:
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    assert init_sentry() is False
