# Review of Codex Batch 04 (PR #2) — merged to `main` (`bdf55bb`)

**Verdict: strong, compliance-aware work. Merged after review; 51 tests pass, CI green.**

## What's good
- **Approval moved out of the customer API** into an attorney-only router (`/v1/attorney/matters/{id}/approve`), role-gated. This closes the earlier "customer could self-approve" gap.
- **AI prep is internal-only.** Results are exposed *only* via an attorney-role endpoint (`/v1/attorney/matters/{id}/ai-prep`); no customer endpoint returns them. The Anthropic path is deliberately a safe stub until wired — no unreviewed model calls.
- **Public hardening**: per-IP rate limiting + an early content-length 413, with the checker's post-read size check as a backstop. Defense-in-depth.
- **Playbook data model, notifications, observability, retention** all landed with tests. Sensible env-stub fallbacks throughout.

## Notes / things to change (rolled into Batch 05)
1. **Retention deletes DB file references but NOT the actual GCS objects** — confidential files could be orphaned in the bucket. Real deletion must also remove the storage object (or rely on a documented GCS lifecycle rule). → **Batch 05, Issue 1.**
2. **Rate limiter is in-memory (per-process)** — won't hold across multiple Cloud Run instances. Fine for MVP; needs a shared store (e.g. Redis) at scale. → note for later.
3. **Content-length check can be bypassed** by omitting/faking the header; the checker's real byte-count check is the backstop. Acceptable, but a hard streaming cap would be stronger. → note for later.
4. `on_event` startup is deprecated (pre-existing) — migrate to FastAPI lifespan handlers eventually. → minor.

None of these block the merge; #1 is the one that matters for confidentiality and is the first Batch 05 issue.
