# Charter Law — Build Roadmap

> Working name: **Charter Law** (domain: `charterlaw.services`). Treated as settled for now.
> Owner: Rhys — **solo founder, non-technical but good at vibe-coding** (building the software himself with Claude Code / AI assistance, no separate developer).
> Legal: one **reviewing attorney, paid per completed matter** (a contractor / cost-of-goods, not a salaried hire).
> Status: **BUILDING** — living document. The engineering foundation is now merged to `main` (see Build Progress below).

---

## Build Progress (live) — updated 1 July 2026

**Merged to `main` (`bdf55bb`), 51 backend tests passing, CI green (backend + frontend).**

In `main` now (foundation + Batches 02-04):
- **Backend**: guarded matter lifecycle; org-scoped access; **attorney-only workspace** (queue + approval + AI-prep view), approval no longer in the customer API; **internal-only AI prep engine** (summary + issue list, Anthropic behind a safe stub); **playbook data model**; Stripe checkout + webhook; signed upload/download URLs; audit trail + read/report endpoints; typed config validation (fails closed); liveness + readiness probes; **notifications**, **retention/privacy**, **public-endpoint hardening** (rate-limit + size caps).
- **Lead-gen**: free Contract Mistake Checker (stores nothing) + public intake.
- **Frontend**: customer portal (upload -> status -> download), attorney page, admin, landing; env-guarded Sentry.
- **Observability/deploy**: request logging, env-guarded Sentry (BE+FE), Dockerfiles + Cloud Run recipe.
- **Packaging fixed**; CI runs backend tests + frontend build on every push/PR.

Invariants enforced + tested: AI never shown to customers as legal advice; delivery requires attorney-role approval; org isolation everywhere; fail-closed auth; signed-only file URLs; free checker stores nothing; AI prep is attorney-only.

### Gates still standing before "production ready"
1. **The moat**: playbook-DRIVEN AI prep + the attorney feedback loop + redline/cover-letter deliverable (Batch 05).
2. **Real Anthropic integration** wired behind the key (still internal-only).
3. **Real accounts + actual deploy** (Cloud Run/SQL/GCS/Clerk/Stripe/Sentry secrets).
4. **Retention completion** — delete the actual GCS objects, not just DB refs (Batch 05 #1).
5. **The one-off security review**; **the legal foundation** (attorney engaged + structure confirmed).

Next build step: **Batch 05** (`build-system/generated-issues/batch-05-next-nine.md`) — playbook-driven AI, feedback loop, redline + cover letter, confidence/routing, attorney workbench v2.

---

## 0. What we are building (the one-paragraph version)

Charter Law is an **AI-native, attorney-reviewed contract-review service** for founders, startups, and small businesses. A customer sends us a contract; AI does the routine first pass (intake, plain-English summary, issue-spotting, first-draft redlines); a **licensed attorney reviews, applies judgment, and owns every output** that goes back to the customer. We charge **flat fees** with **fast turnaround** (target: first turn in a few hours, not days). It is a legal *service* with AI leverage underneath — **not** a self-serve legal chatbot.

We are deliberately modelling the technology and operating playbook on **General Legal (YC W26)**, adapted to a **one-person, AI-built** start.

### The single non-negotiable principle
**AI prepares. An attorney approves and owns.** No AI output ever reaches a customer as legal advice. AI work is *internal preparation* until a barred attorney has reviewed and approved it. A matter cannot reach "delivered" without explicit attorney sign-off. Every phase below is built around this.

---

## 1. The operating model (read this first — it shapes everything)

This is a **lean, two-person operation**:

- **You** 🧑‍💼 — run the business and **build all the software yourself by vibe-coding with Claude Code**. You're non-technical but capable of driving AI to produce working software in small, tested pieces. You own product, marketing, sales, intake, and the build.
- **A reviewing attorney** ⚖️ — a barred lawyer who reviews and approves every legal deliverable, **paid per completed matter**. They are your cost-of-goods: when a job comes in and gets delivered, they get paid for that job. No matters, no attorney cost. This keeps your overhead near zero until revenue is real.

There is **no developer to hire or manage**. That removes your single biggest cost and bottleneck — but it means *you* are the engineering team, so the roadmap is paced for one person building with AI, and it's honest about the few places where vibe-coding alone isn't enough (see Section 2).

There are **two tracks**, and the legal one gates the technical one:

| Track | What it covers | Who |
|-------|----------------|-----|
| **Legal / Operations** | Attorney, entity, compliance, engagement letters, actual service delivery | You + Attorney |
| **Technology** | Website, portal, backend, AI pipeline, attorney app | You (with Claude Code) |

**You cannot legally deliver contract review without the attorney foundation** — so no amount of software matters until Phase 0 is done. Build the business first, automate it second.

Each phase lists: **Goal · What gets built · Depends on · Done =**.
Owner key: 🧑‍💼 You (founder, building with Claude Code) · ⚖️ Attorney (per matter) · 🤖 Claude/AI

---

## 2. Vibe-coding this safely (the honest part)

Vibe-coding with Claude Code will genuinely get you most of the way: the marketing site, the customer portal, the matter workflow, the AI prompts, and the attorney app are all well within reach for a determined non-technical founder driving AI carefully, in small pieces, testing as you go.

But this business handles **other people's confidential legal contracts and takes payments**, so two areas deserve more respect than a casual vibe-coding pass:

1. **Security & data isolation** — making sure one customer can never see another's documents, that logins can't be bypassed, and that contract files are stored securely. Claude Code can build this correctly, but mistakes here are serious (confidentiality is an attorney obligation, not just good manners).
2. **Payments** — handled by Stripe's hosted tools wherever possible, so you're not building sensitive payment handling yourself.

**Recommended safeguard:** before you accept your *first real client contract* through the software (Phase 3+), pay for a **one-off security review** from a freelance engineer (a few hours of someone's time on a platform like a vetted contractor marketplace). It's a small, one-time cost that protects you from the one category of mistake that actually matters. This isn't hiring a developer — it's a checkup. Everything else, you build.

Practical habits that make solo vibe-coding work: build in **small, testable steps**; use **preview deploys** so you can click and test each change before it's live; keep a **decisions log** (`charter-law-decisions.md`) so you and Claude Code stay oriented across sessions; never paste secrets into code; and keep real customer documents out of any test environment.

---

## 3. Architecture

Charter Law is built on the **General Legal stack** — a React single-page frontend, a Python/FastAPI backend, and a PostgreSQL database, hosted on Google Cloud. We mirror General Legal because matching a proven, well-funded competitor's architecture is the lowest-risk path, and because Python is the strongest ecosystem for the AI- and Word-document-heavy work at the core of this business. Full per-layer detail lives in **`charter-law-tech-stack.md`**; the summary is in Section 4.

The system is **five surfaces sharing one backend**: a marketing site, a customer portal, an attorney review app, the backend "brain," and the database. The same backend later serves the Word plugin and the MCP server too — exactly the set of surfaces General Legal runs.

Two tooling notes for when you're building:
- **Hosting is Google Cloud Run** (General Legal uses the older App Engine). Cloud Run is Google's recommended choice for new projects in 2026 — same FastAPI code in a container, scales to zero so it's cheap when idle, and avoids App Engine's one-app-per-project limit.
- **Redlines come from the Claude for Word add-in**, not raw `python-docx`. That library can't produce true Word tracked changes, so we rely on the Word add-in — which outputs native accept/reject redlines — exactly as General Legal does, so the attorney works in familiar Word markup.

*(An earlier prototype existed on Next.js + Convex. We're not continuing on it — reuse its landing-page copy and design ideas only, and build the engine on the stack above.)*

---

## 4. Target tech stack (short version — full detail in `charter-law-tech-stack.md`)

| Layer | General Legal uses | Charter Law choice |
|-------|--------------------|--------------------|
| Marketing site | Webflow | Webflow (`charterlaw.services`) |
| Customer portal | Vite + React + TS | Vite + React + TypeScript |
| Attorney app | Separate internal app | Separate internal app (same stack) |
| Backend API | Python + FastAPI | Python + FastAPI |
| Database | PostgreSQL | PostgreSQL (Google Cloud SQL) |
| Auth | Clerk | Clerk (organisation-based) |
| Payments | Stripe | Stripe (hosted checkout) |
| File storage | (Google Cloud) | Google Cloud Storage |
| AI / LLM | Anthropic Claude | Anthropic Claude |
| Doc engine | python-docx + Word plugin | Claude for Word add-in (+ redline tooling) |
| Hosting | Google App Engine | Google **Cloud Run** |
| CDN / DNS | Cloudflare | Cloudflare |
| Monitoring | Sentry | Sentry |
| Analytics | Segment | Segment (add later) |
| Agent interface | MCP server | MCP server (later phase) |
| Email | Google Workspace | Google Workspace |

---

## 5. The phases

### Phase 0 — Foundation: legal + identity + accounts (the real starting line)
**Goal:** Be legally and operationally able to take on a paying contract-review client, with a clean business identity. **No customer-facing software yet.**

**What gets done:**
- **Business identity** 🧑‍💼 — business Google Workspace account, a dedicated Chrome profile signed into it, and Claude Code signed up under the business email (not personal). *(In progress.)*
- **Attorney foundation** ⚖️🧑‍💼 — the heart of Phase 0. Engage at least one **California-barred reviewing attorney on a per-matter (paid-per-completed-job) basis**. Agree the per-matter rate and turnaround expectations. Get engagement-letter / scope-of-work templates drafted. Confirm professional liability (malpractice) insurance. Have a real lawyer pressure-test the model against **UPL**, **Rule 5.4 (fee-sharing / non-lawyer ownership)**, and **attorney-advertising** rules.
- **Corporate / compliance structure** ⚖️🧑‍💼 — decide with counsel, and **stage it**:
  - **For the first ~10 clients (start here — lowest risk):** Charter Law is the **branded intake + AI-prep + operations layer**; the **reviewing attorney's own practice/firm is the legal provider**; the **customer engages the attorney directly** before any advice is delivered; and **Charter Law is paid a separate, fixed workflow/vendor fee — not a percentage of the legal fee** (a cut of legal fees risks improper fee-sharing). This keeps you onside California **B&P Code §6125** (only barred lawyers practise law), **Rule 5.4** (no fee-sharing / non-lawyer control), **Rule 5.3** (lawyer supervises non-lawyer help), and **Rule 7.1** (no false/misleading copy). You are *not* a law firm yet — don't say "our lawyers"; say "your **reviewing attorney**" and "AI prepares the work; a licensed attorney reviews and approves."
  - **Later, at scale (only after demand is proven):** move toward the **two-entity "Atrium model"** — a **lawyer-owned law firm** (client relationship, bar license, malpractice, legal judgment) **+ a separate technology/operations company** (Charter Law — software, IP, capital). This is how funded AI-native firms like General Legal structure around Rule 5.4 / ABS limits long-term.
  - *(Full detail in `charter-law-operating-playbook.md` §9. Not legal advice — the staged model to take to a California attorney.)*
- **Brand basics** 🧑‍💼 — Charter Law name, `charterlaw.services` domain, a simple logo/wordmark, one paragraph of positioning.
- **Core accounts** 🧑‍💼 — GitHub, Google Cloud project, Cloudflare, Clerk, Stripe, Sentry, Anthropic API — all under the business identity, secrets in a password manager (never in code).

**Depends on:** nothing — this is the start.
**Done =** an attorney is contractually ready to review matters per-job under a structure a lawyer has signed off on; business identity and all core accounts exist and are owned by the business.

> ⚠️ The phase people skip because it's not fun. Don't. The technology is worthless without the attorney. **If you only do one thing this month, line up the per-matter reviewing attorney.**

---

### Phase 1 — Manual MVP: sell and deliver before you build
**Goal:** Deliver the actual service to real paying customers using **off-the-shelf tools only**. Prove the model and pricing before building any custom software.

**What gets done:**
- **Manual delivery workflow** 🧑‍💼⚖️🤖 — customer sends a contract by email; you produce a first-pass summary, issue list, and redline using Claude + the Claude Word plugin; the attorney reviews, edits, and approves; you deliver the final redline. Tools: Word + Claude Word plugin, a shared Google Drive, a simple intake form.
- **Pricing** 🧑‍💼 — set flat-fee tiers (General Legal's public anchors: ~$250 simple review, $500 standard, $1,000 full negotiation, $2,000 drafting). **Make the $500 "standard" tier = a clean redline + one revision + a "what changed / why it's risky / your fallback" cover letter — not negotiation.** General Legal learned most clients want exactly this and close the deal themselves; reserve full negotiation (unlimited turns + counterparty calls) for the $1,000 tier. Price *on value*, not cost-plus, and make sure every tier covers the attorney's per-matter fee + tooling + margin. Take payment with **Stripe payment links** — no portal needed yet.
- **Target the right client (ICP)** 🧑‍💼 — growth-stage startups with real contract volume but no full-time GC (roughly Series A–B); not pre-seed, not big-corp in-house teams. Narrow + repeatable is what makes flat fees and consistency work.
- **Cap your pilots** 🧑‍💼 — deliberately keep the first cohort small (3–10). The "early-demand trap" (YC) is real: too many clients too fast buries a solo operator in manual work and you never build the leverage. Use the first few to learn where AI gives real leverage and to write the playbooks.
- **Measure everything** 🧑‍💼 — cycle time, **attorney-minutes per matter** (your key leverage/margin number), what customers ask for, what AI gets right/wrong. This data designs the software *and* validates your margins.
- **Start the playbook by hand** 🧑‍💼⚖️ — from the very first manual matter, write down per contract type: what to check, severity, and preferred/acceptable/unacceptable fallback language. This becomes the structured Playbook system in Phase 4 — and it's the moat, so start it now even on paper.

**Depends on:** Phase 0 (attorney must be in place).
**Done =** a repeatable, written delivery workflow; **3–10 paying customers**; first revenue; documented turnaround and per-matter economics. The most important milestone in the whole roadmap — it proves the business works before you build anything. *(See `charter-law-operating-playbook.md` for the full operating model behind this phase.)*

---

### Phase 2 — Marketing site + intake
**Goal:** A public website that takes a customer from "never heard of you" to "paid and submitted a contract."

**What gets done:**
- **Webflow marketing site** 🧑‍💼 on `charterlaw.services` — clear plain-English copy, pricing tiers, social proof as it accumulates, one obvious "Send us a contract" call to action. Cloudflare in front for DNS/CDN. (Webflow is no-code, so this is you, not vibe-coding.)
- **Intake + payment** 🧑‍💼 — Stripe checkout + a lightweight intake form (a form that emails you + a Stripe link) so the site converts.
- **Truthful copy** ⚖️ — the attorney reviews all claims (turnaround, "attorney-reviewed", pricing) so nothing is misleading or crosses advertising rules.
- **Free "Contract Mistake Checker" lead magnet** 🧑‍💼🤖 — drag-drop a `.docx` → a free AI pass surfacing typos, broken cross-references, unused defined terms, missing sections, ending in a CTA to a paid review. Hard privacy promise: **"We never save or store your contract"** — process in memory, persist nothing. Keep it isolated from the main app. (Modelled on General Legal's open-sourced "FindTheFuckUp"; super-prompt B2.)

**Depends on:** Phase 1 (real pricing + proof + a working manual process behind the site).
**Done =** a stranger can land on the site, understand the offer, pay, and submit a contract — even if everything behind the form is still manual.

---

### Phase 3 — Customer portal v1 (your first real vibe-coding build)
**Goal:** Customers self-serve: sign up, upload a contract, watch its status, download the finished redline, and pay — without you doing it by hand.

**What gets built (you, with Claude Code):** 🧑‍💼🤖
- **Frontend** — Vite + React + TypeScript single-page app. Clerk handles login (organisation-based, so a company can have several users). Customer can: create an account, upload a `.docx` contract, see matter status, download the deliverable, manage billing.
- **Backend** — Python + FastAPI on Google Cloud Run. PostgreSQL (Cloud SQL) for users, organisations, matters, files. File storage in Google Cloud Storage. Stripe for billing.
- **The matter lifecycle:** `intake → ai_review → attorney_queue → attorney_review → delivered → completed`
- **Status tracker (Domino's-style)** 🧑‍💼🤖 — a horizontal progress bar across the five stages (Received → AI Review → Queued for Attorney → Attorney Review → Delivered), each lighting up as it completes. Build the **static-stage version now** (smart ETAs come in Phase 4). Sells *predictability*.
- **"Clerk"-style assistant (shell)** 🧑‍💼🤖 — a single dashboard chat box with an **AI-answer / talk-to-attorney toggle** and canned prompts (summarise, key risks, anything unusual, should I get a lawyer involved). Compliance-safe framing: the AI gives plain-English *preparation*, not legal advice; advice-level questions route to the attorney toggle, with an honest offline-SLA line.
- **Security baseline** — every API request verifies the Clerk session on the server; a customer only ever sees their own matters; secrets in environment variables. **→ This is the build to get the one-off security review on (Section 2) before any real client uploads a contract.**

**Depends on:** Phase 2.
**Done =** a real customer can, end to end and unaided, sign up → upload → track → download → pay, for an actual matter (even while the AI + attorney steps in the middle are still partly manual), **and** the security review has passed.

---

### Phase 4 — AI prep engine + attorney workbench
**Goal:** Automate the internal first pass and give the attorney a fast review-and-approve cockpit. This is where the "AI-native" leverage shows up.

**What gets built (you, with Claude Code):** 🧑‍💼🤖⚖️
- **AI prep pipeline ("the engine")** — on upload, Claude automatically produces a plain-English summary, an issue list, and a first-pass **tracked-changes redline** in Word. General Legal calls their version "Sentinel." **Strictly internal — never shown to the customer until the attorney approves.**
  - *Build note:* plain `python-docx` can't produce true Word tracked changes. Real accept/reject redlines need either a structured approach (Claude outputs proposed edits as data, then a tool like open-source `legal-redline-tools` renders native markup) or the **Claude for Word add-in**, which outputs native tracked changes directly. Lean on the Word add-in first — it matches how the attorney already works.
- **Attorney app** — a separate internal app (mirroring General Legal's `lawyers.` app) where the attorney sees their queue, reviews the AI draft, edits the redline in Word, and clicks **Approve**. Approval is the gate that moves the matter to `delivered`. Because the attorney is paid per completed matter, this app is also effectively their worklist and the record of completed jobs.
- **The Playbook system (the moat)** 🧑‍💼🤖 — a structured risk/clause library per contract type: each check has a detection, a **severity tier**, a remediation intent, **preferred / acceptable / unacceptable fallback language**, and a tracked per-check accuracy stat; plus per-client overlays on a firm-wide base and an overall **risk score that routes matters**. Stored as **structured data in Postgres**, not free-text prompts. (Competitor evidence — Tilder — says the playbook drives ~+40 points of accuracy from ~20 min of setup vs ~+2 from a better model. Build it first-class.)
- **Confidence scoring + feedback loop** 🤖⚖️ — every AI issue/edit carries a strong/medium/weak confidence rating (so the attorney looks where the AI is unsure). When the attorney dismisses/edits a suggestion, capture *why* and **update the playbook entry** so corrections compound into accuracy. Log **attorney-minutes per matter (HuRT)** as the core margin metric.
- **Status polish** — live "estimated time to delivery" tracker (General Legal's "Domino's-pizza" feature).

**Depends on:** Phase 3.
**Done =** AI generates the first pass automatically; the attorney reviews and approves in-app; **approval — and only approval — releases the work to the customer**; corrections feed back into the playbook. *(Full feature spec: `charter-law-super-prompt.md` Parts B4–B7 — the core of the moat; build with the most care.)*

---

### Phase 5 — Scale, polish, and differentiators
**Goal:** Handle volume with low overhead, and add the features that made General Legal notable.

**What gets built (you, with Claude Code):** 🧑‍💼🤖
- **Delivery channels** — Slack integration (deliver and discuss matters in a shared channel), email automation.
- **Throughput** — batch uploads, billing automation, customer API keys, and — if attorney volume grows — adding a second per-matter attorney to the same queue.
- **Quality tooling** — an internal proofreader / error-checker (General Legal open-sourced theirs as "FindTheFuckUp" — Flask + Claude + python-docx + Postgres). *(The public-facing version of this is the free "Contract Mistake Checker" lead magnet — ship that earlier, in Phase 2–3; see super-prompt B2.)*
- **Market-benchmark ("what's market") data layer** 🤖 — quietly accumulate anonymised, structured clause terms from every matter (with consent/anonymisation) to build a private "what's market" dataset that improves fallback recommendations and powers a future client-facing benchmarking feature. **Start the data capture early even though the feature comes later** — it's a compounding moat (Covenant does this for fund terms; no one owns it for startup commercial contracts).
- **Analytics + monitoring** — Segment + Sentry.
- **Second-chair review** — optional two-attorney sign-off toggle for higher-value matters.
- **Agent-facing surface** — an **MCP server** so AI assistants can upload/track/download contracts, plus a Word plugin. Later-stage differentiators, not early priorities.

**Depends on:** Phase 4 + real volume justifying the work.
**Done =** the operation processes dozens of matters per week without proportional manual overhead.

---

## 6. Rough timeline (one founder vibe-coding + a per-matter attorney)

| Phase | Rough timing | Gated by |
|-------|--------------|----------|
| 0 — Foundation | Weeks 0–3 | Attorney engaged (per-matter) |
| 1 — Manual MVP | Weeks 2–8 (overlaps 0) | First customers |
| 2 — Marketing site | Weeks 4–8 | Real pricing + proof |
| 3 — Portal v1 | Months 2–5 | Built + security-reviewed |
| 4 — AI engine + attorney app | Months 4–8 | Portal live |
| 5 — Scale + differentiators | Months 8+ | Volume |

Solo + vibe-coding means the technical phases (3–5) run a bit longer than they would with a full-time engineer — that's the honest trade for near-zero payroll. You can still sell and deliver manually (Phase 1) the entire time you're building.

---

## 7. Rough monthly cost expectation (early stage)

This is the big payoff of the lean model — your fixed costs are tiny:

- **Tools / infra while small:** Webflow, Clerk, Stripe (% of revenue), Google Cloud (Cloud Run + Cloud SQL + Storage — cheap, scales to zero when idle), Cloudflare, Sentry, Anthropic API, Google Workspace, plus your **Claude Code subscription** (your build tool) → order of **low hundreds of dollars/month** combined until you have volume.
- **Attorney:** **paid per completed matter** — a cost-of-goods that only exists when revenue exists. Price each tier so the attorney's per-matter fee plus tooling leaves you healthy margin.
- **One-off:** a single **security review** before going live with real client documents (a few hours of a freelance engineer's time).
- **No developer salary.** This is the line item the lean model removes entirely — you trade it for time and your own effort.

So: **near-zero fixed overhead, variable attorney cost per job, you as the builder.** That's the whole financial advantage of this approach.

---

## 8. Account setup checklist (Phase 0, under the business identity)

- [ ] Business Google Workspace + dedicated Chrome profile *(in progress)*
- [ ] Claude Code on the business email *(in progress)* — this is your build tool
- [ ] `charterlaw.services` domain + Cloudflare
- [ ] GitHub organisation
- [ ] Google Cloud project (billing enabled)
- [ ] Clerk account (auth)
- [ ] Stripe account (payments)
- [ ] Sentry account (error monitoring)
- [ ] Anthropic API account (the AI engine)
- [ ] Password manager holding every credential above

---

## 9. Compliance guardrails (binding — confirm all with your attorney)

> I am not a lawyer and this is not legal advice. These are principles to build into both the software and the business, to be signed off by your reviewing attorney. The detailed compliance plan from the earlier `Standard Legal/build-roadmap.md` should be carried over and treated as authoritative once it's in this folder.

1. **Attorney owns every output.** The licensed attorney is the legal-services provider; Charter Law is the operations + AI layer. No deliverable goes out without attorney approval.
2. **No AI legal advice to customers.** AI output is internal preparation only, until approved.
3. **No improper fee-sharing / non-lawyer ownership** (Rule 5.4) — paying the attorney **per completed matter** must be structured in a way a lawyer confirms is compliant in your jurisdiction (per-matter contractor pay is common, but get it blessed).
4. **Truthful marketing.** Every claim on the site (speed, "attorney-reviewed", pricing) must be accurate and reviewed.
5. **Confidentiality & privilege.** Customer documents are confidential; build security and access controls accordingly from day one (customers see only their own matters; encryption; least-privilege access). This is the reason for the Phase 3 security review.
6. **Don't copy General Legal's protected material.** Study them as a reference; write our own copy, brand, and templates.

---

## 10. Open questions to work through together

1. **Jurisdiction** — California first (matching General Legal), or somewhere else? Changes the compliance specifics.
2. **First practice area** — start narrow like General Legal (commercial contracts: NDAs, MSAs, vendor agreements), or different?
3. **Finding the attorney** — do you already have a barred lawyer in mind for the per-matter role, or is sourcing one part of Phase 0?
4. **Pull the old Standard Legal docs into this folder** (build guide, GL fingerprint, compliance roadmap) so everything lives in one place?

---

*Companion doc: `charter-law-tech-stack.md` — the concrete stack with plain-English explanations and reasoning for each layer (already drafted; being aligned to the solo-builder model).*
