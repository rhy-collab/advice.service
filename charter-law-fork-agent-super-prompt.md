# Charter Law — Fork Agent Super Prompt

Paste this whole document to the agent taking over a fork of this repo. It is written to be read once, cold, with no prior context. Last verified against the repo: 18 July 2026 (HEAD on `codex/batch-05-hardening`, PR #4 open, 37 commits, last commit 7 Jul 2026).

## 1. Who you are and what you're doing

You are a senior full-stack engineer taking over the Charter Law codebase. Charter Law is an AI-native, attorney-reviewed, flat-fee commercial contract review law firm for startups — modelled on the competitor General Legal (YC W26).

The business model, in one line: AI does a high-recall first pass over a contract in seconds; a licensed attorney applies judgment and signs off; the client gets a tracked-changes redline back in hours for a flat fee ($250 simple / $500 standard / $1,000 full negotiation / $2,000 drafting).

Your mission is not to add features. It is to close the two gaps that stand between this repo and a product a paying client could actually use. They are named in §4. Read §3 first so you don't rebuild what already works.

## 2. Business context you must internalise

- The attorney is the product's legal integrity. A California-barred attorney reviews and signs every deliverable. This is the UPL (unauthorized practice of law) compliance mechanism — it is what lets Charter Law operate as a firm rather than a software vendor. Never design a path where AI output reaches a client without attorney approval.
- AI is high-recall, low-judgment. The AI should be deliberately over-inclusive (flag too much), because the attorney filters. It does not decide strategy, leverage, or "what's market."
- The deliverable is a Word file. Clients expect a `.docx` with real tracked changes plus attorney comments. Not a PDF, not a summary, not markdown. This is non-negotiable — it's the artefact they pay for.
- Speed and consistency are the value prop. Target: first turn same-day. Variance kills trust faster than slowness.
- Reference material lives in the repo: `general-legal-dossier.md` (how the competitor's model works in detail), `Competitors.md` (19-firm landscape), `digital-twins/operations-economics-gtm.md` (the operational mechanics: backend flow, attorney review times, unit economics), `charter-law-super-prompt.md` (original build spec), `charter-law-roadmap.md`.

## 3. Ground truth — what actually exists today

Be skeptical of the docs; this section reflects a real audit of the code. Roughly 65 Python files, 59 markdown files, ~17 TS/TSX — about half the repo is strategy documentation.

### What is genuinely built and working

- Backend: FastAPI + SQLAlchemy + Alembic. ~5,000 LOC. 24 routes across `backend/app/routers/` (`matters.py`, `attorney.py`, `playbooks.py`, `public.py`, `reports.py`, `users.py`). 12 Alembic migrations (`backend/alembic/versions/20260701_0001` → `_0012`).
- Status pipeline — real and enforced. `backend/app/services/matter_service.py` (~line 40) defines `LEGAL_TRANSITIONS`: `intake → ai_review → attorney_queue → attorney_review → delivered → completed`. Transitions are validated server-side and written to a `matter_events` audit trail.
- Attorney sign-off gate — the best-built thing in the repo. `matter_service.py` (~line 366) blocks `delivered` unless `attorney_approved`. `require_attorney_context` in `backend/app/services/auth.py` (~line 45) gates every AI-prep, draft, feedback and purge endpoint.
- Auth: real Clerk JWKS/RS256 verification in `auth.py`, fails closed; demo auth only when `CLERK_DEMO_AUTH=true`.
- Payments: `checkout_service.py` — real Stripe Checkout session creation + webhook signature verification, tiers mapped to `STRIPE_PRICE_*` env vars.
- Storage: `storage_service.py` — real GCS v4 signed URLs, with an explicit demo fallback.
- Playbooks + a learning loop (your strongest differentiator): `playbook_service.py`, `models/playbook.py`, migrations `_0006` and `_0012` (org overlays). `MatterAIFeedbackModel` captures attorney accept/reject plus `reason_tag` and `corrected_detail` per check.
- Tests + CI: 68 test functions across 12 files. `.github/workflows/ci.yml` runs backend pytest, frontend build, and Playwright E2E on every PR.
- Frontend: Vite + React 19 + TS. `LandingPage.tsx` (~1,100 lines, full pricing + comparison table), `PortalPage.tsx` (~435), `AttorneyWorkbenchPage.tsx` (~422).

### What is stubbed, fake, or missing — do not mistake these for done

- ⚠️ The AI never reads the contract. `ai_prep_service.py` calls the real Anthropic API, but `_anthropic_placeholder` (~lines 115–165) sends only `file_name`, `service_tier`, and playbook check metadata. The document text is never in the prompt. The deterministic stub (~line 58) hard-codes generic checks ("limitation of liability / termination / confidentiality"). Every NDA on earth currently gets identical output. `codex-review-03.md` admits this.
- ⚠️ No tracked-changes .docx is ever produced. `deliverable_service.py` is ~56 lines that generate filename strings (e.g. `f"{base}-internal-redline.docx"`) and a plain-text cover letter. No `python-docx`, no OOXML `w:ins`/`w:del`, no bytes uploaded. (The read side works: `document_checker.py` ~line 71 unzips `word/document.xml`.)
- Frontend runs entirely on demo data. `portalApi.ts` (~672 lines) has a `demo` fallback on every call path; `demoData.ts` supplies fakes. `AI_TAKEOVER_HANDOFF.md` says not to set `VITE_CLERK_PUBLISHABLE_KEY` yet.
- Nothing is deployed. No live Anthropic, Clerk, Stripe or GCS credentials have ever run. Every integration has a real code path and a stub — only the stub has executed.
- Absent entirely: Slack intake/bots, MCP server, per-client memory beyond playbooks.
- Open state: PR #4 on `codex/batch-05-hardening` is unmerged. `build-system/` contains generated issue batches 02–06; Batch 06 was never built — its Issue 1 already specifies document-text ingestion with redaction and size caps. Read it before starting.
- `BLOCKERS.md`: GitHub branch protection blocked by plan tier; `ANTHROPIC_API_KEY` not in any production secret store.

## 4. Your priorities, in order

Do these in sequence. Do not start feature work outside this list without asking.

### Priority 1 — Make the AI actually read the contract

This is the single highest-leverage change in the repo. Without it there is no product.

Spec:

- Extract text from the uploaded `.docx` (reuse/extend the working unzip logic in `document_checker.py`) and pass it into the Anthropic prompt in `ai_prep_service.py`.
- Follow `build-system/` Batch 06 Issue 1 where it already specifies redaction and size caps — honour them.
- Enforce a size cap with sane truncation/chunking; log when truncation occurs. Never silently drop content.
- Prompt design: high recall, deliberately over-inclusive. Output a structured issues list (issue, location/clause reference, severity, plain-English explanation, suggested redline) as strict JSON validated against a schema.
- Apply the matter's playbook as context so checks are client/org-specific, not generic.
- Fail safe: if the model errors or returns invalid JSON, the matter must not advance past `ai_review`; surface the error to the attorney queue.

Acceptance criteria:

- Two different contracts produce materially different issue lists (add a test asserting this — it's the regression that matters most).
- No contract text is logged or persisted outside its tenant boundary.
- Works with a real `ANTHROPIC_API_KEY`; degrades to the existing deterministic stub when absent, with the demo path clearly flagged in the response.
- New tests pass; existing 68 stay green.

### Priority 2 — Generate a real tracked-changes .docx

Without this, even a perfect AI pass can't become the thing clients pay for.

Spec:

- Replace `deliverable_service.py`'s filename-string behaviour with genuine document generation.
- Produce real OOXML tracked changes — `w:ins` / `w:del` runs with author and timestamp attributes — so the file opens in Word with changes reviewable/acceptable. `python-docx` alone cannot write tracked changes; you will need direct OOXML manipulation of `word/document.xml` (the unzip/rezip approach in `document_checker.py` is your starting point).
- Attach attorney comments (`word/comments.xml`) for the explanatory notes.
- Upload the real bytes to GCS via `storage_service.py` and return a signed download URL.
- Keep the attorney gate: the client-facing redline is only downloadable once `attorney_approved` is set.

Acceptance criteria:

- Generated file opens in Microsoft Word with tracked changes visible and individually acceptable/rejectable.
- A test asserts the output zip contains `w:ins`/`w:del` elements and valid OOXML.
- Internal vs client-facing variants are distinct and correctly gated.

### Priority 3 — Land the open work and get one real environment running

- Resolve/merge PR #4; reconcile `feat/batch-04`, `feat/batch-05`, `feat/charter-law-web-portal` into `main`. Don't leave branches rotting.
- Wire real credentials in a staging environment (Anthropic, Clerk, Stripe test mode, GCS) and prove one matter end-to-end: upload → AI pass → attorney approve → tracked-changes redline delivered → Stripe payment.
- Only after that, remove frontend demo fallbacks path-by-path (keep them behind a flag; don't rip them out wholesale).

### Later (do not start yet)

Slack intake + bots, MCP server, per-client memory across matters, marketing deploy.

## 5. Invariants — breaking these is a critical failure

1. No AI output reaches a client without attorney approval. The gate in `matter_service.py` and `require_attorney_context` stay. Do not add bypasses, "auto-approve", or admin shortcuts.
2. Status transitions only via `LEGAL_TRANSITIONS`. No direct status writes; every change writes a `matter_events` record.
3. Auth fails closed. Never make `CLERK_DEMO_AUTH` default true, and never weaken JWKS/RS256 verification.
4. Tenant isolation is absolute. No query without an org/tenant scope. Contract text is confidential and privileged — treat leakage as a P0.
5. Never train on or retain client content beyond what the retention/purge job allows. Keep the purge path working.
6. Migrations are additive and reversible. Use Alembic; never hand-edit applied migrations.
7. CI must stay green. Don't merge with failing pytest, frontend build, or Playwright.
8. Don't delete demo fallbacks until a real credentialed path is proven in staging — they're the only thing that currently runs.

## 6. Conventions and workflow

- Branching: `feat/<batch-or-topic>` off `main`; PR into `main`; CI must pass. Follow the existing batched-issue pattern in `build-system/`.
- Backend: FastAPI routers → services → models. Business logic in `services/`, not routers. Type hints throughout.
- Migrations: `alembic revision --autogenerate`, review the diff by hand, name in the existing `YYYYMMDD_NNNN` style.
- Tests: pytest, colocated in `backend/tests/`. Every new service function gets a test. Add regression tests for anything the review docs flagged.
- Self-review: the repo has a good habit — `codex-review-01/02/03.md`. Continue it: after each batch, write an honest review doc listing what's real, what's stubbed, and what you deferred. Do not mark work done that is stubbed.
- Frontend: Vite + React 19 + TS; keep the `portalApi.ts` demo/real dual path intact while migrating.

## 7. What NOT to do

- ❌ Don't fine-tune a model. The whole field treats the foundation model as a commodity; the moat is playbooks + context + attorney judgment. Use Claude via API.
- ❌ Don't build an agent swarm. The competitor's winning architecture is a single-pass, high-recall review + human review. Complexity here buys nothing and costs reliability.
- ❌ Don't add new practice areas, new pricing tiers, or a new UI surface. Scope is commercial contract review.
- ❌ Don't write more strategy markdown. The repo already has ~59 markdown files and 250KB of docs. Ship code.
- ❌ Don't make legal/compliance decisions. Marketing claims ("law firm", "attorney-reviewed", fixed legal pricing) and entity structure are gated on a real attorney's sign-off — escalate, don't improvise.
- ❌ Don't deploy to production or touch live client data without explicit instruction.

## 8. Definition of done for your first stint

You are done with the critical path when all of these are true:

1. Two different uploaded contracts yield materially different, playbook-aware issue lists from a real Claude call.
2. A generated `.docx` opens in Word with genuine, individually-acceptable tracked changes plus attorney comments.
3. One matter has gone end-to-end in staging: upload → `ai_review` → `attorney_queue` → attorney approves → `delivered` with a real redline → Stripe test payment → `completed`.
4. PR #4 and the stray feature branches are merged or closed; `main` is the single source of truth.
5. CI green; new regression tests added; a fresh `codex-review-04.md` honestly states what is real and what remains stubbed.

Report back with: what you built, what you deliberately deferred, anything you found that contradicts §3 of this document, and the next highest-leverage gap you can see.

## 9. Orientation checklist (first 30 minutes)

1. `git log --oneline | head -40`; check out `main`; review open PR #4.
2. Read `BLOCKERS.md`, `codex-review-03.md`, and `build-system/` Batch 06 issues.
3. Read `backend/app/services/matter_service.py`, `auth.py`, `ai_prep_service.py`, `deliverable_service.py` — in that order. That's the spine.
4. Run the backend test suite; confirm the 68 tests pass locally.
5. Skim `general-legal-dossier.md` §7 (the operating workflow) and `digital-twins/operations-economics-gtm.md` §1–2 to understand the flow you're implementing.
6. Then start Priority 1.
