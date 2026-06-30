# Charter Law — Operating Playbook

> How to actually run Charter Law as a business, distilled from (a) **Y Combinator's "AI-native service companies" playbook** and (b) **General Legal's** observed operating model. Tailored to your reality: **solo non-technical founder who vibe-codes, plus one per-matter attorney.**
> Companion to `charter-law-roadmap.md` (what to build, in order), `charter-law-tech-stack.md` (with what), and `general-legal-dossier.md` (the competitor). Status: **DRAFT v1.**

---

## 0. The one idea

Charter Law is an **AI-native service company**, not a software company. The customer buys a **finished legal outcome** (an attorney-reviewed redline), not a tool. That single fact changes everything below: the human (attorney) is the *interface* to the customer; the software exists to let that human deliver many more outcomes per hour without quality dropping. **The process IS the product.**

---

## 1. Is this the right market? (YC's four traits — Charter Law scores well)

YC's framework for whether an AI-native service business can work. Commercial contract review hits all four:

1. **Low trust / already outsourced.** Founders already pay outside lawyers for contracts; they care about the *result*, not how it's produced. You're displacing a vendor, not changing behaviour. ✅
2. **Low judgment at the task level.** Most of a contract review (parsing, issue-spotting, drafting boilerplate redlines, explaining changes) is automatable; real legal *judgment* concentrates in a few spots. That's the shape AI services need. ✅
3. **High intelligence threshold.** The work is hard enough that **AI + a licensed attorney** is required to produce something the client will accept — which keeps pure-software competitors out. ✅
4. **Helpful regulation.** Legal practice is regulated: you need a licensed attorney, malpractice cover, and UPL compliance. That raises the bar — and becomes your **moat**. ✅

**The Sam Altman test (apply it constantly):** as the models get better, does Charter Law get *stronger* or get *commoditised*? Answer: stronger — better models lower your cost to produce each review, while the regulatory requirement for an attorney-of-record holds. You ride the model curve; you are not replaced by it. (This is also General Legal's bull case.)

---

## 2. The existential risk: variance

> "Customers will fire you for variance faster than they will fire you for being a bit slower or a bit more expensive." — YC

**Variance = inconsistent output.** One great review and one sloppy one teaches the client they can't trust you, and trust is the whole product. For Charter Law this means: from matter #1, drive consistency with **playbooks, checklists, standard clause language, and standard comment phrasing**, so every review of a given contract type looks and reads the same regardless of when it's done or how rushed it was. This matters *more* for a solo operation, because you can't lean on a big team's averaging — your process has to encode the consistency.

---

## 3. The trap to avoid: the early-demand trap

> "It's easy to sign up a lot of pilot customers… it can quickly overwhelm your ability to serve them… It is a literal trap." — YC

Counterintuitive but vital for a solo founder + one attorney: **cap your first pilots to a small handful (the roadmap says 3–10).** Resist signing too many too fast. Use the first few to *learn* — where AI gives real leverage vs where you're just automating the obvious — and to build the process. Overloading early means you're stuck doing everything by hand and never build the leverage that makes the business work. **Do things that don't scale at first; then make scaling the product.**

---

## 4. Pricing

**Principles (YC):** you're not competing with other software — you're competing with **the cost of a lawyer**. So:
- **Sell outcomes, not seats or tokens.** Flat fee per matter.
- **Price on value, not cost-plus.** Cost-plus caps your upside permanently; straight-line undercutting makes you look cheap/low-quality. Anchor to "a fraction of what a traditional firm charges," not to your own costs.
- **Per-unit (per-contract) is the cleanest** model to explain and forecast.

**Concrete anchors (General Legal's public schedule — a proven reference):**

| Work | Price |
|------|-------|
| Simple review (≤3pp: NDAs, simple SOWs, LOIs) | **$250** |
| Standard review (redline + 1 revision + negotiation-guide cover letter) | **$500** |
| Full negotiation (unlimited turns + counterparty calls) | **$1,000** |
| Drafting from scratch (TOS, Privacy, MSA, DPA, BAA) | **$2,000** |
| Employment / ECVC line items | **$250 → $3,500** by matter type |
| GC-as-a-service subscription | priced by company size/stage (later) |

**The pricing lesson worth stealing:** General Legal learned **most clients don't want negotiation — they want a clean redline and a plain explanation of what changed and why**, then they close themselves. So make the **standard $500 tier = redline + a "what changed, why it's risky, what your fallback is" cover letter**, and reserve full negotiation for a higher tier. This is a better-margin, faster-to-deliver default and it's what clients actually want.

**Margin rule for the per-job-attorney model:** every tier's price must comfortably cover **the attorney's per-matter fee + your tooling cost + healthy margin.** Set the attorney's per-matter rate against each tier before you publish prices.

---

## 5. The economics (P&L) — your unfair advantage is here

YC's structure: **Revenue − COGS = gross profit; − OpEx = operating income.**

**Your COGS (cost to deliver one matter) has three parts — obsess over these from day one:**
1. **Model cost** — the Claude API calls to prepare one review (small, a few dollars).
2. **Hosting** — Cloud Run/Cloud SQL/storage amortised per matter (small).
3. **Human-in-the-loop** — the **attorney's per-matter fee** (your dominant COGS).

**AI operating leverage (the core bet):** the more of the routine prep your software does well, the **less attorney time each matter needs**, the lower your COGS, the higher your margin. Every improvement to Sentinel-equivalent prep, playbooks, and the Word workflow is a margin improvement. Track **attorney-minutes per matter** like a hawk — it's your single most important operating number.

**The opportunity:** traditional service firms top out ~30% margin; the AI-native bet is that operating leverage pushes you toward **50%+** on a market many times larger than software. You don't need to be there day one — the *trajectory* must be believable.

**Your OpEx is tiny** (no developer salary — you build; no office). This is the whole financial point of the solo model: near-zero fixed cost, variable attorney cost per job, margin that improves as your software improves.

---

## 6. How the work flows (the operating model to copy)

General Legal's loop, sized for Charter Law. The principle: **AI prepares, operations move the work, the attorney owns judgment, the client gets an outcome.**

1. **Intake where the client already works** — start with email or a Slack channel + a simple intake form. Capture the same minimum facts every time (deal, counterparty, buyer/seller, deadline, concerns). Don't overbuild a portal first.
2. **Every request becomes a tracked *matter*** — id, type, tier, status, timestamps. If you can't see the queue, you can't manage it. Status model: `intake → ai_review → attorney_queue → attorney_review → delivered → completed`.
3. **Standard lane vs exception lane** — a checklist decides: supported contract type, sane page count, in-scope, in-jurisdiction → proceed; unusual/high-stakes/out-of-scope → pause or decline. **This protects flat-fee margins** — edge cases priced like routine work are how fixed-fee firms die.
4. **AI first pass** — Claude produces a plain-English summary, an issue list, and a draft tracked-changes redline. **Deliberately high-recall** (over-inclusive). Internal only.
5. **Attorney review in Word** — the attorney works in one place (Word + the Claude Word add-in), accepts/edits/rejects, applies judgment and what's-market, and **approves**. Approval is the only gate to delivery.
6. **Deliver + a cover note** — the redline plus a short "what changed / why / fallback" note, back through the same channel.
7. **Follow-up turns reuse context** — prior contracts, redlines, and posture stay on the matter so turn 2 is faster than turn 1.
8. **Every matter improves the system** — tune the prompts, playbook, clause library, and pricing from what the attorney changed.

**The "attorney attention engine" idea:** the software's job is to point the attorney's scarce attention exactly at the provisions that matter, with drafts pre-built — not to replace the attorney.

---

## 7. Metrics — run the operation by numbers

Track these from matter #1 (a spreadsheet is fine before any dashboard):
- **Cycle time:** client submission → delivered (not just working time). This is what the customer feels.
- **Attorney-minutes per matter:** your COGS driver and leverage gauge.
- **Throughput:** matters completed per week.
- **Variance / rework:** how often a deliverable needs redo; how consistent quality is.
- **Escalation rate:** % of matters hitting the exception lane (too high → scope/pricing too broad).
- **Margin per matter** and **CSAT.**

Find the bottleneck and build for it. If AI takes 10 seconds but matters wait hours for the attorney, the bottleneck is **attorney coverage**, not AI — solve the actual constraint.

---

## 8. Growth: land narrow, expand by client pull

- **Land** on one narrow, repeatable, painful job: **commercial contract review** for growth-stage startups (the ICP: enough contract volume to hurt, too small for a full-time GC — *not* pre-seed, *not* Fortune 500).
- **Expand only when clients pull you** into adjacent work in the same channel (employment docs, SAFEs/side letters) — exactly how General Legal added Employment + ECVC. The trusted channel + accumulated context is the compounding advantage; don't email-shop a different firm when you're already in their Slack.
- **The compound moat:** every matter adds to your playbooks and market knowledge, and every client relationship raises switching costs (you hold their history). It gets stronger the more you do.

---

## 9. Corporate & compliance structure (take this to a lawyer)

**Stage the structure — don't start with the complex version.**

**Start here (first ~10 clients, lowest risk):** Charter Law is the **branded intake + AI-prep + operations layer**. The **reviewing attorney's own practice/firm is the legal provider**; the **customer engages the attorney directly** before any advice is delivered; **Charter Law is paid a separate, fixed workflow/vendor fee — not a percentage of the legal fee.** This respects California **B&P Code §6125** (only barred lawyers practise law), **Rule 5.4** (no fee-sharing or non-lawyer control of a practice), **Rule 5.3** (the lawyer supervises non-lawyer assistance), and **Rule 7.1** (truthful marketing). Customer-facing language: "your **reviewing attorney**," "attorney-approved redline," and "AI prepares the work; a licensed attorney reviews the full document and approves the final redline." Do **not** call Charter Law a law firm or say "our lawyers" until that's actually true.

**Move to this later (at scale, once demand is proven):** the **two-entity "Atrium model"** — a **lawyer-owned law firm** (client relationship, bar license, malpractice, legal judgment) **+ a separate technology/operations company** (Charter Law — software, IP, can raise capital). This is how funded AI-native firms (General Legal, Atrium) structure around Rule 5.4 / ABS limits long-term.

Questions to put to a California attorney in Phase 0:
- Will you review startup contracts **per matter** under your **own firm's engagement**, with the customer engaging you directly?
- Can Charter Law be paid a **separate fixed workflow/vendor fee** (not a cut of the legal fee)?
- What exact website wording can we use ("reviewing attorney," "attorney-approved redline")? What disclaimers/FAQ do you require?
- Conflicts, scope, jurisdiction, confidentiality, and which AI tools may process client documents (e.g. Claude for Word) — what are your requirements?
- **UPL:** the attorney-approval gate is the compliance mechanism — we'll bake it into the software so it can't be bypassed.

> Not legal advice. This is the structure to take to a licensed California attorney — settling it is the gating task of Phase 0.

---

## 10. Don't

- **Don't buy a law firm to shortcut in** (YC: almost never works — legacy metrics/expectations; you can't bolt PMF on). One exception: acquiring a regulatory license fast. Build, don't buy.
- **Don't present AI output as legal advice** to a client, ever, pre-approval.
- **Don't sign too many pilots too fast** (the early-demand trap).
- **Don't compete on being cheap** — compete on outcome + speed + predictability at a fraction of BigLaw price.
- **Don't copy General Legal's words, brand, templates, or code** — only the structure and the lessons.

---

## 11. The five things that actually matter (if you remember nothing else)

1. **Get the per-matter attorney + the compliance structure right first** (Phase 0). Nothing else counts without it.
2. **Sell finished outcomes at flat fees; price on value.**
3. **Kill variance** with playbooks and checklists from matter #1.
4. **Watch attorney-minutes-per-matter** — that's your leverage and your margin.
5. **Land narrow, let clients pull you wider.**
