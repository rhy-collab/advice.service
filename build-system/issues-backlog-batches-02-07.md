# Issues — Full Backlog, Batches 02–07 (through to production-ready)

*The complete remaining backlog after Batch 01 (Engineering Foundation). Ordered by phase. Each issue is atomic with acceptance criteria and dependencies. Together with Batch 01 this carries Charter Law from empty repo to a production-ready, attorney-gated contract-review platform.*

**Global rules (every issue obeys):**
- *AI prepares; an attorney approves and owns.* No AI output reaches a customer as legal advice; a matter never reaches `delivered` without a recorded attorney approval — enforced server-side.
- Stack: Vite + React + TS · FastAPI (`uv`, Alembic + SQLAlchemy) · Postgres/Cloud SQL · Clerk (org-based) · Stripe (hosted) · Google Cloud Storage · Anthropic Claude · Cloud Run · Sentry.
- Org-scoped data isolation on every request. Secrets in env vars only. Tests against a throwaway DB. Every schema change is an Alembic migration.

---

# Batch 02 — Phase 2: Lead-gen + intake *(first revenue-driving software)*

### 2.1 — Free "Contract Mistake Checker" (lead magnet)
**Goal:** A public, no-login tool: drag-drop a `.docx`, get a free AI pass on cheap high-credibility errors, ending in a CTA to a paid review.
**Acceptance criteria:**
- [ ] Drag-drop `.docx` upload on a standalone public page (isolated from the main app).
- [ ] AI surfaces: typos, broken cross-references, defined-terms-never-used, missing standard sections.
- [ ] Returns a short, shareable report.
- [ ] **The file is processed in memory and never stored** — the page states "We never save or store your contract," and that is literally true.
- [ ] Clear CTA to book a paid review.
**Compliance/security:** No persistence of the uploaded file anywhere. No login. Keep fully isolated from customer data.

### 2.2 — Public intake + matter creation
**Goal:** A stranger can submit a contract and details, creating a pending matter the team can pick up.
**Acceptance criteria:**
- [ ] Intake form (contract type, urgency, contact, file) that creates a matter in `intake` and notifies the team.
- [ ] Works before login exists (pre-portal); captures enough to follow up.
- [ ] Confirmation screen + email to the submitter.
**Depends on:** Batch 01 #4.

### 2.3 — Stripe checkout for flat-fee tiers
**Goal:** Customers pay a flat fee via Stripe hosted checkout; payment is recorded against the matter.
**Acceptance criteria:**
- [ ] Stripe hosted checkout for the tier set (e.g. ~$250 / $500 / $1,000 / $2,000).
- [ ] On successful payment (webhook), the matter is marked paid.
- [ ] Never handle card data directly.
**Compliance/security:** Hosted checkout only; verify Stripe webhook signatures.
**Depends on:** 2.2.

### 2.4 — Connect the Webflow marketing site
**Goal:** The marketing site's CTAs route to the intake form, checkout, and the free checker.
**Acceptance criteria:**
- [ ] "Send us a contract" → intake/checkout flow.
- [ ] Free checker linked from the site.
- [ ] Basic analytics events fire on key actions.
**Note:** Webflow itself is no-code (founder-built); this issue is the wiring/embeds.

### 2.5 — Truthful-copy compliance gate
**Goal:** A repeatable check that every public claim (speed, "attorney-reviewed," pricing) is accurate and attorney-approved.
**Acceptance criteria:**
- [ ] A checklist doc the attorney signs off before any new public claim ships.
- [ ] Copy says "your reviewing attorney," not "our lawyers," until the firm structure supports it.

---

# Batch 03 — Phase 3: Customer portal v1

### 3.1 — Authenticated file upload to Cloud Storage
**Goal:** A logged-in customer uploads a `.docx`, stored in Google Cloud Storage with only a reference in the DB; a matter is created in `intake`.
**Acceptance criteria:**
- [ ] Upload via signed URLs to GCS; DB stores the key, not the bytes.
- [ ] Matter created and scoped to the user's org.
- [ ] File type/size validation; clear errors.
**Compliance/security:** Org-scoped; encrypted at rest; audit event recorded.
**Depends on:** Batch 01 #5, #6.

### 3.2 — Matter list / dashboard
**Goal:** The customer sees their org's matters in a list.
**Acceptance criteria:**
- [ ] Columns: File name · Versions · Status · Submitted.
- [ ] Strictly org-scoped (cannot see other orgs).
- [ ] Empty state + loading state.
**Depends on:** 3.1.

### 3.3 — Domino's-style status tracker (static stages)
**Goal:** A horizontal progress bar across the five stages, lighting up as a matter advances.
**Acceptance criteria:**
- [ ] Stages: Received → AI Review → Queued for Attorney → Attorney Review → Delivered.
- [ ] Current stage highlighted; completed stages filled.
- [ ] Static first (smart ETAs come in Batch 07).
**Depends on:** 3.2.

### 3.4 — Matter detail + deliverable download
**Goal:** A customer opens a matter and downloads the finished, attorney-approved deliverable when ready.
**Acceptance criteria:**
- [ ] Detail view with status, files, and timeline.
- [ ] Download enabled **only** once the matter is `delivered`.
**Compliance/security:** No AI draft is ever downloadable before attorney approval.
**Depends on:** 3.2.

### 3.5 — Billing in the portal
**Goal:** Customers pay/managing billing inside the portal via Stripe.
**Acceptance criteria:**
- [ ] Stripe hosted checkout from the portal; billing/history view.
- [ ] Matter marked paid on webhook.
**Depends on:** Batch 02 #2.3.

### 3.6 — "Clerk"-style assistant shell
**Goal:** A dashboard chat box with an AI-answer / talk-to-attorney toggle and canned prompts.
**Acceptance criteria:**
- [ ] Chat box with toggle: instant AI answer vs. route to attorney.
- [ ] Canned prompts: Summarize this contract · Key risks · Anything unusual to ask about · Should I get a lawyer involved.
- [ ] Honest SLA line when attorneys are offline.
- [ ] **Compliance framing:** AI gives plain-English *preparation*, not legal advice; advice-level questions route to the attorney toggle.
**Depends on:** 3.4.

### 3.7 — Status-change notifications
**Goal:** Customers are emailed when a matter advances (e.g. "your review is ready").
**Acceptance criteria:**
- [ ] Email on key transitions, especially `delivered`.
- [ ] Org-scoped; no leakage across orgs.

### 3.8 — Pre-launch security review gate
**Goal:** A checklist that must pass before any real client contract flows through the portal.
**Acceptance criteria:**
- [ ] Documented scope for the one-off freelance security review (auth bypass, cross-org access, file access, secrets).
- [ ] Sign-off recorded in `DECISIONS.md` before real documents are accepted.

---

# Batch 04 — Phase 4a: AI prep engine ("the brain")

### 4.1 — Document ingestion + text extraction
**Goal:** Reliably extract clean, structured text from an uploaded `.docx` (and scanned PDFs via OCR later).
**Acceptance criteria:**
- [ ] `.docx` text + structure extracted; clauses/sections identified.
- [ ] Robust to messy formatting; clear failure handling.
**Depends on:** Batch 03 #3.1.

### 4.2 — AI prep pipeline (summary + issue list)
**Goal:** On upload, Claude produces an **internal-only** plain-English summary and an issue list, stored against the matter, moving it to `ai_review`.
**Acceptance criteria:**
- [ ] Summary + structured issue list generated and stored.
- [ ] Output is internal-only and never exposed to the customer.
- [ ] Matter transitions `intake → ai_review`.
**Compliance/security:** Internal-only enforced server-side.
**Depends on:** 4.1.

### 4.3 — Over-inclusive tracked-changes redline
**Goal:** Generate a first-pass redline in native Word tracked changes via the Claude for Word add-in, tuned for recall (suggest more; the attorney trims).
**Acceptance criteria:**
- [ ] Redline produced as native accept/reject tracked changes (not raw `python-docx`).
- [ ] Deliberately over-inclusive; attorney can delete fast.
**Depends on:** 4.2.

### 4.4 — Cover-letter deliverable
**Goal:** Generate the "what changed / why it's risky / your fallback" cover letter — the heart of the standard tier.
**Acceptance criteria:**
- [ ] Plain-English cover letter generated from the issues/redline.
- [ ] Internal-only until attorney approval.
**Depends on:** 4.3.

### 4.5 — Confidence scoring
**Goal:** Every issue and edit carries a strong/medium/weak confidence rating.
**Acceptance criteria:**
- [ ] Confidence stored per issue/edit.
- [ ] Drives attorney-workbench highlighting and routing (Batch 05/06).
**Depends on:** 4.2.

### 4.6 — Internal-only gate + queue handoff
**Goal:** AI output is sealed from customers and the matter is queued for an attorney.
**Acceptance criteria:**
- [ ] No endpoint exposes AI drafts to a customer.
- [ ] Matter moves `ai_review → attorney_queue`.
- [ ] Audit events recorded for each AI run.
**Compliance/security:** This is a core enforcement point — server-side only.
**Depends on:** 4.4.

---

# Batch 05 — Phase 4b: The Playbook system (the moat)

### 5.1 — Playbook data model
**Goal:** A structured risk/clause library per contract type, stored in Postgres (not free-text prompts).
**Acceptance criteria:**
- [ ] Tables for playbooks, contract types, and checks.
- [ ] Migrations; seedable.
**Depends on:** Batch 01 #4.

### 5.2 — Per-check schema
**Goal:** Each check captures detection, severity, remediation intent, fallback language, and accuracy.
**Acceptance criteria:**
- [ ] Fields: detection, severity tier (table-stakes/high/medium/low), remediation intent (flag vs. fix), **preferred / acceptable / unacceptable fallback language**, tracked per-check accuracy stat.
**Depends on:** 5.1.

### 5.3 — Per-client playbook overlay
**Goal:** A client's house positions sit on top of the firm-wide base library.
**Acceptance criteria:**
- [ ] Per-org overrides resolve over the base at review time.
**Depends on:** 5.2.

### 5.4 — Risk score + routing
**Goal:** Each matter gets an overall risk score used to route it.
**Acceptance criteria:**
- [ ] Risk score computed from checks.
- [ ] Low-risk fast-tracked; high-risk escalated with more attorney time.
**Depends on:** 5.2.

### 5.5 — Playbook-authoring screen
**Goal:** You/the attorney can define a policy in ~20 minutes.
**Acceptance criteria:**
- [ ] CRUD screen for checks and fallback language; usable by a non-engineer.
**Depends on:** 5.2.

### 5.6 — Wire engine to the playbook
**Goal:** The AI prep engine uses the playbook for detection, not ad-hoc prompts.
**Acceptance criteria:**
- [ ] Issues are generated against the structured checks; results reference the check that fired.
**Depends on:** 5.2, Batch 04 #4.2.

---

# Batch 06 — Phase 4c: Attorney workbench + feedback loop

### 6.1 — Attorney matter queue
**Goal:** The attorney sees what's waiting, in review, and approved, with deadlines.
**Acceptance criteria:**
- [ ] Queue/dashboard in the attorney app; the worklist = record of billable matters.
**Depends on:** Batch 01 #7, Batch 04 #4.6.

### 6.2 — Review surface (Word + Claude add-in)
**Goal:** The attorney reviews in familiar Word tracked changes with per-suggestion Apply/Dismiss + reasoning.
**Acceptance criteria:**
- [ ] Per-suggestion Apply / Dismiss; expandable reasoning per edit.
- [ ] No bespoke redline editor — use Word + the add-in.
**Depends on:** 6.1.

### 6.3 — Confidence flags front-and-centre
**Goal:** Weak-confidence issues are highlighted so the attorney looks where the AI is unsure.
**Acceptance criteria:**
- [ ] Weak items visually prioritised in the review surface.
**Depends on:** 6.2, Batch 04 #4.5.

### 6.4 — The Approve gate
**Goal:** Attorney approval is the **only** thing that moves a matter to `delivered` and releases the deliverable.
**Acceptance criteria:**
- [ ] Approve action records who/when and produces the client-ready deliverable.
- [ ] `attorney_review → delivered` impossible without a recorded approval — enforced server-side and covered by a test.
**Compliance/security:** The central compliance gate. Test it explicitly.
**Depends on:** 6.2.

### 6.5 — HuRT (attorney-minutes) capture
**Goal:** Log attorney-minutes per matter as the core margin/automation metric.
**Acceptance criteria:**
- [ ] Review time captured per matter; viewable as a trend.
**Depends on:** 6.2.

### 6.6 — Correction → playbook feedback loop
**Goal:** Each attorney correction permanently improves the playbook.
**Acceptance criteria:**
- [ ] Dismiss/edit captures a reason tag.
- [ ] The relevant playbook entry updates (fallback language / severity / detection).
- [ ] Per-check accuracy is re-tracked after corrections.
**Depends on:** 6.2, Batch 05 #5.2.

### 6.7 — Second-chair review (optional, later)
**Goal:** A two-attorney sign-off toggle for high-value matters.
**Acceptance criteria:**
- [ ] Optional second approval required when enabled.
**Depends on:** 6.4.

---

# Batch 07 — Phase 5: Scale + differentiators

### 7.1 — Slack delivery
**Goal:** Deliver and discuss matters in a shared client Slack channel.
**Acceptance criteria:** [ ] Matter delivery + updates posted to Slack; replies linked back.

### 7.2 — Email delivery automation
**Goal:** Full email delivery in addition to the portal.
**Acceptance criteria:** [ ] Automated delivery + status emails, templated and org-scoped.

### 7.3 — Smart ETAs on the status tracker
**Goal:** Replace static stages with estimated-minutes-to-next-step / delivery.
**Acceptance criteria:** [ ] ETAs computed from historical cycle times; shown under the current stage.
**Depends on:** Batch 03 #3.3.

### 7.4 — Market-benchmark ("what's market") data layer
**Goal:** Accumulate anonymised, structured clause terms to build a private benchmarking dataset.
**Acceptance criteria:** [ ] Consent/anonymisation in place; structured terms captured from every matter; data capture starts even before the client-facing feature.
**Compliance/security:** Anonymisation + consent are mandatory.

### 7.5 — MCP server (agent-facing surface)
**Goal:** An MCP server so AI assistants can upload/track/download contracts.
**Acceptance criteria:** [ ] Authenticated MCP endpoints for the core matter actions.

### 7.6 — Word add-in surface
**Goal:** A customer/attorney Word add-in for in-document workflow.
**Acceptance criteria:** [ ] Add-in connects to the backend for upload/redline/track.

### 7.7 — Internal proofreader tool
**Goal:** An internal error-checker (the FindTheFuckUp-style quality pass).
**Acceptance criteria:** [ ] Flags typos/cross-refs/defined-terms across a matter for the team.

### 7.8 — Data posture + lifecycle
**Goal:** Surface the no-train trust line and enforce retention/deletion.
**Acceptance criteria:**
- [ ] Confirm + surface "your data is never used to train public models."
- [ ] Defined retention/deletion for client documents; honoured in code.
**Compliance/security:** Confirm the Anthropic no-training agreement; honour deletion literally.

---

## Production-ready definition (end of Batch 07)
A secure, org-isolated, tested, audited platform where: customers self-serve upload→pay→track→download; the AI prepares an internal-only summary, issue list, redline, and cover letter scored by confidence and driven by a structured playbook; an attorney reviews in Word and is the sole gate to delivery; every correction compounds into a better playbook; and delivery, benchmarking, and agent surfaces are live. Plus the one-off security review passed (Batch 03 #3.8) and the compliance model confirmed with counsel. That is production-ready.
