# Codex `/goal` Super-Prompt — Continue Building Charter Law

*Paste everything in the fenced block below after `/goal` in Codex, from inside the `Charter-Law/charter-law` repo. It tells Codex to keep building autonomously, issue by issue, through the backlog — stopping only for things a human must do.*

```
GOAL: Continue building Charter Law toward production-ready, working autonomously through the
backlog one issue at a time. Keep going until you either finish the backlog or hit a blocker
that genuinely requires a human. Prefer making steady, reviewed progress over speed.

=== READ FIRST (authoritative, in this repo) ===
- charter-law-super-prompt.md   -> the authoritative feature spec
- charter-law-roadmap.md        -> phases + the live "Build Progress" section (current state)
- charter-law-tech-stack.md     -> the authoritative stack + project structure
- build-system/CLAUDE.md        -> standing rules and conventions
- build-system/issues-batch-01-engineering-foundation.md
- build-system/issues-backlog-batches-02-07.md   -> the ordered backlog you work through
- codex-review-01.md            -> the review of your first pass; do not reintroduce those issues
Treat the super-prompt as the feature source of truth and the tech-stack as the stack source of
truth. If any instruction here conflicts with them, follow them and note it.

=== WHAT IS ALREADY DONE (in main, do not rebuild) ===
The web portal foundation is merged: FastAPI backend (matters, files, audit events, matter
lifecycle, Stripe checkout + webhook, upload targets, attorney-approval action), a Vite+React+TS
customer portal, org-scoped isolation, an attorney-ROLE delivery gate, fail-closed auth, signed
upload/download URLs, a passing test suite, and a CI workflow that runs tests on every PR.

=== THE ONE RULE THAT OVERRIDES EVERYTHING ===
"AI prepares; an attorney approves and owns." No AI output is ever shown to a customer as legal
advice. A matter can NEVER reach `delivered` without a recorded approval from a user with an
attorney/admin role — enforced in the backend, not just the UI, and covered by a test. Never
weaken this. Keep organisation-scoped data isolation on every request.

=== STACK (do not substitute) ===
Vite + React + TypeScript (customer portal + a separate attorney app); Python + FastAPI backend
(uv, Alembic + SQLAlchemy); PostgreSQL on Cloud SQL; Clerk org-based auth (verify the session on
every backend request, scope all data to the requesting org, honour role claims); Stripe hosted
checkout only; Google Cloud Storage (signed URLs; never store file bytes in the DB); Anthropic
Claude for AI; Claude for Word add-in for tracked-changes redlines; Google Cloud Run hosting;
Cloudflare; Sentry. Matter lifecycle: intake -> ai_review -> attorney_queue -> attorney_review ->
delivered -> completed.

=== BUILD ORDER (work top-down; each item = one or more atomic PRs) ===
1. DEPLOY + MONITORING (Batch 01 #9): Dockerfiles for backend + both frontends; a Cloud Run deploy
   config; wire Sentry on all surfaces; secrets via environment config only. Provide a documented
   deploy command. (You cannot create the cloud accounts — see BLOCKERS.)
2. SEPARATE ATTORNEY APP (Batch 01 #7 + Batch 06 #6.1-6.5): a distinct Vite+React+TS app restricted
   to attorney/admin users; a matter queue; a review surface (Word + Claude add-in, Apply/Dismiss +
   reasoning); confidence flags highlighted; the Approve gate that alone moves a matter to
   `delivered`; capture attorney-minutes (HuRT). Move approval out of the customer API into here.
3. AI PREP ENGINE (Batch 04): document ingestion; internal-only summary + issue list; over-inclusive
   tracked-changes redline; the "what changed / why risky / your fallback" cover letter; per-issue
   strong/medium/weak confidence; enforce internal-only + queue handoff server-side.
4. PLAYBOOK SYSTEM (Batch 05): structured risk/clause library in Postgres (detection, severity,
   remediation intent, preferred/acceptable/unacceptable fallback language, per-check accuracy),
   per-client overlay, risk score + routing, an authoring screen; wire the engine to use it.
5. FEEDBACK LOOP (Batch 06 #6.6): reason-tagged attorney corrections update the playbook and track
   per-check accuracy.
6. REMAINING PORTAL + PHASE 5 items per the backlog (status tracker polish, "Clerk" assistant,
   notifications, Slack/email delivery, market-benchmark data capture, MCP server) as reachable.

=== HOW TO WORK (the loop, repeat) ===
For each issue, in order:
  a. Plan the smallest correct slice; keep one concern per branch/PR.
  b. Create a branch feat/<short-name>. Implement with the stack + conventions above.
  c. Write/'update tests FIRST where practical; every schema change gets an Alembic migration;
     secrets in env vars only; separate SQLAlchemy models from Pydantic schemas; thin routers +
     service layer.
  d. Run the full backend test suite locally and make it pass. Do not mark an issue done with
     failing tests or a partial implementation.
  e. Commit with a clear message and open a PR that links the issue and explains how it was tested.
     Ensure CI is green. Then merge to main if unblocked, and move to the next issue.
  f. After each merge, append a one-line entry to DECISIONS.md and update the "Build Progress"
     section of charter-law-roadmap.md so state stays current.
  g. If corrected, update build-system/CLAUDE.md with a short rule so the mistake never repeats.

=== PRODUCTION-READINESS BAR (non-negotiable) ===
Org-scoped isolation on every request (add negative tests); encryption in transit/at rest; an
audit/events row for uploads, AI runs, and approvals; Stripe hosted checkout only with verified
webhooks; Sentry on every surface; keep real client documents out of tests; honour "we never store
your contract" literally for the free tool; fail closed on auth. Flag any change that would need the
one-off security review before real client contracts.

=== BLOCKERS: what you CANNOT do — do NOT guess or fake around these ===
You cannot create third-party accounts, set real secret keys, engage the attorney, or run the
security review. When an issue needs one of those:
  - Implement everything behind a clean interface with a documented demo/stub fallback that works
    without the real credential (as already done for Stripe and GCS), reading config from env vars
    listed in .env.example.
  - Clearly list the exact human step required (e.g. "create the Cloud Run service and set
    GOOGLE_APPLICATION_CREDENTIALS") in the PR description and in a top-level BLOCKERS.md.
  - Then continue with the next issue you CAN make progress on. Do not stop the whole goal for one
    external dependency.

=== WHEN TO STOP ===
Stop and summarise only when: the backlog is complete; or every remaining issue is blocked on a
human step you have documented in BLOCKERS.md; or you hit something that would violate the one rule
or the production-readiness bar. Otherwise, keep going. At the end, output a concise status: what
merged, what is blocked and why, and the recommended next human action.
```
