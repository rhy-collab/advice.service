# Batch 02 Progress Log

## Issue 1 — Restore trustworthy backend CI/package baseline

**Status:** Completed

**What changed**
- Added backend build-system metadata.
- Changed backend Python support from `>=3.14` to `>=3.12`.
- Added explicit setuptools package discovery for `app*`.
- Refreshed `backend/uv.lock`.
- Ignored editable-install `*.egg-info/` output.

**Tests/commands run**
- `/opt/homebrew/bin/python3.12 -m venv /tmp/charter-law-backend-ci-venv`
- `/tmp/charter-law-backend-ci-venv/bin/python -m pip install --upgrade pip`
- `/tmp/charter-law-backend-ci-venv/bin/python -m pip install -e . pytest email-validator`
- `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q`
- `cd frontend && npm ci && npm run build`
- `git diff --check`

**Result**
- Clean backend install succeeded.
- Backend tests passed before this batch expansion: `16 passed`.
- Frontend build passed.
- `git diff --check` passed.

**Remaining work**
- Push and let GitHub Actions prove the same remotely.

**Security/compliance notes**
- No auth, approval, org-scope, or storage behavior changed.

## Issue 2 — Free Contract Mistake Checker backend

**Status:** Completed

**What changed**
- Added `DocumentChecker` service that validates `.docx`, extracts text from `word/document.xml`, and returns a short preparation report.
- Added `POST /v1/public/check-contract`.
- Added response schemas with `stored: false`.
- Added tests for report generation, non-`.docx` rejection, and the public endpoint.
- Added `python-multipart` for upload parsing.

**Tests/commands run**
- `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q`

**Result**
- Backend tests passed after checker and intake work: `21 passed`.

**Remaining work**
- Later: replace deterministic checks with Anthropic-assisted checking if desired, while preserving no-storage behavior.

**Security/compliance notes**
- Checker does not create a matter, intake row, GCS object, or file artifact. The response states it is not legal advice.

## Issue 3 — Free Contract Mistake Checker frontend

**Status:** Completed

**What changed**
- Added `frontend/src/lib/publicApi.ts`.
- Added public checker UI on the landing page.
- Added privacy promise: "We never save or store your contract."
- Added report display grouped by findings, with backend/demo source and CTA to paid review.

**Tests/commands run**
- `cd frontend && npm run build`
- `cd frontend && npm ci && npm run build`

**Result**
- Frontend build passed.

**Remaining work**
- Browser QA/polish against a live dev server would be useful before public launch.

**Security/compliance notes**
- UI copy says preparation-only and no storage. Contract content is not persisted in frontend beyond the current selected file/report state.

## Issue 4 — Public intake API

**Status:** Completed

**What changed**
- Added `PublicIntakeModel` and Alembic migration `20260701_0004_create_public_intakes.py`.
- Added `IntakeService`.
- Added `POST /v1/public/intake`.
- Added tests for persistence and request validation.

**Tests/commands run**
- `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q`

**Result**
- Backend tests passed: `21 passed`.

**Remaining work**
- Add email notification/CRM routing later.

**Security/compliance notes**
- Public intake is a lead record, not a matter and not legal advice. It does not create deliverables.

## Issue 5 — Public intake frontend

**Status:** Completed

**What changed**
- Replaced the mailto-only landing CTA with a structured intake form.
- Added fields for name, email, company, contract type, urgency, tier, and notes.
- Added API/demo submission handling and a confirmation reference.
- Added truthful copy that scope/payment/reviewing-attorney path happen before legal work begins.

**Tests/commands run**
- `cd frontend && npm run build`
- `cd frontend && npm ci && npm run build`

**Result**
- Frontend build passed.

**Remaining work**
- Browser QA/polish and email routing.

**Security/compliance notes**
- Copy does not promise legal advice or attorney-client relationship on submit.

## Issue 6 — Environment and command documentation

**Status:** Completed

**What changed**
- Updated `build-system/CLAUDE.md` with exact backend install/test, frontend dev/build, and diff-check commands.
- Added `DECISIONS.md` entry for the Python 3.12 baseline and public lead-gen slice.

**Tests/commands run**
- `git diff --check`

**Result**
- Diff check passed.

**Remaining work**
- Fill deploy preview command once Cloud Run/Vercel/hosting is configured.

**Security/compliance notes**
- Docs explicitly keep demo auth as local opt-in only.

## Issue 7 — API contract update for public endpoints

**Status:** Completed

**What changed**
- Documented `POST /v1/public/check-contract`.
- Documented `POST /v1/public/intake`.
- Added request/response examples and privacy/compliance notes.

**Tests/commands run**
- `git diff --check`

**Result**
- Diff check passed.

**Remaining work**
- Keep docs in sync if endpoint shapes change.

**Security/compliance notes**
- Contract docs say the checker is preparation-only and stores nothing.

## Issue 8 — CI workflow covers frontend build

**Status:** Completed

**What changed**
- Added `frontend-build` GitHub Actions job using Node 20, `npm ci`, and `npm run build`.
- Updated backend CI install to include `httpx`, matching endpoint tests.

**Tests/commands run**
- `cd frontend && npm ci && npm run build`
- `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q`
- `git diff --check`

**Result**
- Frontend clean build passed.
- Backend tests passed.
- Diff check passed.

**Remaining work**
- Push and confirm GitHub Actions goes green remotely.

**Security/compliance notes**
- CI jobs require no secrets.

## Issue 9 — Batch handoff and completion audit

**Status:** Completed

**What changed**
- Batch file and progress log created.
- Handoff file written at `build-system/generated-issues/codex-goal-handoff-after-batch-02.md`.

**Tests/commands run**
- `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q`
- `cd frontend && npm ci && npm run build`
- `git diff --check`

**Result**
- All verification passed locally, and the handoff captures the next `/goal` prompt.

**Remaining work**
- Push and confirm GitHub Actions goes green remotely.

**Security/compliance notes**
- No secrets or tokens should be included in handoff.
