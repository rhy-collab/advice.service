from app.services.checkout_service import CheckoutService


def test_checkout_returns_demo_url_without_stripe_config(monkeypatch) -> None:
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.delenv("STRIPE_PRICE_STANDARD_REDLINE", raising=False)

    checkout = CheckoutService().create_checkout_url(
        matter_id="matter_123",
        service_tier="standard_redline",
        customer_email="founder@example.com",
    )

    assert checkout.mode == "demo"
    assert checkout.checkout_url.endswith("demo-matter_123")
    assert checkout.session_id == "demo-matter_123"
