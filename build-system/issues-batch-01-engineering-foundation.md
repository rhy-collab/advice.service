# Issues — Batch 01: Engineering Foundation

*The first 9 GitHub issues. This is the buildable starting line: the repo, the backend, the database, auth, both frontends, tests, and a preview deploy — the skeleton everything else is built on. Each issue is atomic and dependency-ordered. Post them into the `Charter-Law` repo (once it exists) using the build-task template, or paste them straight in.*

**Milestone:** Engineering Foundation
**Build order:** #1 → #2 → #3 → #4 → #5 → (#6 and #7 in parallel) → #8 → #9
**Stack reminder:** Vite + React + TS · FastAPI (`uv`, Alembic + SQLAlchemy) · Postgres on Cloud SQL · Clerk (org-based) · Cloud Run · Sentry. The one rule: *AI prepares; an attorney approves and owns.*

---

## Issue 1 — Create the repository and base structure

**Goal:** A clean monorepo exists with the agreed folder layout and the build-system files in place, so every later issue has a home.

**Context:** Repo lives under the `Charter-Law` GitHub org. Layout per `charter-law-tech-stack.md` (frontend/, attorney-app/, backend/). Copy the contents of `build-system/` (CLAUDE.md, DECISIONS.md, `.github/` templates) into the repo root.

**Acceptance criteria:**
- [ ] Repo created under `Charter-Law`, private, with a README describing the project in one paragraph.
- [ ] Top-level folders: `backend/`, `frontend/` (customer portal), `attorney-app/`, `docs/`.
- [ ] `CLAUDE.md`, `DECISIONS.md`, and `.github/` issue + PR templates copied into the repo root.
- [ ] A `.gitignore` that excludes secrets, `.env` files, build artefacts, and virtualenvs.
- [ ] The planning docs (roadmap, super-prompt, tech-stack) copied into `docs/` so the AI can read them in-repo.

**Out of scope:** Any application code. This issue is structure only.

**Verification:** Clone the repo fresh; confirm the folders, templates, and `.gitignore` are present and no secrets are tracked.

**Compliance/security:** `.gitignore` must exclude all secrets and `.env` files.

---

## Issue 2 — Backend skeleton (FastAPI + uv)

**Goal:** A minimal FastAPI backend runs locally and returns a health check, with configuration read from environment variables.

**Context:** Python managed with `uv`. Thin routes + service layer convention. Secrets via env vars only.

**Acceptance criteria:**
- [ ] FastAPI app in `backend/` started with `uv`, with a documented run command.
- [ ] `GET /health` returns `{ "status": "ok" }` and a version string.
- [ ] Configuration (DB URL, Clerk keys, etc.) loaded from environment variables, with a committed `.env.example` listing the names (no values).
- [ ] Basic structured logging set up.
- [ ] The run/test commands added to `CLAUDE.md` under Commands.

**Out of scope:** Database, auth, business logic.

**Verification:** Run the documented command; hit `/health`; confirm `200 OK` with the expected body.

**Compliance/security:** No secrets in code; `.env.example` holds names only.

---

## Issue 3 — Database connection + migrations baseline

**Goal:** The backend connects to PostgreSQL, with SQLAlchemy and Alembic set up and an empty baseline migration that applies cleanly.

**Context:** Postgres on Google Cloud SQL (a local Postgres is fine for development). Every schema change from here on gets an Alembic migration — never hand-edited.

**Acceptance criteria:**
- [ ] SQLAlchemy configured against the env-var DB URL.
- [ ] Alembic initialised; a baseline migration runs up and down without error.
- [ ] A documented command to run migrations, added to `CLAUDE.md`.
- [ ] A separate throwaway **test database** configuration that tests use.

**Out of scope:** Actual tables (next issue).

**Verification:** Run the migration command against a clean database; confirm it applies and rolls back cleanly.

**Compliance/security:** Test DB is fully separate; no real data anywhere near tests.

**Depends on:** #2.

---

## Issue 4 — Core data model (orgs, users, matters, files, audit)

**Goal:** The central tables exist, including the matter lifecycle and an audit/events table, via Alembic migrations.

**Context:** This is the spine of the system. The matter lifecycle is `intake → ai_review → attorney_queue → attorney_review → delivered → completed`. The `delivered` transition will later require recorded attorney approval — model it so that's enforceable.

**Acceptance criteria:**
- [ ] Tables: `organisations`, `users` (linked to org), `matters`, `files`, `events` (audit).
- [ ] `matters` has a status field constrained to the six lifecycle states, plus timestamps and the owning org.
- [ ] `files` stores a reference/key (the actual file will live in Cloud Storage), never file bytes in the DB.
- [ ] `events` records actor, action, target, and timestamp — enough to audit uploads, AI runs, and approvals.
- [ ] All created via Alembic migrations; up and down both work.

**Out of scope:** Cloud Storage upload itself; AI; the approval-enforcement logic (later phase). Just the schema.

**Verification:** Apply migrations; inspect the tables; insert a sample org → user → matter and confirm the status constraint rejects an invalid value.

**Compliance/security:** Audit table present from day one; file bytes never stored in the DB.

**Depends on:** #3.

---

## Issue 5 — Clerk org-based auth on the backend

**Goal:** Every backend request can verify a Clerk session and is scoped to the requesting organisation; a protected test endpoint proves it.

**Context:** Clerk, organisation-based. The non-negotiable security baseline: verify the session **server-side on every request**, and a user only ever sees their own org's data.

**Acceptance criteria:**
- [ ] Middleware/dependency that verifies the Clerk session on protected routes and rejects invalid/absent sessions with `401`.
- [ ] The verified user's organisation is available to handlers and used to scope queries.
- [ ] `GET /me` returns the current user + org for a valid session; `401` otherwise.
- [ ] A test proving a user cannot access another organisation's data.

**Out of scope:** Frontends; full matter endpoints.

**Verification:** Call `/me` with a valid Clerk token (200) and without one (401); run the cross-org isolation test (passes).

**Compliance/security:** This issue **is** the data-isolation guarantee. Flag for the one-off security review later.

**Depends on:** #4.

---

## Issue 6 — Customer portal skeleton (Vite + React + TS)

**Goal:** The customer web app runs, lets a user log in via Clerk, and successfully calls the protected `/me` endpoint.

**Context:** Vite + React + TypeScript, feature-organised. Clerk org-based login.

**Acceptance criteria:**
- [ ] App in `frontend/` runs with a documented dev command.
- [ ] Clerk login/sign-up works; logged-out users see a sign-in screen.
- [ ] After login, the app calls `/me` and displays the user + org name.
- [ ] Run command added to `CLAUDE.md`.

**Out of scope:** Upload, payments, status tracker (later phases). Skeleton only.

**Verification:** Start the dev server; sign up; confirm the dashboard shows your name and org pulled from the backend.

**Compliance/security:** No customer data displayed beyond the logged-in user's own org.

**Depends on:** #5.

---

## Issue 7 — Attorney app skeleton (separate Vite + React + TS app)

**Goal:** A separate internal attorney web app runs and logs in via Clerk, ready to become the review workbench later.

**Context:** Mirrors General Legal's separate `lawyers.` app. Same stack, separate app in `attorney-app/`. Internal users only.

**Acceptance criteria:**
- [ ] App in `attorney-app/` runs with a documented dev command.
- [ ] Clerk login works and is restricted to internal/attorney users.
- [ ] After login, shows a placeholder "Matter queue" screen calling `/me`.
- [ ] Run command added to `CLAUDE.md`.

**Out of scope:** The review surface, approve gate, confidence flags (Phase 4). Skeleton only.

**Verification:** Start the dev server; log in as an internal user; confirm the placeholder queue loads.

**Compliance/security:** Attorney app access restricted to internal users, not customers.

**Depends on:** #5. *(Can be built in parallel with #6.)*

---

## Issue 8 — CI, tests, and branch protection

**Goal:** Automated checks run on every pull request — tests against the throwaway test DB, plus lint/format — and merging is blocked unless they pass.

**Context:** This is what lets you trust merges without reading the code yourself. Pairs with the code-review plugin.

**Acceptance criteria:**
- [ ] CI runs backend tests against the test DB on every pull request.
- [ ] CI runs frontend lint/format/build checks on every pull request.
- [ ] A starter test suite exists (health endpoint, `/me` auth, cross-org isolation from #5).
- [ ] Branch protection on `main`: CI must pass and one approval required before merge.
- [ ] An auto-format step so style is consistent without manual effort.

**Out of scope:** Full coverage; end-to-end browser tests (added with the portal in Phase 3).

**Verification:** Open a test pull request that breaks a test; confirm CI fails and merge is blocked; fix it; confirm it passes and can merge.

**Compliance/security:** Tests never touch real data; the isolation test from #5 runs in CI.

**Depends on:** #5.

---

## Issue 9 — Containerise and deploy a preview to Cloud Run

**Goal:** The backend and both frontends build into containers and deploy to a Cloud Run preview environment, with Sentry capturing errors.

**Context:** Google Cloud Run (scales to zero, cheap when idle). Sentry on every surface. This gives you clickable preview deploys to test each future change before it goes live.

**Acceptance criteria:**
- [ ] Dockerfiles for backend, customer portal, and attorney app.
- [ ] A documented deploy producing a working Cloud Run preview URL for each surface.
- [ ] The deployed backend connects to a managed Postgres (Cloud SQL) instance.
- [ ] Sentry wired into all three surfaces, capturing a test error.
- [ ] Secrets supplied via Cloud Run environment configuration, never baked into images.

**Out of scope:** Custom domain, production hardening, autoscaling tuning (later).

**Verification:** Open each preview URL; log in; trigger a deliberate test error and confirm it appears in Sentry.

**Compliance/security:** Secrets via environment config only; not in images or git. This deployed environment is **not** for real client documents until the one-off security review passes.

**Depends on:** #6, #7, #8.

---

## When all 9 are done
The foundation is live: a secure, org-isolated, tested, deployable app skeleton with both frontends and an audit trail. The next batch (Batch 02) would be **Phase 2 — the Webflow marketing site + intake + the free Contract Mistake Checker**, then Batch 03 the customer portal features (upload, status tracker, billing). Ask me to generate the next batch when you're ready.
