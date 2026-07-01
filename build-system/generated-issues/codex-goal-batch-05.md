# Codex `/goal` Super-Prompt — Complete Batch 05 (the moat)

Paste the block below after `/goal` in Codex, from inside the Charter Law repo.

## Current state (`main` = bdf55bb, 51 tests green)
Foundation + Batches 02-04 merged: attorney-only workspace (queue + approval + AI-prep view),
internal-only AI prep (Anthropic behind a safe stub), playbook data model, public hardening,
notifications, observability, retention (DB refs only — see Issue 1), Dockerfiles + deploy recipe,
customer portal. Batch 05 turns this into the real playbook-driven, attorney-in-the-loop engine.
Issues: `build-system/generated-issues/batch-05-next-nine.md`.

```
GOAL: Complete ALL nine issues in build-system/generated-issues/batch-05-next-nine.md, in order.
Real code, tests, verification. Do NOT redefine the goal to a smaller subset. Continue until all
nine are complete or a genuine external blocker (a real account/secret, or an owner/settings step)
prevents progress.

FIRST: git fetch; checkout main; confirm latest (bdf55bb or newer); git status; do not overwrite
untracked files (codex-review-01.md, codex-review-02.md).

NON-NEGOTIABLE (never regress; enforced server-side + tested):
- AI is NEVER shown to a customer as legal advice; AI prep stays attorney-only/internal until approval.
- `delivered` requires a recorded attorney/admin-role approval.
- Org isolation on every request; fail-closed auth; signed-only file URLs; free checker stores nothing.
- Keep Python >=3.12 packaging and guarded lifecycle transitions.

STACK (do not substitute): Vite+React+TS; FastAPI (uv, Alembic+SQLAlchemy); Postgres/Cloud SQL; Clerk
org auth with roles; Stripe hosted checkout; GCS signed URLs; Anthropic Claude (internal-only);
Cloud Run; Sentry.

FOR EACH ISSUE:
  1. Read its acceptance criteria. 2. Implement the smallest correct slice; anything needing a real
  account/secret (Anthropic key, GCS, email provider) goes behind a clean interface with a
  deterministic stub fallback + a note in BLOCKERS.md, then continue. 3. Add tests; every schema
  change gets an Alembic migration; secrets via env only. 4. Verify: from backend/  ->
  pip install -e . pytest email-validator httpx && pytest -q ; from frontend/ -> npm ci &&
  npm run build ; then git diff --check. Fix real causes; never skip tests or weaken security.
  5. Update the issue's status in batch-05-next-nine.md and append to
  build-system/generated-issues/batch-05-progress.md. 6. COMMIT after each issue and PUSH your
  branch (feat/batch-05) regularly so nothing is left uncommitted; open a PR into main; do NOT
  merge to main without the owner's explicit go-ahead.

WHEN DONE (or fully blocked): write
build-system/generated-issues/codex-goal-handoff-after-batch-05.md (issues complete, blocked +
why, exact files changed, exact commands + results, branch/status, next best action) and report the
same plainly in chat.
```
