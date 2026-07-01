# Codex `/goal` Super-Prompt — Complete Batch 06 (real analysis + launch readiness)

Paste the block below after `/goal` in Codex, from inside the Charter Law repo.

## Current state (`main` = 9e37df6, 61 tests + E2E green)
Foundation + Batches 02-05 merged: the moat is taking shape (playbook data model + authoring UI +
per-client overlay, playbook-driven internal AI prep, attorney feedback loop, confidence + risk
routing, redline/cover-letter drafts, attorney workbench v2), real Anthropic path (filename +
playbook only so far), retention with real GCS deletion, notifications, observability, E2E in CI.
Batch 06 makes the AI analyse the real document and gets the product launch-ready.
Issues: `build-system/generated-issues/batch-06-next-nine.md`.

```
GOAL: Complete ALL nine issues in build-system/generated-issues/batch-06-next-nine.md, in order.
Real code, tests, verification. Do NOT redefine the goal to a smaller subset. Continue until all
nine are complete or a genuine external blocker (a real account/secret, or an owner/settings step)
prevents progress.

FIRST: git fetch; checkout main; confirm latest (9e37df6 or newer); git status; do not overwrite
untracked files (codex-review-01.md, codex-review-02.md, codex-review-03.md).

NON-NEGOTIABLE (never regress; enforced server-side + tested):
- AI is NEVER shown to a customer as legal advice; AI prep + drafts stay attorney-only/internal
  until approval. When feeding the contract TEXT to the model: no-training posture, redact obvious
  secrets, cap size, and NEVER log document contents.
- `delivered` requires a recorded attorney/admin-role approval (two approvals when second-chair is on).
- Org isolation on every request; fail-closed auth; signed-only file URLs; free checker stores nothing.
- Keep Python >=3.12 packaging and guarded lifecycle transitions.

STACK (do not substitute): Vite+React+TS; FastAPI (uv, Alembic+SQLAlchemy); Postgres/Cloud SQL; Clerk
org auth with roles; Stripe hosted checkout; GCS signed URLs; Anthropic Claude (internal-only);
Cloud Run; Sentry.

FOR EACH ISSUE:
  1. Read its acceptance criteria. 2. Implement the smallest correct slice; anything needing a real
  account/secret (Anthropic key, Clerk, Stripe, GCS, email/Slack) goes behind a clean interface with
  a deterministic stub fallback + a note in BLOCKERS.md, then continue. 3. Add tests; every schema
  change gets an Alembic migration; secrets via env only. 4. Verify: from backend/  ->
  pip install -e . pytest email-validator httpx && pytest -q ; from frontend/ -> npm ci &&
  npm run build (and Playwright E2E if touched) ; then git diff --check. Fix real causes; never skip
  tests or weaken security. 5. Update the issue status in batch-06-next-nine.md and append to
  build-system/generated-issues/batch-06-progress.md. 6. COMMIT after each issue and PUSH your branch
  (feat/batch-06) regularly; open a PR into main; do NOT merge to main without the owner's go-ahead.

WHEN DONE (or fully blocked): write
build-system/generated-issues/codex-goal-handoff-after-batch-06.md (issues complete, blocked + why,
exact files changed, exact commands + results, branch/status, next best action) and report the same
plainly in chat.
```
