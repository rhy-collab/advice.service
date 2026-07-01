import json
import os
from typing import Any

import stripe
from fastapi import HTTPException

from app.schemas.matters import CheckoutResponse, ServiceTier

SERVICE_TIER_ENV_KEYS: dict[ServiceTier, str] = {
    "simple_review": "STRIPE_PRICE_SIMPLE_REVIEW",
    "standard_redline": "STRIPE_PRICE_STANDARD_REDLINE",
    "full_negotiation": "STRIPE_PRICE_FULL_NEGOTIATION",
}


class CheckoutService:
    def create_checkout_url(
        self,
        matter_id: str,
        service_tier: ServiceTier,
        customer_email: str,
    ) -> CheckoutResponse:
        secret_key = os.getenv("STRIPE_SECRET_KEY")
        price_id = os.getenv(SERVICE_TIER_ENV_KEYS[service_tier])

        if not secret_key or not price_id:
            session_id = f"demo-{matter_id}"
            return CheckoutResponse(
                checkout_url=f"https://checkout.stripe.com/c/pay/{session_id}",
                mode="demo",
                session_id=session_id,
            )

        stripe.api_key = secret_key
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=customer_email,
            client_reference_id=matter_id,
            success_url=os.getenv("STRIPE_SUCCESS_URL", "http://127.0.0.1:5173/portal?checkout=success"),
            cancel_url=os.getenv("STRIPE_CANCEL_URL", "http://127.0.0.1:5173/portal?checkout=cancelled"),
            metadata={"matter_id": matter_id},
        )

        return CheckoutResponse(checkout_url=session.url or "", mode="stripe", session_id=session.id)

    def construct_webhook_event(self, payload: bytes, signature: str | None) -> dict[str, Any]:
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if webhook_secret:
            if not signature:
                raise HTTPException(status_code=400, detail="Missing Stripe signature")
            try:
                return stripe.Webhook.construct_event(payload, signature, webhook_secret)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Invalid Stripe payload") from exc
            except stripe.SignatureVerificationError as exc:
                raise HTTPException(status_code=400, detail="Invalid Stripe signature") from exc

        try:
            return stripe.Event.construct_from(json.loads(payload.decode("utf-8")), stripe.api_key)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid Stripe payload") from exc


checkout_service = CheckoutService()
