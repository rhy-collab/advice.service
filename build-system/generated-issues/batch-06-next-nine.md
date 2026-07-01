# Batch 06 — The Next Nine Issues (real analysis + launch readiness)

*Generated 1 July 2026 from the roadmap + current `main` (`9e37df6`). Dependency-ordered. Goal: make the AI actually analyse the contract, produce real work product, and get the product launch-ready. Status: ⬜ Not started · 🟨 In progress · ✅ Completed · ⛔ Blocked.*

**Baseline (do not regress):** 61 tests + E2E pass; AI is attorney-only/internal until approval; delivery needs attorney-role approval; org isolation; fail-closed auth; signed-only file URLs; free checker stores nothing; Python ≥3.12.

---

## Issue 1 — AI prep reads the actual contract text (safely) ⬜
**Objective:** Feed the uploaded contract's extracted text into the AI prep, not just the filename + playbook.
**Why:** Today AI prep reasons from filename + playbook metadata only — it isn't analysing the document. This is the real analysis step.
**Scope:** Retrieve the stored document, extract text (reuse the checker's .docx extraction), pass it to the AI prep prompt; enforce a **no-training posture**, **redact obvious secrets**, cap input size, keep results **internal-only**; never log document contents.
**Acceptance:** With a key, AI prep reflects the actual contract; without a key the stub still works; nothing logged; tests use the stub.
**Verification:** `pytest -q`.
**Security/compliance:** Confidential text handled internally only; no-training posture confirmed; no content in logs. **Files:** `app/services/ai_prep_service.py`, ingestion helper, `.env.example`, `BLOCKERS.md`, tests. **Depends on:** —. **Done means:** the AI analyses the real document.

## Issue 2 — Real redline generation path ⬜
**Objective:** Produce a genuine tracked-changes redline (Word add-in boundary), not a placeholder.
**Why:** The redline is the core work product.
**Scope:** Implement the Word-add-in call behind config with a deterministic stub fallback; store the redline artifact reference; keep it internal until approval; over-inclusive tuning.
**Acceptance:** A redline artifact is produced/stored per matter; internal-only; tested with the stub.
**Verification:** `pytest -q`.
**Security/compliance:** Internal-only; signed URLs for any artifact. **Files:** `app/services/deliverable_service.py`, redline boundary, tests. **Depends on:** 1. **Done means:** a real redline exists per matter.

## Issue 3 — Ops dashboard (HuRT, throughput, per-check accuracy) ⬜
**Objective:** An internal dashboard of the metrics already being captured.
**Why:** Margin (attorney-minutes) and quality (per-check accuracy) must be visible to run the business.
**Scope:** Backend aggregate endpoints (org-scoped, attorney/admin) for HuRT trends, matter throughput by status, and per-check accuracy; a simple admin UI.
**Acceptance:** Dashboard shows the metrics from real data; attorney/admin only; tested.
**Verification:** `pytest -q`; `npm run build`.
**Security/compliance:** Attorney/admin only; org-scoped. **Files:** `app/routers/reports.py`, services, `frontend`, tests. **Depends on:** —. **Done means:** the business is measurable in-app.

## Issue 4 — Market-benchmark data capture ("what's market") ⬜
**Objective:** Accumulate anonymised, structured clause terms from matters to build a private benchmark set.
**Why:** A compounding data moat; powers better fallbacks + a future client benchmarking feature.
**Scope:** On each matter, capture anonymised structured terms (with consent flag) into a separate store; no client identifiers; start capture even before the feature.
**Acceptance:** Anonymised terms captured per matter; no PII/identifiers; tested.
**Verification:** `pytest -q`.
**Security/compliance:** Anonymisation + consent mandatory; no client identifiers. **Files:** `app/models/*`, `app/services/*`, migration, tests. **Depends on:** 1. **Done means:** the benchmark dataset starts accumulating safely.

## Issue 5 — Second-chair review for high-value matters ⬜
**Objective:** Optional two-attorney sign-off for high-risk/high-value matters.
**Why:** Extra assurance where it counts.
**Scope:** A toggle (per matter or by risk score) requiring a second attorney approval before `delivered`; audited.
**Acceptance:** When enabled, one approval is insufficient; two distinct attorney approvals required; tested.
**Verification:** `pytest -q`.
**Security/compliance:** Both approvals attorney-role, recorded. **Files:** `app/services/matter_service.py`, `app/routers/attorney.py`, migration, tests. **Depends on:** —. **Done means:** high-value matters can require two sign-offs.

## Issue 6 — Delivery channels: email + Slack ⬜
**Objective:** Deliver the approved work product by email (and optionally Slack), not just the portal.
**Why:** Low-friction delivery clients expect.
**Scope:** Email the deliverable link on approval (provider behind env stub); optional Slack post to a client channel (stub); no confidential content in the message body, only a secure link.
**Acceptance:** On `delivered`, a notification with a secure link is sent (stub logs it); tested.
**Verification:** `pytest -q`.
**Security/compliance:** No document content in messages; signed links only. **Files:** `app/services/notifications.py`, integration boundary, tests. **Depends on:** 2. **Done means:** delivery works beyond the portal.

## Issue 7 — Real Clerk auth wiring + role provisioning ⬜/⛔
**Objective:** Wire real Clerk org auth + attorney/admin role assignment (behind config).
**Why:** Demo auth must give way to real identity before launch.
**Scope:** Verify real Clerk sessions/roles end-to-end; provision attorney/admin roles; keep the demo path for local dev; document the exact Clerk setup in `BLOCKERS.md`.
**Acceptance:** With Clerk configured, real login + roles work; demo path still works locally; tested where possible.
**Verification:** `pytest -q`; manual with a Clerk dev instance.
**Security/compliance:** Fail-closed; roles enforced. **Files:** `app/services/auth.py`, `frontend`, `BLOCKERS.md`, tests. **Depends on:** —. **Done means:** real auth is ready to switch on. *(Live Clerk account is a human step.)*

## Issue 8 — Real Stripe products/prices + receipts ⬜/⛔
**Objective:** Wire real Stripe products/prices, receipts, and refund path (behind config).
**Why:** Real payments before launch.
**Scope:** Map service tiers to real Stripe prices; verified webhooks; email receipts; a refund path; keep the demo fallback; document setup in `BLOCKERS.md`.
**Acceptance:** With Stripe configured, checkout→paid→receipt works; demo path still works; tested with stubs/fixtures.
**Verification:** `pytest -q`.
**Security/compliance:** Hosted checkout only; verified webhooks; no card data handled. **Files:** `app/services/checkout_service.py`, `.env.example`, `BLOCKERS.md`, tests. **Depends on:** —. **Done means:** real billing is ready to switch on. *(Live Stripe account is a human step.)*

## Issue 9 — Launch security hardening ⬜
**Objective:** Raise the security bar for launch: dependency + secret scanning in CI, a threat-model doc, and a stronger rate-limit option.
**Why:** Prep for the one-off security review; catch issues automatically.
**Scope:** Add dependency and secret scanning to CI; write `docs/threat-model.md`; make the public rate limiter pluggable with a shared-store option; ensure no secrets in code.
**Acceptance:** CI runs the scans; threat-model doc exists; rate limiter has a shared-store path; tested.
**Verification:** CI run; `pytest -q`.
**Security/compliance:** This issue *is* launch security prep. **Files:** `.github/workflows/*`, `docs/threat-model.md`, `app/middleware/public_hardening.py`, tests. **Depends on:** —. **Done means:** the codebase is ready for the security review.

---

## Recommended order
1 → 2 (analysis then redline), then 3, 4, 5, 6 (independent business features), then 7 and 8 (real integrations, partly blocked on accounts), then 9 (security prep). Issues 3, 5, 9 can be done any time.
