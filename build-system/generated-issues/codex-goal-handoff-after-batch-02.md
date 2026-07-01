# Codex `/goal` Handoff After Batch 02

Use this as the next continuation prompt for Codex.

```text
Use /goal to continue the Charter Law build from the current repo state.

Current repo:
- Local path: /Users/rhys/Downloads/Projects/Charter Law
- Branch at time of handoff: feat/charter-law-web-portal
- Existing untracked user file to preserve: codex-review-01.md
- Do not overwrite untracked files or user local changes.

What was inspected:
- charter-law-roadmap.md
- build-system/issues-backlog-batches-02-07.md
- build-system/CLAUDE.md
- build-system/DECISIONS.md
- backend app, routers, models, services, schemas, tests, migrations
- frontend landing page, portal, API helpers, styles
- .github/workflows/ci.yml

Batch file generated:
- build-system/generated-issues/batch-02-next-nine.md

Progress log:
- build-system/generated-issues/batch-02-progress.md

Issues generated and status:
1. Restore trustworthy backend CI/package baseline — Completed
2. Free Contract Mistake Checker backend — Completed
3. Free Contract Mistake Checker frontend — Completed
4. Public intake API — Completed
5. Public intake frontend — Completed
6. Environment and command documentation — Completed
7. API contract update for public endpoints — Completed
8. CI workflow covers frontend build — Completed
9. Batch handoff and completion audit — Completed once this file is present and final diff check passes

Files changed:
- .github/workflows/ci.yml
- .gitignore
- backend/alembic/versions/20260701_0004_create_public_intakes.py
- backend/app/db/session.py
- backend/app/main.py
- backend/app/models/intake.py
- backend/app/routers/public.py
- backend/app/schemas/public.py
- backend/app/services/document_checker.py
- backend/app/services/intake_service.py
- backend/pyproject.toml
- backend/tests/conftest.py
- backend/tests/test_document_checker.py
- backend/tests/test_public_intake.py
- backend/uv.lock
- build-system/CLAUDE.md
- build-system/DECISIONS.md
- build-system/generated-issues/batch-02-next-nine.md
- build-system/generated-issues/batch-02-progress.md
- build-system/generated-issues/codex-goal-handoff-after-batch-02.md
- frontend/API_CONTRACT.md
- frontend/src/features/landing/LandingPage.tsx
- frontend/src/lib/publicApi.ts
- frontend/src/styles.css

Commands already run and results:
- /opt/homebrew/bin/python3.12 -m venv /tmp/charter-law-backend-ci-venv — succeeded
- /tmp/charter-law-backend-ci-venv/bin/python -m pip install --upgrade pip — succeeded
- /tmp/charter-law-backend-ci-venv/bin/python -m pip install -e . pytest email-validator — succeeded
- /tmp/charter-law-backend-ci-venv/bin/python -m pip install -e . pytest email-validator httpx — succeeded
- /tmp/charter-law-backend-ci-venv/bin/python -m pytest -q — succeeded with 21 passed, 3 warnings
- cd frontend && npm run build — succeeded
- cd frontend && npm ci && npm run build — succeeded
- git diff --check — succeeded
- uv lock — succeeded after adding python-multipart

Important compliance/security invariants preserved:
- AI/checker output is preparation-only, not legal advice.
- The free Contract Mistake Checker processes uploaded .docx bytes in memory and stores nothing.
- Public intake creates a lead record, not a customer matter or attorney-approved deliverable.
- Demo auth remains local opt-in only and defaults off.
- Attorney approval remains role-gated.
- Customer matter access remains org-scoped.
- Deliverable downloads remain gated behind delivered/approval state.

Next best action:
1. Inspect current `git status --short --branch`.
2. Run final verification:
   - cd backend && pytest -q
   - cd frontend && npm ci && npm run build
   - git diff --check
3. Stage the completed Batch 02 files, preserving codex-review-01.md unless the user explicitly wants it included.
4. Commit with a message like: `feat: add public checker and intake flow`
5. Push the branch.
6. Confirm GitHub Actions backend and frontend jobs go green remotely.
7. Then generate Batch 03 next-nine issues from the roadmap, likely around production deployment readiness, environment validation, attorney workspace separation, Sentry, and end-to-end portal hardening.

Use /goal to complete all remaining issues in build-system/generated-issues/batch-02-next-nine.md. Work issue by issue. Verify each issue before marking it complete. Do not redefine the goal to a smaller subset. Continue until all nine are complete, or until a genuine external blocker prevents progress.

If Batch 02 is already complete when you resume, audit it from current state, mark it complete only if evidence still proves every issue, then move immediately to the next production-readiness batch.
```
