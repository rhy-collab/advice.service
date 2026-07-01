from dataclasses import dataclass
from functools import lru_cache
import os

import jwt
from jwt import PyJWKClient
from fastapi import Header, HTTPException


@dataclass(frozen=True)
class AuthContext:
    user_id: str
    email: str
    name: str
    organisation_id: str
    organisation_name: str


def require_auth_context(authorization: str | None = Header(default=None)) -> AuthContext:
    """Verify Clerk auth or use explicit local demo auth.

    Local development keeps `CLERK_DEMO_AUTH=true` by default so the API can be
    exercised before a real Clerk app exists. Production should set
    `CLERK_DEMO_AUTH=false`, `CLERK_JWKS_URL`, and `CLERK_JWT_ISSUER`.
    """
    demo_auth_enabled = os.getenv("CLERK_DEMO_AUTH", "true").lower() == "true"

    if authorization is None:
        if demo_auth_enabled:
            return demo_auth_context()
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.removeprefix("Bearer ").strip()

    if token == "demo" and demo_auth_enabled:
        return demo_auth_context()

    return verify_clerk_token(token)


def demo_auth_context() -> AuthContext:
    return AuthContext(
        user_id="user_demo",
        email="founder@example.com",
        name="Founder Example",
        organisation_id="org_demo",
        organisation_name="Acme Labs",
    )


def verify_clerk_token(token: str) -> AuthContext:
    jwks_url = os.getenv("CLERK_JWKS_URL")
    issuer = os.getenv("CLERK_JWT_ISSUER")

    if not jwks_url or not issuer:
        raise HTTPException(status_code=500, detail="Clerk JWT verification is not configured")

    try:
        signing_key = get_jwks_client(jwks_url).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid Clerk token") from exc

    organisation_id = claims.get("org_id")
    if not organisation_id:
        raise HTTPException(status_code=403, detail="A Clerk organisation is required")

    return AuthContext(
        user_id=claims["sub"],
        email=claims.get("email", ""),
        name=claims.get("name", claims.get("email", "Authenticated user")),
        organisation_id=organisation_id,
        organisation_name=claims.get("org_name", claims.get("org_slug", organisation_id)),
    )


@lru_cache(maxsize=4)
def get_jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)
