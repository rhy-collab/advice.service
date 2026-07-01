# Batch 05 — The Next Nine Issues (the moat)

*Generated 1 July 2026 from the roadmap + current `main` (`bdf55bb`). Dependency-ordered. Goal: turn the internal AI-prep skeleton into the real, playbook-driven, attorney-in-the-loop engine that is Charter Law's moat. Status: ⬜ Not started · 🟨 In progress · ✅ Completed · ⛔ Blocked.*

**Baseline (do not regress):** 51 tests pass; attorney-only approval + AI-prep; internal-only AI; org isolation; fail-closed auth; signed-only file URLs; free checker stores nothing; Python ≥3.12 packaging.

---

## Issue 1 — Retention: delete the actual storage objects ✅
**Objective:** Make retention/deletion remove the real GCS objects, not just DB file references.
**Why:** Today retention deletes `matter_files` rows but leaves confidential documents in the bucket — orphaned confidential material. (From the Batch 04 review.)
**Scope:** Add `StorageService.delete_object(bucket, object)` (real delete when creds present, no-op stub otherwise); have `RetentionService.purge_expired` delete each object before removing its row; add an admin/scheduled trigger to run the purge.
**Acceptance:** Purge removes storage objects then rows; free checker still stores nothing; tests cover the delete path via a fake storage.
**Current status:** Retention calls `StorageService.delete_object` before deleting expired matter-file rows, reports object deletions, and exposes an attorney/admin purge endpoint at `/v1/attorney/retention/purge`.
**Verification:** `pytest -q`.
**Security/compliance:** True deletion of confidential material. **Files:** `app/services/storage_service.py`, `app/services/retention.py`, trigger, tests. **Depends on:** —. **Done means:** deletion is real end-to-end.

## Issue 2 — Playbook-driven AI prep ✅
**Objective:** The AI prep engine generates its issue list from the matter's contract-type **playbook checks**, not generic prompts.
**Why:** The playbook is the accuracy moat; AI must run against it.
**Scope:** Resolve the playbook for the contract type; for each check produce a structured finding (which check fired, severity, confidence); store findings linked to their check id.
**Acceptance:** AI prep issues reference specific playbook checks; internal-only; tests with a seeded playbook.
**Current status:** Matters now persist `contract_type`; upload completion resolves matching playbook checks; generated AI prep issues store `playbook_check_id` and `playbook_check_key` while preserving the no-playbook fallback.
**Verification:** `pytest -q`.
**Security/compliance:** Internal-only preserved. **Files:** `app/services/ai_prep_service.py`, `app/services/playbook_service.py`, `app/models/*`, migration, tests. **Depends on:** —. **Done means:** AI prep is playbook-grounded.

## Issue 3 — Attorney feedback loop ✅
**Objective:** Attorney corrections permanently improve the playbook.
**Why:** The compounding moat — every review makes the next better.
**Scope:** When an attorney dismisses/edits an AI issue, capture a reason tag; update the relevant playbook check (fallback language / severity / detection); track per-check accuracy over time.
**Acceptance:** A correction updates the linked check and its accuracy stat; tested.
**Current status:** Attorney feedback is stored durably, linked playbook checks update accuracy counters, and edit feedback can replace fallback language for the check.
**Verification:** `pytest -q`.
**Security/compliance:** Attorney-role only. **Files:** `app/routers/attorney.py`, `app/services/playbook_service.py`, `app/services/matter_service.py`, migration, tests. **Depends on:** 2. **Done means:** corrections compound into the playbook.

## Issue 4 — Over-inclusive redline + cover-letter deliverable ✅
**Objective:** Generate an internal-only first-pass redline + the "what changed / why risky / your fallback" cover letter.
**Why:** The cover letter is the heart of the standard tier; the redline is the core work product.
**Scope:** Produce a tracked-changes redline via a Word-add-in boundary (stub the add-in call, real path behind config); generate the cover letter from the issue list; tune for recall (over-inclusive). Internal-only until approval.
**Acceptance:** Redline + cover letter generated and stored internally; never customer-visible pre-approval; tested.
**Current status:** Upload completion now creates an internal-only draft deliverable record with a stubbed redline object path and cover-letter body generated from the issue list; client download still requires attorney-approved delivery.
**Verification:** `pytest -q`.
**Security/compliance:** Internal-only enforced server-side. **Files:** `app/services/ai_prep_service.py`, redline boundary module, schema, migration, tests. **Depends on:** 2. **Done means:** the full internal work product exists.

## Issue 5 — Confidence scoring + risk-score routing ✅
**Objective:** Surface per-issue confidence to the attorney and route matters by overall risk score.
**Why:** Attorneys should look where the AI is unsure; low-risk matters fast-track, high-risk escalate.
**Scope:** Ensure every issue carries strong/medium/weak; compute a matter risk score from checks; route on it (fast-track vs escalate); expose confidence in the attorney AI-prep view.
**Acceptance:** Risk score computed + used for routing; confidence visible to attorney; tested.
**Current status:** AI-prep confidence is exposed in the attorney response; matter summaries now carry `risk_score` and `risk_route`; upload completion computes the route from severity plus confidence.
**Verification:** `pytest -q`.
**Security/compliance:** none new. **Files:** `app/services/*`, `app/routers/attorney.py`, tests. **Depends on:** 2. **Done means:** confidence + routing drive attorney attention.

## Issue 6 — Real Anthropic integration (internal-only, behind key) ✅
**Objective:** Replace the AI-prep placeholder with a real Claude call for the summary + issues.
**Why:** Move from stub to actual AI preparation.
**Scope:** Wire the Anthropic client behind `ANTHROPIC_API_KEY`; keep the deterministic stub fallback when unset; enforce a no-training data posture; results remain internal-only. Document the exact key/setup step in `BLOCKERS.md`.
**Acceptance:** With a key, real output is produced and stored internally; without a key, the stub still works; tests use the stub.
**Current status:** `ANTHROPIC_API_KEY` now switches AI prep onto the Anthropic Messages API path, with deterministic fallback when unset; setup is documented in `.env.example` and `BLOCKERS.md`.
**Verification:** `pytest -q`.
**Security/compliance:** Internal-only; no document content logged; confirm no-training posture. **Files:** `app/services/ai_prep_service.py`, `.env.example`, `BLOCKERS.md`, tests. **Depends on:** 2. **Done means:** real AI prep is available when keyed. *(Live key is a human step.)*

## Issue 7 — Attorney workbench v2 (review surface) ✅
**Objective:** A real review surface: list AI issues with Apply/Dismiss + reasoning + confidence flags; capture attorney-minutes (HuRT).
**Why:** The attorney's cockpit; HuRT is the margin metric.
**Scope:** Attorney UI showing the AI prep (summary/issues/redline link) with per-issue Apply/Dismiss + reason; highlight weak-confidence items; record review minutes per matter; approve from here.
**Acceptance:** Attorney can review, action issues (feeding Issue 3), and approve; HuRT recorded; UI builds.
**Current status:** `/attorney` now renders a dedicated workbench with queue selection, AI-prep issues, Apply/Dismiss/Edit feedback, risk/confidence highlighting, review-minutes capture, and approval.
**Verification:** `pytest -q`; `npm run build`.
**Security/compliance:** Attorney-role only. **Files:** `frontend`/`attorney-app`, `app/routers/attorney.py`, tests. **Depends on:** 3, 5. **Done means:** the attorney works entirely in-app.

## Issue 8 — Playbook authoring UI + per-client overlay ✅
**Objective:** A screen to define/edit playbook checks, plus per-client overlays on a firm-wide base.
**Why:** You/the attorney must be able to shape the moat without code.
**Scope:** CRUD UI for checks (detection, severity, fallback language); per-org overlay that resolves over the base at review time.
**Acceptance:** Checks editable in-app; per-client overrides apply; tested.
**Current status:** Attorney-only playbook APIs now support organisation overlays, check creation, and check edits; the workbench includes a playbook authoring panel for overlays and checks.
**Verification:** `pytest -q`; `npm run build`.
**Security/compliance:** Attorney/admin only. **Files:** `app/services/playbook_service.py`, `app/routers/*`, `frontend`, tests. **Depends on:** 2. **Done means:** the playbook is editable and layered.

## Issue 9 — End-to-end tests + CI required checks ⬜
**Objective:** Automated end-to-end coverage of the customer and attorney happy paths, and CI enforced as required.
**Why:** Confidence to keep shipping fast without breaking the flow.
**Scope:** Playwright (or equivalent) E2E for upload→status→download and attorney queue→review→approve; ensure CI runs them; confirm branch protection requires the checks.
**Acceptance:** E2E green in CI; protection requires CI.
**Verification:** `pytest -q`; E2E run; `npm run build`.
**Security/compliance:** none. **Files:** `frontend/e2e/*`, `.github/workflows/ci.yml`, tests. **Depends on:** 7. **Done means:** the core journeys are protected by automated tests. *(Branch-protection toggle is a human/GitHub-settings step.)*

---

## Recommended order
1 (independent, fixes the retention gap) → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9. Issues 1 and 8 can be done any time; 2 unlocks most of the rest.
