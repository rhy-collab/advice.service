# Review of Codex Batch 05 (PR #3) — merged to `main` (`9e37df6`)

**Verdict: strong. Merged after review; 61 tests pass, CI + Playwright E2E green.**

## Good
- **Retention gap fixed** — `StorageService.delete_object` now removes the real GCS object, and retention deletes objects before rows (fixes the Batch 04 note). Purge is attorney-role gated.
- **Real Anthropic path wired** conservatively: only filename + service tier + **playbook check metadata** are sent — **not the contract text** — so no confidential-content exfil; JSON parse falls back to the stub; results stay attorney-only.
- **Internal-only invariant holds**: every AI-prep, draft, feedback, review-minutes, and playbook endpoint is `require_attorney_context`; no customer/public route exposes AI output.
- Playbook-driven issues, confidence, risk routing, attorney workbench v2, authoring UI, and E2E tests all landed with tests.

## Notes (rolled into Batch 06)
1. **AI prep does not yet read the actual contract text** — it reasons from filename + playbook only. Wiring safe document-text ingestion into the prompt (with no-training posture + secret redaction + size caps) is the real analysis step. → **Batch 06, Issue 1.**
2. Retention deletes objects then commits rows in one pass — if a storage delete succeeds but the commit fails, files are gone but rows remain (minor edge case).
3. `_anthropic_placeholder` now really calls the API — misleading name, cosmetic.
4. In-memory rate limiter still won't scale across instances (carried note).
