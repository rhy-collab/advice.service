# Batch 04 Progress Log

## Issue 1 — Confirm remote CI green + branch protection

**Status:** Blocked

**What changed**
- Confirmed remote GitHub Actions on `main` is green.
- Could not enable or verify branch protection through the GitHub API because GitHub returned `HTTP 403`: private repo branch protection requires GitHub Pro or making the repository public.
- Recorded the blocker in `BLOCKERS.md`.

**Commands run**
- `gh run list --repo Charter-Law/Charter-Law --branch main --limit 5`
- `gh api repos/Charter-Law/Charter-Law/branches/main/protection --jq '{required_status_checks,required_pull_request_reviews}'`

**Result**
- Latest `main` CI run: `completed success`.
- Branch protection: externally blocked by GitHub plan/settings.

**Remaining work**
- Owner enables branch protection in GitHub once the plan/settings allow it.

## Issue 2 — Public-endpoint hardening

**Status:** Completed

**What changed**
- Added `PublicEndpointHardeningMiddleware` for unauthenticated `/v1/public/*` routes.
- Added per-IP fixed-window rate limiting with `PUBLIC_RATE_LIMIT_PER_MINUTE`.
- Added edge `Content-Length` rejection for oversized checker uploads with `PUBLIC_UPLOAD_BODY_LIMIT_BYTES`.
- Changed the checker endpoint to stream uploads in chunks and stop above `MAX_CHECK_BYTES`.
- Tightened public intake validation with `EmailStr` and whitespace stripping.
- Kept the free checker non-persistent: it still returns `stored=false` and does not create DB/GCS records.

**Commands run**
- `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q`

**Result**
- `37 passed, 3 warnings`.

**Remaining work**
- None for this issue.
