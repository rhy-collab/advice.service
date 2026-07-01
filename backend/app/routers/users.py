from fastapi import APIRouter, Depends

from app.services.auth import AuthContext, require_auth_context

router = APIRouter(tags=["users"])


@router.get("/me")
def get_me(auth: AuthContext = Depends(require_auth_context)) -> dict[str, object]:
    return {
        "user": {
            "id": auth.user_id,
            "email": auth.email,
            "name": auth.name,
        },
        "organisation": {
            "id": auth.organisation_id,
            "name": auth.organisation_name,
        },
    }
