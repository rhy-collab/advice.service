# Batch 04 — The Next Nine Issues

*Generated 1 July 2026 from the roadmap + current `main` (`c11f381`). Dependency-ordered. Goal: move from "hardened foundation + lead-gen" toward the attorney-in-the-loop product and the AI engine. Status: ⬜ Not started · 🟨 In progress · ✅ Completed · ⛔ Blocked.*

**Baseline (do not regress):** 32 tests pass; Python ≥3.12 packaging; demo auth off by default; attorney-role approval gate; guarded lifecycle transitions; signed-only file URLs; org-scoped access; the free checker stores nothing; prod config fails closed.

---

## Issue 1 — Confirm remote CI green + branch protection ⛔/🟨
**Objective:** Prove GitHub Actions is green on `main` and make it a required check before merge.
**Why:** Trust in the green baseline must be remote, not just local.
**Scope:** Verify the Actions run on `main`; enable branch protection requiring the CI check + 1 review.
**Acceptance:** CI green on `main`; protection rule active.
**Verification:** GitHub Actions tab; repo settings.
**Security/compliance:** none. **Files:** none (settings). **Depends on:** —. **Done means:** merges are gated on green CI. *(Branch-protection toggle is a human/GitHub-settings step.)*

## Issue 2 — Public-endpoint hardening ⬜
**Objective:** Protect `/v1/public/check-contract` and `/v1/public/intake` from abuse.
**Why:** They're unauthenticated; today there's no rate-limit and the checker reads the whole upload before the size check.
**Scope:** Per-IP rate limiting; enforce a max request/body size at the edge (reject before full read); basic input validation on intake; keep the "no storage" guarantee.
**Acceptance:** Oversized/too-frequent requests are rejected (413/429) before heavy work; tests cover it.
**Verification:** `pytest -q`.
**Security/compliance:** No file persistence; no PII leakage. **Files:** `app/routers/public.py`, `app/services/document_checker.py`, new middleware, tests. **Depends on:** —. **Done means:** the public surface is abuse-resistant.

## Issue 3 — Attorney workspace v1 ⬜
**Objective:** An attorney-only queue + minimal attorney UI; move approval fully into the attorney surface.
**Why:** Closes the review gap — approval should not live in the customer API.
**Scope:** `GET /v1/attorney/queue` (attorney/admin only: matters in `attorney_queue`/`attorney_review`); a minimal attorney page listing the queue with an Approve action; keep `require_attorney_context`; consider firm-vs-client org scoping.
**Acceptance:** Non-attorneys get 403; attorneys see the queue; approve moves to `delivered`.
**Verification:** `pytest -q`; `npm run build`.
**Security/compliance:** Attorney-role enforced; org/firm scoping. **Files:** `app/routers/attorney.py`, `frontend` or `attorney-app`, tests. **Depends on:** 1. **Done means:** attorneys action their queue in a dedicated surface.

## Issue 4 — Customer portal completion ⬜
**Objective:** Wire upload → status tracker → download end-to-end against the backend.
**Why:** The portal has pages; the full happy path must work for a real customer.
**Scope:** Upload to a signed URL, create matter; show the 5-stage status tracker; enable download only when `delivered`.
**Acceptance:** A customer can upload, watch status, and download an approved deliverable; org-scoped.
**Verification:** `npm run build`; backend `pytest -q`; manual click-test on preview.
**Security/compliance:** No draft downloadable before approval; org isolation. **Files:** `frontend/src/*`, `app/routers/matters.py` (if needed), tests. **Depends on:** 3. **Done means:** the customer happy path is complete.

## Issue 5 — AI prep engine v1 (internal-only) ⬜
**Objective:** On upload, generate an **internal-only** plain-English summary + issue list; gate it from customers.
**Why:** The first real "AI prepares" step.
**Scope:** Document ingestion (reuse the checker's .docx extraction); call Anthropic behind an env key with a deterministic stub fallback when unset; store results against the matter; move `intake → ai_review → attorney_queue`; never expose to customers.
**Acceptance:** Summary + issue list produced and stored internally; not visible via any customer endpoint; transitions recorded.
**Verification:** `pytest -q` (with the stub).
**Security/compliance:** Internal-only enforced server-side; no legal advice to customers. **Files:** `app/services/ai_engine.py`, `app/routers/matters.py`, migration, tests. **Depends on:** 3. **Done means:** AI prep runs and stays internal until approval.

## Issue 6 — Playbook data model v1 ⬜
**Objective:** A structured risk/clause library in Postgres (not free-text prompts).
**Why:** The moat; drives accuracy and routing later.
**Scope:** Tables for playbooks + checks (detection, severity tier, remediation intent, preferred/acceptable/unacceptable fallback language, per-check accuracy); Alembic migration; basic CRUD service + tests. Seed a small NDA playbook.
**Acceptance:** Playbook + checks persist; CRUD works; migration up/down clean.
**Verification:** `pytest -q`.
**Security/compliance:** none. **Files:** `app/models/playbook.py`, `app/services/playbook_service.py`, migration, tests. **Depends on:** —. **Done means:** the playbook is a first-class, structured system.

## Issue 7 — Status-change notifications ⬜
**Objective:** Email the customer on key transitions (especially `delivered`).
**Why:** Predictability + "your review is ready."
**Scope:** A notification service behind an env-configured provider (log/no-op stub when unset); fire on transitions; org-scoped; no document contents in emails.
**Acceptance:** A `delivered` transition triggers a notification (stub logs it); tested.
**Verification:** `pytest -q`.
**Security/compliance:** No confidential content in notifications. **Files:** `app/services/notifications.py`, hook in `matter_service`, tests. **Depends on:** —. **Done means:** customers are notified on progress.

## Issue 8 — Observability completion ⬜
**Objective:** Structured request logging + request IDs (backend) and frontend Sentry init.
**Why:** You can't run a legal product blind to errors.
**Scope:** Request-ID middleware + structured logs (no secrets/documents); wire Sentry on the frontend (env-guarded like the backend).
**Acceptance:** Each request logs a correlation id; frontend Sentry initialises only when its DSN is set; tested where practical.
**Verification:** `pytest -q`; `npm run build`.
**Security/compliance:** Never log document contents or secrets. **Files:** `app/observability.py`, middleware, `frontend/src/main.tsx`, tests. **Depends on:** —. **Done means:** end-to-end observability without leaking data.

## Issue 9 — Data retention & privacy ⬜
**Objective:** Define + enforce retention/deletion for public intakes (PII) and documents.
**Why:** Confidential legal material + PII need a lifecycle, not indefinite storage.
**Scope:** A documented retention policy; a deletion path/job for old public intakes and matter files; confirm the free checker persists nothing; a privacy note surfaced in the API/docs.
**Acceptance:** A deletion routine removes data past retention; the free tool provably stores nothing; tested.
**Verification:** `pytest -q`.
**Security/compliance:** This issue *is* a privacy control. **Files:** `app/services/retention.py`, `docs/security-posture.md`, tests. **Depends on:** 6, 7. **Done means:** data has a defined, enforced lifecycle.

---

## Recommended order
2 → 3 → 4 → 5 → 6 → 7 → 8 → 9, with 1 (remote CI + branch protection) confirmed first. Issues 2, 6, 7, 8 are independent and can be done any time.
