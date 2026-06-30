# How It Actually Works — Backend, Economics, Attorney Life & First Clients

> The grounding layer under the personal twins. This is the *machine* the founders built and the people in the twins operate. Everything here is sourced; self-reported figures are flagged as **[claim]** and unverifiable specifics as **[unverified]**.
>
> Built for Charter Law: read this to understand the logistics — how a contract moves through the firm, what the lawyers do all day, whether they're happy, what the per-matter math is, and exactly how General Legal got its first ~20–30 clients.

---

## 1. The backend — how one contract flows, end to end

It's **Slack-native, AI-first, bot-orchestrated**. The whole point is to kill the email-driven dead time of a traditional firm.

1. **Intake (Slack channel per client).** Most clients work over a **private Slack channel** spun up the same day after a 15-minute scoping call. "Each client's private Slack channel is monitored by bots that detect new client requests, trigger our contract AI workflows, and schedule attorney time for review" (Walker). Client drops a contract in, tags the channel. The clock "starts the moment the client hits send."
2. **AI triage + routing.** "As soon as a document comes in, the first set of eyes on that document is not a lawyer. It's an AI." Routing is done "with AI understanding our lawyer specializations… what they're good at," and client comms are analysed so the firm "understand[s] the psychology and the background of that client." Triage matches the *request* (practice area, complexity, urgency) against *attorney fit* (expertise, bandwidth, availability) and routes "in the right Slack DMs the first time" (their post "Right matter, right lawyer, right now").
3. **Sentinel first pass (~10 sec).** Their contract AI "always takes the first pass… guided optionally by an attorney-defined strategy," producing redlines, annotations, and an issues list in ~10 seconds. Deliberately **over-inclusive (high recall)** — it "sometimes misinterpret[s] market, and [doesn't] fully align to the client strategy."
4. **Attorney review — in Word only.** "Contract review happens in only one place. Microsoft Word." They built a proprietary **Word add-in** for in-document AI help. The attorney edits/removes/adds to the AI markup and owns the final call.
5. **Delivery + billing.** Final tracked-changes `_redline.docx` + attorney comments returned in the same Slack channel. **Stripe** auto-invoices the flat fee per matter — "paying for your legal services takes seconds."
6. **Status pipeline.** Described flow `intake → ai_review → attorney_queue → attorney_review → delivered → completed`. (The literal enum is in the MCP/portal teardown; the public posts describe this flow but don't print the labels verbatim — treat the labels as **[unverified]**, the flow as solid.)

**Automation around every handoff.** "Bots and agents manage our scheduling, and notification, eliminating hours of lost productivity." The non-AI "boring operational technology" (routing, scheduling, status, notifications) is, per Walker, as important as the model.

---

## 2. What the lawyers actually do all day

The human is the **judgment + accountability layer on top of AI's routine output**. Qadrud-Din: "Our AI takes the first cut at anything that comes in… then our lawyers review that output and remove some of the output, add to it, modify it and then give it back." Mohler: "you actually want the lawyer exercising judgment on top of all of the routine work that the AI can do."

- **The ~15–30 min review (this is the number you asked about).** Walker, verbatim: *"Experienced attorneys can typically do a post-Sentinel review in about 15-30 minutes, a compression of several hours of formerly billable work."* It's fast because issues arrive pre-marked with explanations, redlines/comments are pre-built and editable, and full client context (prior contracts, posture) is in AI memory.
- **Bigger docs.** A full MSA that traditionally takes a lawyer **8–10 hours** they mark up — including all turns and the occasional counterparty call — in about **2.2 hours**, "cut out about 80% of the human process."
- **What the human adds (their own A/B test).** On a rigged purchase agreement, Sentinel actually *out-spotted* a senior attorney on three buried economic asymmetries (asymmetric termination, a 5-day deemed-acceptance window, a $5K liability cap on a $1M deal). The human still won on **judgment**: rewriting an overbroad non-compete into an enforceable "Exclusivity" article. The intern's line: *"The AI told me what was wrong. The attorney decided what to do about it."*
- **Turn-routing across attorneys.** "The same contract can actually be marked up on different turns by different attorneys while ensuring that the context… isn't lost from attorney to attorney. And that's something that AI can do very well, which means that you're off the clock at 5 PM." Attorney time is the scarce input, so they pool capacity and route prepared matters to the next qualified attorney.
- Attorneys also do the **15-min non-AI intake calls** and product counseling.

---

## 3. Are the lawyers happy? — the model's human side

This is a real strategic question, and General Legal has a deliberate answer.

**Who they hire:** "fifth to eighth year [Big Law] associates… who have already really been tripped up — that's our sweet spot," plus "folks who have 10, 15 plus years experience in-house." Critically: "we hire only partners" — i.e. only people senior enough to "give the final sign-off." **No juniors.** This is what makes the ~15-min review safe *and* what underpins the UPL/attorney-owns-output model.

**The trade they're selling lawyers:**
- **Lower pay than Big Law, on purpose.** "Coming in from a fifth, sixth year associate, you are taking a lower salary than you have at Big Law… you're making a quality-of-life trade-off." (Sourced comp signals: Senior Counsel ~$180–240k; Managing Partner – Emerging Cos ~$300k + equity.)
- **Offset by C-corp equity** and the pitch that real ownership "yields exceptional outcomes." (The vivid "enough to retire you when we win" phrasing is in the working dossier but **[unverified]** in public sources.)
- **Quality of life — "off the clock at 5pm."** "You can go off and enjoy your life and feel like you're a real person." Explicit contrast with Big Law's 11pm-and-back-at-7am expectations. **No billable hour.**
- **Anti-AI-anxiety positioning.** Their pitch to a nervous 5th-year: the path to partner is 11 years — "how long is it going to take AI to obfuscate this role?" Better to join the side doing the disrupting. "Our lawyers are really into AI… obsessed with AI."

**Satisfaction vs strain signals.** Ops lead Moon Kim: *"I won't pretend the work isn't grueling at times. It absolutely is. But it's the kind of grueling that fuels you rather than drains you… In past roles, long hours felt like survival. Here, they feel like momentum."* Reads as motivated-but-intense, not a 9-to-5. Client-side **95% CSAT [claim]**.

**Charter Law read:** the morale model is real but rests on (a) hiring only senior, sign-off-capable lawyers, (b) genuine QoL + equity, and (c) self-selecting AI enthusiasts. A solo Charter Law can't offer equity-at-scale, but *can* offer one senior reviewing attorney genuine autonomy, no billable hour, and AI-leverage as a perk.

---

## 4. Unit economics — the per-matter math

**Flat-fee schedule:** $250 (≤3pp; NDAs, simple SOWs, LOIs) · $500 (standard, 3–25pp; +1 revision + negotiation guide) · $1,000 (full negotiation; unlimited turns + counterparty calls) · $2,000 (drafting ToS/Privacy/MSA/DPA/BAA; smaller drafts $1,000–1,500) · long/non-standard "from $1,000" · GC-as-a-service "custom."

- **Margin today: ~40–50% per contract [claim].** On a $500 review, "you're keeping about 300." COGS = **AI cost + attorney time**.
- **The trajectory bet:** as Sentinel's first cut converges on the attorney's final product (Mohler estimates **6–9 months**), human touch on an MSA drops from 2.2 hrs → ~30 min, COGS falls, and "our margins go… closer to software margins." This is Warren's "AI operating leverage" (see [`charlie-warren.md`](charlie-warren.md)) made concrete.
- **Throughput per attorney:** **300–600 contracts/year** today [claim], projected to "multiple thousands… without any decline in quality and while working fewer hours than Big Law." StartupHub frames the ~80%-by-AI as a **5–10× leverage ratio per attorney**; Walker's north star is **100×**.
- **Scale [claim]:** ~$1M ARR run rate and ~110–115 clients by late March 2026; target $10M ARR / 30–40 attorneys within a year; "30–50% market share" ambition in target segments.
- **Pricing is designed to fall.** Some MSAs will get *cheaper* over 18 months as the human touch shrinks — they're pricing for share, not margin extraction. Complex work (e.g. asset purchase agreements) is priced above $500.

---

## 5. How they got the first ~20–30 clients (the GTM you asked about)

The single most copyable part for Charter Law.

1. **Start in a warm, dense network.** "Our first 30 clients were all YC startups that were either seed or Series A." They sold to their *own cohort* — founders who already trusted the YC brand and lived in Slack. Charter Law equivalent: pick one tight community where you have credibility and contract pain is acute.
2. **Risk-reversal offer that removes the first "no."** The lever, verbatim from the YC launch post: *"Don't let your founder friends pay traditional law firms for routine contract review! Send them to us. We'll do any company's first contract review for free until demo day."* First contract free + a "book a demo" Calendly. A $250–500 free trial is cheap CAC for a sticky, recurring client.
3. **Wedge on a sharp, recurring pain.** The hook is the moment a startup gets its first 30-page Cloud Services Agreement "with company-ending terms buried in the first turn," and the incumbent wants "$500–$2,000/hour" over "days or weeks." Narrow ICP: Series A–B doing recurring commercial paper — "big enough to have real contract volume but small enough that a full-time GC is not cost-justified."
4. **Land-and-expand inside the Slack channel.** Once you're in, switching costs compound: "they have all your playbooks, your redline history, your negotiating positions." Turn 2 is faster and stickier than turn 1. Then expand practice areas *on client pull* — "the clients telling us to launch [Employment & ECVC] were our existing clients. Once a founder has gotten a sales contract turned in three hours over Slack, they don't want to email a different firm."
5. **Move upmarket once proven.** "Our last 30 clients were only about half YC startups… half were Series B/C/D or later," incl. 10+ companies that raised >$100M, as overflow/supplemental counsel to in-house teams.
6. **Always-on demand gen.** Disciplined **LinkedIn direct-response ads** (offer-led, ~8–12 truthful claim families × hooks; iterate hook→image→CTA), a free viral tool (FindTheFuckUp), a free template library (CC0 on GitHub), heavy founder thought-leadership, and PR stunts ("first law firm hired by an AI agent"). *(Ad infrastructure confirmed via LinkedIn pixel; exact creative/spend [unverified].)*

> ⚠️ Compliance gate (carried from the main dossier): "law firm," "US-barred attorney," "attorney-reviewed," and fixed *legal* pricing are only usable once Charter Law's attorney/entity structure is actually live. Until then, stay at the workflow-support layer in public copy.

---

## Sources
- [Artificial Lawyer — "How Do AI-Native Law Firms Work?" (full J.P. Mohler interview/transcript)](https://www.artificiallawyer.com/2026/03/31/how-do-ai-native-law-firms-work/)
- [Ryan Walker — "Contract Review & the AI-Native Model"](https://www.general.legal/blog/contract-review-the-ai-native-model)
- [General Legal — "Right matter, right lawyer, right now" (triage/routing)](https://general.legal/blog/right-matter-right-lawyer-right-now)
- [General Legal — "Optimizing Legal Operations…" (Stripe, 95% CSAT)](https://general.legal/blog/optimizing-legal-operations-to-ensure-a-frictionless-client-experience)
- [General Legal — "Reinventing Modern Legal: Operations & Culture" (Moon Kim)](https://general.legal/blog/reinventing-modern-legal-operations-culture)
- [General Legal — "The Death of the Billable Hour"](https://general.legal/blog/the-death-of-the-billable-hour)
- [Zach Zager — "Balancing Attorney and Machine at an AI-Native Law Firm"](https://general.legal/blog/finding-the-balance-between-lawyer-and-machine-at-an-ai-native-law-firm)
- [J.P. Mohler — "Introducing Employment and ECVC"](https://general.legal/blog/introducing-employment-and-ecvc-at-general-legal)
- [General Legal — Pricing](https://general.legal/pricing)
- [Best Practice — Javed Qadrud-Din interview](https://bestpracticeai.substack.com/p/how-this-yc-backed-startup-are-reinventing)
- [YC Launch — General Legal (first-clients, free-until-demo-day offer)](https://www.ycombinator.com/launches/PLT-general-legal-the-ai-native-law-firm-for-the-growth-stage)
- [StartupHub — Claude's Corner: General Legal](https://www.startuphub.ai/ai-news/claudes-corner/2026/claudes-corner-general-legal-yc-w2026)
