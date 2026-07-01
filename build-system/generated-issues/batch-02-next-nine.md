# Batch 02 — Next Nine Issues Toward Production Readiness

Generated from the current repo state, `charter-law-roadmap.md`, and `build-system/issues-backlog-batches-02-07.md`.

Status key: Not started · In progress · Completed · Blocked

## Issue 1 — Restore trustworthy backend CI/package baseline

**Status:** Completed

### Objective
Make the backend installable and testable in the same Python version CI uses.

### Why it matters
Every later issue depends on reliable tests. A broken install path makes CI decorative rather than protective.

### Scope
- Align backend Python support with CI.
- Add explicit package discovery.
- Refresh lock metadata.
- Ignore editable-install metadata.

### Acceptance criteria
- `pip install -e . pytest email-validator` succeeds in Python 3.12.
- `pytest -q` passes.
- CI and `pyproject.toml` both support Python 3.12.
- No security/compliance behavior is weakened.

### Verification commands
- `/opt/homebrew/bin/python3.12 -m venv /tmp/charter-law-backend-ci-venv`
- `/tmp/charter-law-backend-ci-venv/bin/python -m pip install -e . pytest email-validator`
- `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q`

### Security/compliance check
No auth, approval, storage, or org-scoping code changes.

### Files likely to change
- `.gitignore`
- `backend/pyproject.toml`
- `backend/uv.lock`

### Dependencies
None.

### Done means
The backend baseline is green from a clean Python 3.12 environment.

## Issue 2 — Free Contract Mistake Checker backend

**Status:** Completed

### Objective
Add a public, no-login backend endpoint that accepts a `.docx`, inspects it in memory, and returns a short report.

### Why it matters
This is the lead magnet in Phase 2 and gives the public site a useful conversion tool without requiring accounts.

### Scope
- Add a document-checking service.
- Add a public API endpoint isolated from matter/customer data.
- Reject non-`.docx` files and oversized files.
- Persist nothing.

### Acceptance criteria
- Endpoint accepts one `.docx` upload.
- Report includes typos/style flags, broken cross-reference candidates, unused defined-term candidates, and missing standard-section candidates.
- Response includes a clear `stored: false`/equivalent signal.
- Unit tests prove `.docx` content is inspected and non-`.docx` is rejected.

### Verification commands
- `cd backend && pytest -q`
- `git diff --check`

### Security/compliance check
The uploaded file is processed in memory only. No DB row, file object, or audit matter is created.

### Files likely to change
- `backend/app/services/document_checker.py`
- `backend/app/routers/public.py`
- `backend/app/main.py`
- `backend/app/schemas/public.py`
- `backend/tests/test_document_checker.py`
- `backend/pyproject.toml`
- `backend/uv.lock`

### Dependencies
Issue 1.

### Done means
The backend exposes a tested, non-persistent checker suitable for the public landing page.

## Issue 3 — Free Contract Mistake Checker frontend

**Status:** Completed

### Objective
Add a public landing-page section/page where a visitor can upload a `.docx` and see the checker report.

### Why it matters
The roadmap calls for a public lead magnet before deeper portal automation.

### Scope
- Add a public checker UI.
- Wire it to the backend endpoint.
- Show a privacy promise: "We never save or store your contract."
- Include a CTA to the paid intake flow.

### Acceptance criteria
- Upload UI accepts `.docx`.
- Loading, success, and error states are polished.
- Results are grouped by finding type.
- The feature remains usable in demo mode if the backend is unavailable.

### Verification commands
- `cd frontend && npm run build`
- `git diff --check`

### Security/compliance check
No checked document content is stored in frontend state beyond the current session/report display.

### Files likely to change
- `frontend/src/features/landing/LandingPage.tsx`
- `frontend/src/lib/publicApi.ts`
- `frontend/src/styles.css`

### Dependencies
Issue 2.

### Done means
A visitor can use the checker from the public site in a local build.

## Issue 4 — Public intake API

**Status:** Completed

### Objective
Add a pre-login intake endpoint for early manual MVP leads.

### Why it matters
The roadmap requires strangers to submit contract-review interest before the full customer portal is complete.

### Scope
- Accept contact, company, contract type, urgency, tier, and notes.
- Create a lead/intake record separate from authenticated matters.
- Return a confirmation reference.
- Keep uploads out of scope unless storage is explicitly safe.

### Acceptance criteria
- Public intake request validates required fields.
- Intake is persisted in a dedicated table.
- Tests cover creation and validation.

### Verification commands
- `cd backend && pytest -q`
- `git diff --check`

### Security/compliance check
The intake endpoint must not expose customer matter data and must not create attorney-approved deliverables.

### Files likely to change
- `backend/app/models/intake.py`
- `backend/app/schemas/public.py`
- `backend/app/routers/public.py`
- `backend/app/services/intake_service.py`
- `backend/alembic/versions/*`
- `backend/tests/test_public_intake.py`

### Dependencies
Issue 1.

### Done means
The public site can capture qualified leads without requiring Clerk login.

## Issue 5 — Public intake frontend

**Status:** Completed

### Objective
Replace the mailto-only landing-page CTA with a real intake form.

### Why it matters
A visitor should be able to express interest and give enough information for follow-up.

### Scope
- Add fields for name, email, company, contract type, urgency, tier, and notes.
- Submit to the public intake endpoint.
- Show confirmation reference and expectation-setting copy.

### Acceptance criteria
- Form validates required fields.
- Success and failure states are clear.
- CTA remains truthful: Charter Law is operations/AI-prep plus reviewing attorney, not "our lawyers."

### Verification commands
- `cd frontend && npm run build`
- `git diff --check`

### Security/compliance check
No promise of legal advice or attorney-client relationship before attorney engagement.

### Files likely to change
- `frontend/src/features/landing/LandingPage.tsx`
- `frontend/src/lib/publicApi.ts`
- `frontend/src/styles.css`

### Dependencies
Issue 4.

### Done means
The landing page captures structured intake leads.

## Issue 6 — Environment and command documentation

**Status:** Completed

### Objective
Replace TBD command placeholders and document the local/dev verification path.

### Why it matters
Future agents and GitHub issue loops need exact commands, not rediscovery.

### Scope
- Update `build-system/CLAUDE.md` commands.
- Document backend install/test, frontend build/dev, and demo auth behavior.
- Record the CI/package decision.

### Acceptance criteria
- Commands are exact and tested.
- `DECISIONS.md` has a short entry for the Python 3.12/package baseline.

### Verification commands
- `git diff --check`

### Security/compliance check
Docs must state demo auth is local opt-in only.

### Files likely to change
- `build-system/CLAUDE.md`
- `build-system/DECISIONS.md`

### Dependencies
Issue 1.

### Done means
The next agent can run the project without guessing.

## Issue 7 — API contract update for public endpoints

**Status:** Completed

### Objective
Document the public checker/intake API contracts.

### Why it matters
Frontend/backend work stays aligned and future agents do not need to infer payload shapes.

### Scope
- Add endpoint docs for `/v1/public/check-contract` and `/v1/public/intake`.
- Include request/response examples.
- Include persistence/privacy notes.

### Acceptance criteria
- Contract docs match implemented schemas.
- Privacy notes explicitly state checker uploads are not stored.

### Verification commands
- `git diff --check`

### Security/compliance check
Contract docs do not suggest legal advice is being provided by AI.

### Files likely to change
- `frontend/API_CONTRACT.md`
- possibly `README.md`

### Dependencies
Issues 2 and 4.

### Done means
Public API behavior is documented.

## Issue 8 — CI workflow covers frontend build

**Status:** Completed

### Objective
Extend CI beyond backend tests to include the Vite/TypeScript frontend build.

### Why it matters
Frontend regressions should be caught automatically before merge.

### Scope
- Add a frontend-build job to GitHub Actions.
- Use `npm ci` and `npm run build`.
- Keep backend job intact.

### Acceptance criteria
- CI defines backend and frontend jobs.
- Local equivalent commands pass.

### Verification commands
- `cd frontend && npm ci && npm run build`
- `git diff --check`

### Security/compliance check
No secrets are required for build.

### Files likely to change
- `.github/workflows/ci.yml`

### Dependencies
Issue 1.

### Done means
CI protects both app halves.

## Issue 9 — Batch handoff and completion audit

**Status:** Completed

### Objective
Keep a clear progress log and write the next Codex `/goal` handoff.

### Why it matters
The user wants the nine-issue loop to compound across agents without rediscovery.

### Scope
- Update `batch-02-progress.md`.
- Add `codex-goal-handoff-after-batch-02.md`.
- Include exact commands and remaining blockers.

### Acceptance criteria
- Progress file lists all nine statuses.
- Handoff is ready to paste into Codex `/goal`.
- Final audit does not mark incomplete items complete.

### Verification commands
- `git diff --check`

### Security/compliance check
No secrets or tokens in handoff.

### Files likely to change
- `build-system/generated-issues/batch-02-progress.md`
- `build-system/generated-issues/codex-goal-handoff-after-batch-02.md`

### Dependencies
All prior issues, or honest status if some remain incomplete.

### Done means
The next agent can continue from exact evidence.
