# Claude / Kirk Handoff — Batch 05 Completed

Batch 05 was completed on branch `feat/batch-05`.

## Completed issues

1. Retention deletes actual storage objects before deleting expired file rows.
2. AI prep is grounded in contract-type playbook checks.
3. Attorney feedback is stored and updates linked playbook check accuracy/fallback language.
4. Internal draft redline and cover-letter work product is generated after AI prep.
5. Risk score and risk route are computed from severity plus confidence.
6. Anthropic Messages API integration is wired behind `ANTHROPIC_API_KEY`, with deterministic fallback.
7. `/attorney` now has a dedicated workbench for AI prep, feedback actions, review minutes, and approval.
8. Attorney playbook authoring supports per-client overlays and check edits.
9. Playwright E2E tests and CI `frontend-e2e` job were added.

## Verified locally

- Backend: `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q` → 61 passed, 3 existing warnings.
- Frontend: `npm run build` → passed.
- E2E: `npm run e2e` → 2 passed.
- Whitespace: `git diff --check` → passed.

## External blocker

GitHub branch protection / required checks still cannot be enabled by API while the repository plan or visibility blocks it. GitHub returned:

```text
HTTP 403: Upgrade to GitHub Pro or make this repository public to enable this feature.
```

Owner action required after merge: upgrade/adjust plan or repo visibility, then require CI checks on `main`.

## Suggested Claude follow-up

Review PR/branch `feat/batch-05`, confirm CI, and focus next on launch polish:

- Dogfood `/portal` and `/attorney` in a real browser at desktop and mobile widths.
- Replace preset playbook authoring buttons with full field-by-field forms.
- Add real document-generation storage writes for redline and cover-letter files.
- Add live Anthropic secret only in the deployment secret store, never in git.
