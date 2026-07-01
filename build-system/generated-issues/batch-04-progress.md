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

## Issue 3 — Attorney workspace v1

**Status:** Completed

**What changed**
- Added a dedicated attorney backend router under `/v1/attorney`.
- Added `GET /v1/attorney/queue` for attorney/admin users to see `attorney_queue` and `attorney_review` matters in their organisation.
- Added `POST /v1/attorney/matters/{matter_id}/approve` for attorney/admin delivery approval.
- Removed approval from the customer matter router surface.
- Tightened approval so a matter must have upload complete, payment paid, and be in `attorney_queue` or `attorney_review`.
- Added `/attorney` frontend routing and pointed the internal queue UI to the attorney API routes.
- Updated the API contract and navigation label.

**Commands run**
- `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q`
- `cd frontend && npm run build`
- Browser verification at `http://127.0.0.1:5173/attorney`

**Result**
- Backend: `42 passed, 3 warnings`.
- Frontend build passed.
- Browser check showed the attorney delivery queue, `/attorney` nav link, one demo queue row, and no console errors.

**Remaining work**
- Later batch should build the full cross-organisation attorney workbench model; this first slice scopes attorneys to their active Clerk organisation.

## Issue 4 — Customer portal completion

**Status:** Completed

**What changed**
- Converted the dashboard `Upload .docx` action into a real jump link to the upload panel.
- Added the missing `Attorney Queue` stage so the customer status tracker reflects the backend lifecycle: Received → AI Review → Attorney Queue → Attorney Review → Delivered.
- Confirmed portal upload code still creates a matter, uses signed/demo upload targets, marks upload complete, creates checkout, and disables download until `deliverableAvailable`.

**Commands run**
- `cd frontend && npm run build`
- Browser verification at `http://127.0.0.1:5173/portal`

**Result**
- Frontend build passed.
- Browser check confirmed the portal renders, has the upload panel, shows the 5-stage tracker, and keeps pending deliverables disabled.

**Remaining work**
- Real end-to-end upload/payment smoke test requires live Clerk/Stripe/GCS credentials or a fuller mocked browser fixture.
