# Charter Law — Master Build Super-Prompt

> **What this is:** the single authoritative build brief for Charter Law's software. It folds everything learned from the competitor research (`Competitors.md`, `general-legal-dossier.md`) — the playbook system, attorney workbench, status tracker, "Clerk"-style assistant, and the feedback loop — plus the features competitors *haven't* nailed, into one spec you can drive Claude Code from.
>
> **How to use it:** Part F at the bottom is the copy-paste prompt for Claude Code. Parts A–E are the reference spec it points to. Build phase by phase (Part E) — never paste the whole thing and say "build it all." Feed Claude Code one phase at a time, test, then move on.
>
> **Aligns with:** `charter-law-roadmap.md` (phases), `charter-law-tech-stack.md` (stack), `charter-law-operating-playbook.md` (economics/compliance). Where this doc adds something new beyond those, it's flagged **[NEW]**.
>
> Status: DRAFT v1. Get the one-off security review (roadmap §2) before any real client contract flows through this.

---

## Part A — Context & non-negotiables (the rules every feature obeys)

- **What we're building:** an AI-native, **attorney-reviewed** flat-fee contract-review service for founders/startups/SMBs. AI prepares; a licensed attorney approves and owns every output.
- **The single non-negotiable:** **AI prepares. An attorney approves and owns.** No AI output reaches a customer as legal advice. A matter cannot reach `delivered` without a recorded attorney approval. This is enforced **in the backend**, not just the UI.
- **Who's building:** Rhys — solo, non-technical, vibe-coding with Claude Code. One **per-matter** reviewing attorney (cost-of-goods, not salaried). No developer. So: build in **small, testable steps**, behind preview deploys, with a decisions log.
- **The committed stack (do not re-litigate):** Webflow (marketing) · Vite + React + TypeScript (customer portal + attorney app) · Python + FastAPI (backend) · PostgreSQL via Cloud SQL · Clerk (auth, org-based) · Stripe (hosted checkout) · Google Cloud Storage (files) · Anthropic Claude (AI) · Claude for Word add-in (redlines) · Google Cloud Run (hosting) · Cloudflare · Sentry. Python pkg mgmt with `uv`; migrations with Alembic + SQLAlchemy.
- **The set of apps (five surfaces, one backend):** (1) marketing site, (2) customer portal, (3) attorney app, (4) backend "brain," (5) database — plus a free lead-gen tool, and later a Word add-in + MCP server.
- **Jurisdiction / scope to assume:** California-first; first practice area = commercial contracts (NDAs, MSAs, vendor/DPA agreements). Narrow and repeatable.
- **The matter lifecycle (the spine of the whole system):**
  `intake → ai_review → attorney_queue → attorney_review → delivered → completed`

---

## Part B — The complete feature map (what to build, surface by surface)

This is the full target picture. Most of it is already in the roadmap; the **[NEW]** items are the additions from the competitor/playbook/workbench research that the roadmap under-specifies.

### B1. Marketing site (Webflow) — Phase 2
- Plain-English offer, flat-fee pricing tiers, one clear "Send us a contract" CTA, social proof slot.
- All claims (speed, "attorney-reviewed," pricing) attorney-reviewed for advertising-rule compliance. Say "your **reviewing attorney**," not "our lawyers," until the firm structure supports it.

### B2. Free lead-gen tool — "Contract Mistake Checker" — [NEW as a built priority] (Phase 2–3)
Modelled on General Legal's "Find The Fuckup" (which they open-sourced).
- Drag-drop a `.docx` → free AI pass that surfaces **typos, broken cross-references, defined-terms-never-used, missing sections** (the cheap, high-credibility errors). Output a short, shareable report.
- Hard privacy reassurance on the page: **"We never save or store your contract."** Process in memory, don't persist the file.
- Ends with a CTA to a paid review. This is a top-of-funnel lead magnet, not the core product — keep it isolated from the main app.

### B3. Customer portal (Vite + React + TS) — Phase 3
- Clerk org-based login; upload `.docx`; pay (Stripe hosted checkout); download the deliverable; manage billing. A customer only ever sees their own organisation's matters (enforced server-side).
- **Domino's-style status tracker** — [confirmed real at General Legal] — a horizontal progress bar across the five lifecycle stages (**Received → AI Review → Queued for Attorney → Attorney Review → Delivered**), each lighting up as it completes, with an **estimated-minutes-to-next-step / delivery** under the current stage. Matter list columns: **File name · Versions · Status · Submitted.** Sell *predictability*. (Build the basic version of this in Phase 3 even before ETAs are smart — a static stage bar is enough to start.)
- **"Clerk"-style assistant** — [NEW] — a single chat box on the dashboard: "Ask the AI for an instant answer, or toggle to **Attorney** and a lawyer will respond." Canned prompts: *Summarize this contract · What are the key risks? · Anything unusual I should ask about? · Should I get a lawyer involved?* Include an honest SLA line when attorneys are offline (e.g. "lawyers reply by 8am ET"). **Compliance rule:** the AI side gives general/plain-English information framed as *preparation*, not legal advice; anything that crosses into advice routes to the attorney toggle.

### B4. AI prep engine ("the brain") — Phase 4
- On upload, Claude automatically produces, **internally only**: (a) a plain-English summary, (b) an **issue list**, (c) a first-pass **tracked-changes redline**, and (d) a draft **"what changed / why it's risky / your fallback" cover letter** (this cover letter is the core of the $500 standard tier). Never shown to the customer until the attorney approves.
- **Deliberately over-inclusive redlines** — [NEW, from General Legal] — the AI should suggest *more* than needed; it's faster for the attorney to delete than to add. Tune the prompt for recall over precision.
- **Field/issue-level confidence scoring** — [NEW, from Manifest/Crosby] — every issue and edit carries a confidence rating (**strong / medium / weak**). This drives both the attorney workbench (where to look) and routing (below).
- Redlines come from the **Claude for Word add-in** (native tracked changes), not raw `python-docx`.

### B5. The Playbook system — the moat — [NEW, mostly absent from current roadmap] (Phase 4, then deepened in 5)
This is where quality and margin actually come from. Tilder's data: the playbook drives **+40 percentage points of accuracy** from ~15–20 minutes of setup, versus ~+2 points from a better model. Build it as a first-class system, not a prompt afterthought.
- **A risk/clause library** — a structured catalogue of the things to check in each contract type (NDA, MSA, vendor/DPA). Each entry has:
  - a **detection** (is this clause present / how is it framed?),
  - a **severity tier** (table-stakes / high / medium / low),
  - a **remediation intent** (flag-only vs. propose a fix),
  - **preferred / acceptable / unacceptable fallback language** — [NEW, the schema *no competitor publicly published* — a genuine differentiator if done well],
  - a tracked **accuracy stat** per check (how often the AI gets this one right).
- **Per-client playbooks layered on a firm-wide base** — a client's risk tolerance / house positions sit on top of the shared library.
- **An overall contract risk score** per matter, used for **routing** (auto-fast-track low-risk; escalate high-risk to the attorney with more time).
- **A simple playbook-authoring screen** for you/the attorney (target ~20 min to define a policy). Stored as structured data in Postgres — not free-text prompts.

### B6. Attorney workbench (separate internal React app) — Phase 4
The attorney's cockpit. Mirror General Legal's separate `lawyers.` app.
- **Matter queue / dashboard** — what's waiting, in review, approved; deadlines; the attorney's worklist (also the record of completed = billable matters).
- **Review surface = Word + the Claude add-in** — [confirmed approach] — the attorney works in familiar Word tracked changes, with per-suggestion **Apply / Dismiss** and an expandable **reasoning** for each proposed edit. Don't build a bespoke redline editor.
- **Confidence flags front-and-centre** — [NEW] — weak-confidence issues are highlighted so the attorney spends time only where the AI is unsure (this is what keeps **attorney-minutes-per-matter** — your margin number — low).
- **The Approve gate** — approval is the *only* thing that moves a matter to `delivered`. Enforced server-side.
- **Capture Human Review Time (HuRT)** — [NEW, from Crosby] — log attorney-minutes per matter as the core automation-progress / margin metric.
- (Later) **second-chair / two-attorney review** toggle for higher-value matters.

### B7. The feedback loop — [NEW, the thing almost nobody nails] (Phase 4–5)
Make each attorney correction permanently improve the system (Tilder's loop, done explicitly):
- When the attorney dismisses/edits an AI suggestion, capture **why** (a quick reason tag).
- That correction updates the relevant **playbook entry** (e.g. adjust fallback language, change severity, refine the detection) — not just the single contract.
- Re-run, confirm the **per-check accuracy** went up, log it.
- Result: corrections compound into a better playbook over time. This is the moat that strengthens with volume.

### B8. Delivery channels — Phase 5
- **Slack** integration (deliver + discuss matters in a shared client channel) and **email** automation, in addition to the portal. (General Legal, Moritz, Compound all lead with Slack/email — low friction, cheap.)
- **Word add-in** and **MCP server** as later differentiators (General Legal was first to ship an MCP server).

### B9. Market-benchmark data layer — "what's market" — [NEW, a compounding moat] (Phase 5+)
- Quietly accumulate **anonymised, structured terms** from every matter (with the right consent/anonymisation) to build a private dataset of "what's market" for each clause type.
- This powers better fallback recommendations over time and a future client-facing benchmarking feature (Covenant does this for fund terms; nobody owns it for startup commercial contracts yet). Build the data capture early even if the feature comes later.

---

## Part C — Features/elements to ADD beyond the current roadmap (the punch-list)

Quick checklist of everything **[NEW]** above, so nothing is lost when finishing the roadmap:

1. **Playbook system as a first-class build** (risk library + severity tiers + preferred/acceptable/unacceptable fallback language + per-check accuracy + per-client overlay + risk score routing). *The single biggest addition.*
2. **The correction→playbook feedback loop** (reason-tagged corrections that update the playbook and track accuracy).
3. **Field/issue-level confidence scoring** surfaced to the attorney (where to look) and used for routing.
4. **Domino's-style status tracker** with estimated-minutes-to-next-step (predictability as a selling point).
5. **"Clerk"-style AI/attorney-toggle assistant** in the portal, with compliance-safe framing.
6. **Free "Contract Mistake Checker"** lead-gen tool with a no-storage privacy promise.
7. **Deliberately over-inclusive AI redlines** (recall over precision; attorney trims down).
8. **The cover-letter deliverable** ("what changed / why risky / your fallback") as the heart of the standard tier.
9. **HuRT (attorney-minutes-per-matter) capture** as the core margin/automation metric.
10. **Market-benchmark ("what's market") data capture** from day one — a compounding data moat.
11. **No-train data posture** — confirm an Anthropic API/no-training agreement and surface "your data is never used to train public models" as a trust line.
12. **Second-chair review** option (later) for high-value matters.

---

## Part D — Production-readiness requirements (non-negotiable for going live)

- **Security & data isolation** — every backend request verifies the Clerk session server-side; all data scoped to the requesting organisation; one client can never see another's files. Files in Cloud Storage with only references in the DB; least-privilege access. **Get the one-off freelance security review before the first real client contract** (roadmap §2).
- **Confidentiality & privilege** — customer documents are confidential legal material. Encrypt in transit and at rest; keep real client docs out of any test environment; no secrets in code or git (environment variables only).
- **Compliance gates baked into code** — the `delivered` transition requires a recorded attorney approval; the portal/assistant never present AI output as legal advice; marketing/portal copy stays truthful and attorney-reviewed. (Confirm the full compliance model — UPL, Rule 5.4 fee-sharing, advertising — with your attorney; see `charter-law-operating-playbook.md` §9.)
- **Auditability** — an events/audit table records who did what when (uploads, AI runs, attorney approvals). Important for an attorney-accountable business.
- **Payments** — Stripe hosted checkout only; never handle card data yourself.
- **Observability** — Sentry on every surface; basic structured logging in the backend.
- **Data lifecycle** — define retention/deletion for client documents; honour the free tool's "we never store your contract" promise literally (process in memory, persist nothing).
- **Test discipline** — automated tests against a throwaway test DB; preview deploys you click-test before promoting.

---

## Part E — Build sequencing (maps the new features onto the existing phases)

- **Phase 0 — Foundation:** attorney engaged per-matter; entity/compliance structure blessed; all accounts under the business identity. *(No code.)* **Add:** confirm the Anthropic no-training data posture here.
- **Phase 1 — Manual MVP:** deliver to 3–10 paying clients using Word + Claude add-in + Drive + Stripe links. **Add:** start hand-writing the **playbooks** (B5) and logging **attorney-minutes per matter** (B6) from the very first manual matter — this data designs the software.
- **Phase 2 — Marketing site + intake:** Webflow + Stripe + intake form. **Add:** ship the **free Contract Mistake Checker** (B2) as a lead magnet.
- **Phase 3 — Customer portal v1:** auth, upload, status, download, pay. **Add:** the **status tracker** (B3, static stages first) and the **"Clerk" assistant** (B3) shell. **→ Security review here.**
- **Phase 4 — AI engine + attorney workbench:** the prep engine (B4), the **playbook system** (B5), the **attorney workbench** with confidence flags + approve gate (B6), and the first version of the **feedback loop** (B7). **This is the core of the moat — spend the most care here.**
- **Phase 5 — Scale + differentiators:** Slack/email delivery (B8), smart ETAs on the tracker, the **market-benchmark data layer** (B9), MCP server + Word plugin, deepened feedback loop, second-chair review.

---

## Part F — The copy-paste super-prompt for Claude Code

> Paste this at the start of a Claude Code session, then ask it to build **one phase at a time**. Replace `[PHASE]` with the phase you're on. It references the three companion docs — keep them in the repo so Claude Code can read them.

```
You are my senior engineering partner building Charter Law, an AI-native, attorney-reviewed
flat-fee contract-review service for startups. I am a non-technical solo founder; you write the
code, explain choices simply, and work in small, testable steps behind preview deploys.

READ FIRST (in the repo): charter-law-roadmap.md, charter-law-tech-stack.md,
charter-law-super-prompt.md, and Competitors.md. Treat charter-law-super-prompt.md as the
authoritative feature spec and charter-law-tech-stack.md as the authoritative stack.

THE ONE RULE THAT OVERRIDES EVERYTHING:
"AI prepares; an attorney approves and owns." No AI output is ever presented to a customer as
legal advice. A matter can NEVER move to `delivered` without a recorded attorney approval —
enforce this in the backend, not just the UI.

STACK (do not substitute): Vite + React + TypeScript (customer portal + separate attorney app);
Python + FastAPI backend (uv, Alembic + SQLAlchemy); PostgreSQL on Cloud SQL; Clerk org-based
auth (verify the session on EVERY backend request, scope all data to the requesting org);
Stripe hosted checkout; Google Cloud Storage for files; Anthropic Claude for AI; Claude for Word
add-in for tracked-changes redlines; Google Cloud Run hosting; Cloudflare; Sentry.

MATTER LIFECYCLE: intake → ai_review → attorney_queue → attorney_review → delivered → completed.

PROJECT STRUCTURE: follow the layout in charter-law-tech-stack.md (frontend/ feature-organised;
attorney-app/; backend/ with routers/services/models/schemas/ai; thin routes + service layer;
SQLAlchemy models separate from Pydantic schemas; secrets in env vars only; Alembic for every
schema change; tests against a throwaway test DB).

KEY FEATURES TO BUILD (per charter-law-super-prompt.md Part B): the AI prep engine producing an
internal-only summary + issue list + over-inclusive tracked-changes redline + a "what changed /
why risky / your fallback" cover letter, each issue carrying a strong/medium/weak confidence
score; a structured PLAYBOOK system (risk library with severity tiers, remediation intent,
preferred/acceptable/unacceptable fallback language, per-check accuracy, per-client overlay,
overall risk score for routing); an ATTORNEY WORKBENCH (matter queue, Word + Claude-add-in
review with Apply/Dismiss + reasoning, confidence flags highlighted, an Approve gate that alone
releases to the client, and HuRT/attorney-minutes capture); a correction→playbook FEEDBACK LOOP
(reason-tagged corrections update the playbook and track accuracy); a customer portal with a
Domino's-style status tracker (5 stages + ETA) and a "Clerk" assistant (AI-answer / talk-to-
attorney toggle, compliance-safe framing).

PRODUCTION-READINESS (Part D): org-scoped data isolation, encryption, an events/audit table,
Stripe hosted checkout only, Sentry everywhere, honour "we never store your contract" literally
for the free tool. Flag clearly any step where security mistakes would be serious so I can get a
one-off security review before real client contracts flow through.

We are building [PHASE] now. Propose the smallest first slice, list exactly what you'll create or
change, wait for my go-ahead, then build it with tests and tell me how to click-test it. Ask me
when a decision is mine (jurisdiction, pricing, attorney workflow) rather than guessing.
```

---

### Companion docs
`charter-law-roadmap.md` · `charter-law-tech-stack.md` · `charter-law-operating-playbook.md` · `Competitors.md` · `general-legal-dossier.md`

*Not legal advice. All compliance items (UPL, Rule 5.4 fee-sharing, attorney advertising, the per-matter attorney structure, the no-training data posture) must be confirmed with your reviewing attorney before launch.*
