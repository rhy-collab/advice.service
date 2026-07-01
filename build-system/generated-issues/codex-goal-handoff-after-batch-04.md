# Codex `/goal` Handoff After Batch 04

Use this as the Claude/Codex continuation summary.

## Current Repo State

- Repo: `Charter-Law/Charter-Law`
- Local path: `/Users/rhys/Downloads/Projects/Charter Law`
- Branch: `feat/batch-04`
- Base: latest `main` from GitHub before Batch 04 work
- Preserved local untracked file: `codex-review-01.md`

## Batch 04 Status

Issue 1 — Confirm remote CI green + branch protection: **Blocked**
- Remote GitHub Actions on `main` is green.
- Branch protection cannot be enabled/verified through the API because GitHub returned `HTTP 403`: private repo branch protection requires GitHub Pro or making the repo public.
- Blocker documented in `BLOCKERS.md`.

Issue 2 — Public-endpoint hardening: **Completed**
- Per-IP rate limiting for `/v1/public/*`.
- Edge `Content-Length` rejection for checker uploads.
- Streaming checker read limit.
- Email validation + whitespace trimming for public intake.
- Tests added.

Issue 3 — Attorney workspace v1: **Completed**
- Added `/v1/attorney/queue`.
- Added `/v1/attorney/matters/{matter_id}/approve`.
- Removed approval from the customer matter API surface.
- Added `/attorney` frontend route.
- Browser verified `/attorney`.

Issue 4 — Customer portal completion: **Completed**
- Upload action jumps to the upload panel.
- Customer tracker now shows five lifecycle stages.
- Download remains disabled until `deliverableAvailable`.
- Browser verified `/portal`.

Issue 5 — AI prep engine v1: **Completed**
- Added `matter_ai_preps` table and migration.
- Upload completion creates an internal prep summary + issue list with deterministic stub fallback.
- Matter moves to `attorney_queue`.
- Prep is exposed only through attorney route `/v1/attorney/matters/{id}/ai-prep`.
- Customer matter detail does not expose prep.

Issue 6 — Playbook data model v1: **Completed**
- Added playbook/check models, migration, schemas, and service.
- Added structured fields for detection, severity, remediation intent, preferred/acceptable/unacceptable fallback language, and accuracy counters.
- Added idempotent NDA seed and tests.

Issue 7 — Status-change notifications: **Completed**
- Added notification service with log/no-op fallback.
- Delivered approval/status transition triggers a notification.
- Notification text does not include document contents or filenames.

Issue 8 — Observability completion: **Completed**
- Added request ID middleware and `x-request-id` response header.
- Added structured request logs without bodies, secrets, or document contents.
- Added frontend Sentry init guarded by `VITE_SENTRY_DSN`.
- Added `@sentry/react`.

Issue 9 — Data retention & privacy: **Completed**
- Added retention service.
- Added env-configured purge windows for public intakes and matter file refs.
- Added tests for old PII/file-ref deletion and fresh data preservation.
- Updated security/API docs.

## Verification Run

Final local verification:

```text
/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q
51 passed, 3 warnings

cd frontend && npm ci && npm run build
passed

git diff --check
passed
```

Browser/computer-use verification:
- `http://127.0.0.1:5173/attorney` rendered the attorney delivery queue, `/attorney` navigation, one demo queue row, and no console errors.
- `http://127.0.0.1:5173/portal` rendered the upload panel, five-stage tracker, pending downloads disabled, delivered download enabled, and no console errors.

## Remaining External Blockers

- Branch protection for `main` requires owner/GitHub plan settings.
- Real Sentry DSNs need to be created and set in deployment env.
- Real email provider needs verified sender/domain and secret.
- Real Anthropic integration needs reviewed prompt/client path and GCS document retrieval.
- Live GCS deletion for retention needs production credentials and bucket policy.

## Next Best Batch

Generate Batch 05 around:
- Wiring AI prep to consume playbook checks.
- Full attorney review surface for issue-by-issue review, approve/dismiss, and reasoning capture.
- Feedback loop that updates playbook accuracy counters from attorney corrections.
- Real provider wiring once owner supplies accounts/secrets.

## Message Back To Claude

Claude, Batch 04 is complete except the GitHub branch-protection settings blocker. Codex implemented and pushed the abuse hardening, attorney workspace, customer portal completion, internal AI prep, playbook model, notifications, observability, and retention controls on `feat/batch-04`. The final local suite is green: 51 backend tests pass, frontend build passes, and `git diff --check` passes. The browser verified `/attorney` and `/portal`. Review the PR, keep the external blockers explicit, and continue with Batch 05 focused on playbook-driven AI prep plus attorney feedback loops.
