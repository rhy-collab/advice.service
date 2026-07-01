# Codex `/goal` Super-Prompt — Complete Batch 04

Paste the block below after `/goal` in Codex, from inside the Charter Law repo.

## Current state (as of `main` = c11f381)
Foundation + two batches are merged and green: backend (guarded matter lifecycle, org-scoped access,
attorney-role approval gate, Stripe, signed file URLs, audit trail + read/report endpoints, typed
config validation, liveness+readiness probes), the free Contract Mistake Checker + public intake,
env-guarded Sentry, Dockerfiles + a Cloud Run deploy recipe, the customer portal pages, and CI
(backend tests + frontend build). 32 backend tests pass. Packaging is fixed (Python >=3.12).

The next nine issues are in `build-system/generated-issues/batch-04-next-nine.md`.

```
GOAL: Complete ALL nine issues in build-system/generated-issues/batch-04-next-nine.md, in order.
Work issue by issue with real code, tests, and verification. Do NOT redefine the goal to a smaller
subset. Continue until all nine are complete or a genuine external blocker (a real account/secret,
or a settings/merge step that needs the owner) prevents further progress.

FIRST: git fetch; check out main; confirm you are on the latest (c11f381 or newer). Run git status;
do not overwrite untracked user files (e.g. codex-review-01.md).

NON-NEGOTIABLE (never regress, all enforced server-side + tested):
- AI may prepare/summarise/organise, but is NEVER presented to a customer as legal advice.
- A matter reaches `delivered` ONLY via a recorded attorney/admin-role approval.
- Org-scoped isolation on every request; fail-closed auth (demo auth off by default).
- File URLs are always short-lived signed URLs; the free checker stores nothing.
- Keep: Python >=3.12 packaging, setuptools app-only discovery, guarded lifecycle transitions.

STACK (do not substitute): Vite + React + TS; FastAPI (uv, Alembic + SQLAlchemy); Postgres/Cloud SQL;
Clerk org-based auth with role claims; Stripe hosted checkout; Google Cloud Storage (signed URLs);
Anthropic Claude for AI; Cloud Run; Sentry. Matter lifecycle:
intake -> ai_review -> attorney_queue -> attorney_review -> delivered -> completed.

FOR EACH ISSUE (2 through 9; confirm 1 first):
  1. Read its acceptance criteria in batch-04-next-nine.md.
  2. Implement the smallest correct slice. For anything needing a real account/secret (Anthropic,
     Clerk, GCS, Stripe, Sentry, email provider), implement behind a clean interface with a
     deterministic stub/no-op fallback that works without the credential, and record the exact human
     step in BLOCKERS.md — then continue.
  3. Add/adjust tests. Every schema change gets an Alembic migration. Secrets via env only.
  4. Verify: from backend/  ->  pip install -e . pytest email-validator httpx  &&  pytest -q ;
     from frontend/  ->  npm ci && npm run build ;  then git diff --check. Fix real causes; never
     skip tests or weaken security to make them pass.
  5. Update the issue's status marker in batch-04-next-nine.md and append to
     build-system/generated-issues/batch-04-progress.md (status, what changed, commands + results).
  6. COMMIT after each issue with a clear message, and PUSH your working branch regularly
     (feat/batch-04) so work is never left uncommitted. Open a PR into main. Do NOT merge to main
     without the owner's explicit go-ahead.

WHEN DONE (or fully blocked): write build-system/generated-issues/codex-goal-handoff-after-batch-04.md
summarising which issues are complete, which are blocked and why, exact files changed, exact commands
run and results, current branch/status, and the next best action. Report the same plainly in chat.
```
