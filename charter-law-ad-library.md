# Charter Law — Ad Library & A/B Playbook

> A growth-critical reference. Built from a teardown of **all 71 of General Legal's live LinkedIn ads** (captured 2026-06-28 from the LinkedIn Ad Library, company ID `110454124`). For each claim family you get: General Legal's **actual** ads (format, real text, offer, ad numbers), **what they were A/B testing and why**, a **video treatment** where relevant, and **Charter Law's own rewritten ads** ready to ship.
> Source teardown: `general-legal-dossier.md` §F and the Standard Legal file `outputs/research/general-legal-linkedin-ad-library-teardown.md`.

---

## ⚠️ Truthfulness gate (read first — protects you legally)

You're a brand-new firm; some claims aren't true *yet*. Don't ship a claim before it's true. Flags used below:

- **[P0]** — asserts attorney involvement. Only run once your reviewing-attorney structure is live (roadmap Phase 0), wording attorney-approved. Before then use the interim phrasing.
- **[PROOF]** — has a placeholder (client count, satisfaction, testimonial). Fill with real numbers only.
- **[SLA]** — promises a turnaround time. Only claim a time you can actually hit every time.

**Interim phrasing (pre-attorney-structure):** don't say "law firm," "our lawyers," "US-barred," or "attorney-reviewed," and never make AI sound like it gives advice with a lawyer rubber-stamping. Safe swaps: "attorney-reviewed redline" → "fixed-fee contract review with final review by **licensed counsel** / **completed by a barred attorney**"; "our attorneys" → "your **reviewing attorney**." Framing rule: **"AI prepares the work; a licensed attorney reviews the full document and approves the final redline."**
**Don't borrow GL's pedigree** (Casetext/Harvard/YC). Your "built-different" angle is *AI-native from day one* — truthfully yours.

---

## 1. How General Legal's ad system works (so you copy the method, not the posts)

**It's a direct-response system, not brand posting.** 71 live ads = **51 single-image + 20 video**, all pushing to a free-evaluation / booking action. They did **not** invent 71 ideas — they wrote ~**12 claim families** and retested each with different hooks, proof, offers, and formats.

**Ad count per family = how much they're betting on it.** More variants = more spend/confidence. Their ranking:

| Rank | Claim family | # ads | Read |
|---|---|---:|---|
| 1 | Flat fee / no surprise bill | 16 | Their #1 conversion lever — price certainty removes buying fear |
| 2 | Speed / stuck revenue | 11 | "Slow legal = stuck money" is their best pain frame |
| 3 | General commercial ("reimagined") | 10 | A broad always-on lane beside the sharp pain ads |
| 4 | $11K hourly-bill shock | 7 | Hard price-anxiety opener (all video) |
| 5 | AI output vs lawyer review | 6 | Catches AI-curious founders who still want safety (all video) |
| 6 | BigLaw price contrast / Flat-fee… | 4–5 | "BigLaw quality at ~10% price" |
| 7 | AI-native engineering / Slack-native | 4 | Credibility + convenience |
| 8 | Social proof / Fundraising | 3 | Trust + high-intent fundraising moments |
| 9 | Practical judgment | 2 | Quality angle ("good lawyer tells you what matters") |
| 10 | Sales-contract question | 1 | A single live-document hook |

**What they A/B test (the variables they isolate):**
1. **Claim family** — which *pain/value* converts (flat-fee vs speed vs price-shock vs trust…).
2. **Hook angle within a family** — question vs blunt statement vs founder scenario.
3. **Format** — single-image vs video (see the pattern below).
4. **Offer** — and this one visibly *evolved*: early ads = **"Free evaluation of any matter or contract,"** later ads add **"$500 off first contract for qualifying startups"** and **"First contract review is free."** Running an offer test to lift conversion.
5. **Proof point** — "200+ companies / 95% CSAT" vs "YC-backed" vs "Harvard-educated" vs "Casetext."
6. **Creative style** — detailed value-prop vs the minimalist **"Commercial legal, reimagined."** one-liner (curiosity/brand test).
7. **CTA wording** — "Start a review," "Free evaluation," "Try flat-fee counsel."

**The format pattern (important):** **video carries pain narratives** (the "$11K for 4 contracts" and "almost lost a $400K deal" stories, and the "I ran it through Claude vs a lawyer reviewed it" piece are *all* video); **single-image carries crisp value props, trust stats, and the minimalist brand lines.** Match format to message type.

**What they're checking (metrics).** LinkedIn won't show their spend, but a direct-response system like this optimizes a funnel: impressions → **CTR** (is the hook stopping the scroll?) → **cost-per-click / cost-per-landing-page-view** → **leads** (free-eval signups + calls booked via their `meet.` scheduler) → **cost-per-lead (CPL)** → downstream **paid first-contract conversion**. They keep low-CPL/high-converting families, kill the rest, and **iterate the hook first, the image second, the CTA last.**

**Your takeaway:** build a small library of *truthful* claim families, give each 2–3 treatments, run small batches, judge by **family-level CPL and booked calls**, not by individual ad vanity metrics.

> Data limit: the LinkedIn Ad Library doesn't expose per-ad impressions, spend, run-dates, or duration for non-political ads, so we can't see literal win/loss or "odds." **Ad count per family is the best available proxy** for what they bet on, and the **offer/format/proof splits** above are the visible test structure.

---

## 2. The families — GL ground truth + Charter Law ads

Each block: what GL ran (with real text + the test), then Charter Law's rewritten ads (flagged + with a format recommendation).

---

### Family 1 — Flat fee / no surprise bill  ·  GL: 16 ads (all single-image) — their biggest bet
**GL's actual hooks (representative):**
- *"Contract review shouldn't come with a surprise hourly bill. General Legal does it on a flat fee — $500 for most contracts."* (ads 5, 15, 43)
- *"You shouldn't have to brace for the invoice every time you send a contract to your lawyer. General Legal is flat fee —"* (ads 14, 20)
- Offers tested: **"Free evaluation"** (early: 5,14,15,20,43,46) → **"$500 off first contract for qualifying startups"** (later: 51,53,54,58,60,61,62,64,66,71).

**What they A/B tested here:** the **offer** (free eval vs $500-off), and the **framing of price pain** ("surprise hourly bill" vs "brace for the invoice"). All single-image because it's a crisp value prop, not a story. **Checking:** which offer drives more booked evals at lower CPL.

**Charter Law ads (single-image):**
1. Contract review with the price set before we start: one flat fee. → *See pricing.*
2. No hourly meter. No surprise invoice. One flat fee per contract. → *Start a review.* **[P0]**
3. Your legal bill shouldn't be a mystery. Charter Law is flat fee, every time. → *Get a quote.*
4. $500 for most contracts. That's the whole price. → *Send us a contract.*
5. Stop bracing for the invoice every time a contract needs looking at. → *Flat-fee review.*
6. Flat fee, fixed scope, no add-ons. Legal you can budget for. → *Start now.*
7. Most contracts $500. Simple ones $250. You'll always know first. → *See the schedule.*
8. Predictable legal pricing for unpredictable startups. → *Start a review.*
9. Pay per contract, not per hour. → *First review free.* **[P0]** *(offer test: run vs "$X off first contract")*
10. The quote is the price — no timesheets, no rounding up. → *Get started.*
11. Legal bills without the wince. → *Review a contract.*
12. One contract, one price, no surprises. → *Start with Charter Law.*

*Run your own offer A/B here too: "First review free" vs "$250 off your first contract."*

---

### Family 2 — Speed / stuck revenue  ·  GL: 11 ads (~4 image + 7 video)
**GL's actual hooks:**
- *"Deals stall when contracts stall. Outside counsel takes days or weeks — and a stuck contract is stuck revenue."* (image: 9,16,27; offer "Legal work in hours, not weeks")
- **Video story:** *"Imagine almost losing a $400K deal because outside counsel took three weeks to redline one MSA. General Legal turns con[tracts in hours]…"* (video: 25,28,30,31,33,34,65; offer "Deals stuck in legal? Get 3-hour turnarounds and a legal team that lives in your Slack.")
- *"Can your deal wait a week in legal review?"* (image 70, minimalist).

**What they A/B tested:** **format** (the abstract speed claim as image vs the concrete "$400K deal" loss as a video narrative — the story is video-heavy, telling you narrative pain performs in video), and **specificity** (generic "days or weeks" vs a named "$400K / 3 weeks / one MSA"). **Checking:** does the visceral story lower CPL vs the plain claim.

**Charter Law ads:**
13. Deals stall when contracts stall. Get yours back in hours. → *Send it over.* **[SLA]** *(image)*
14. A contract stuck in legal is revenue stuck in limbo. → *Unstick it.* *(image)*
15. **[VIDEO]** A founder almost loses a quarter-defining deal because one contract sat in legal for two weeks — then sends the next one to Charter Law and signs the same day. → *Don't let legal stall your deal.* **[SLA]**
16. Close faster: contracts reviewed in hours, not business days. → *Start a review.* **[SLA]** *(image)*
17. The faster the redline, the faster the signature. → *Send us the contract.* *(image)*
18. **[VIDEO]** Split screen: "Outside counsel — 3 weeks" vs "Charter Law — 3 hours." → *Pick your timeline.* **[SLA]**
19. Don't let one MSA hold up the whole quarter. → *Turn it around today.* *(image)*
20. Send a contract this morning, move your deal forward this afternoon. → *Start now.* **[SLA]** *(image)*
21. Legal at the speed your business actually moves. → *Get a fast review.* *(image)*
22. Can your deal wait a week in legal review? → *It doesn't have to.* *(image, minimalist)*

---

### Family 3 — $11K hourly-bill shock  ·  GL: 7 ads (ALL video)
**GL's actual hooks:**
- *"Paying $11K for 4 contracts? The math on hourly legal is broken. General Legal does flat-fee contract reviews in hours…"* (video 3,4,40,44; offer "$11K for 4 contracts? Try flat-fee startup counsel.")
- *"Last quarter's legal bill: $11K for 4 contracts. We switched to flat-fee, 3-hour reviews with General Legal…"* (video 47,48,59 — the **testimonial framing** of the same number).

**What they A/B tested:** the **frame of the same shock-number** — accusatory question ("Paying $11K…?") vs founder-testimonial ("Last quarter's bill was $11K, we switched…"). All video because a price-shock number lands harder spoken/animated. **Checking:** question vs testimonial CPL.

**Charter Law ads — ALL VIDEO. ⚠️ use a *generic market* figure, not a fake testimonial:**
23. **[VIDEO]** "$1,200 an hour to read a contract?" — text animates the hourly meter ticking up, then cuts to a single flat number. → *The math on hourly legal is broken.*
24. **[VIDEO]** Four contracts shouldn't cost five figures. Animate four invoices stacking into a shock total, then collapse to one flat fee. → *Try flat-fee review.*
25. **[VIDEO]** A clock vs a price tag: "Hourly billing charges you for the clock. We charge for the contract." → *Pay flat instead.*
*(Hold any "we switched and saved $X" testimonial until you have a real client who'll say it — **[PROOF]**.)*

---

### Family 4 — BigLaw price contrast  ·  GL: 4–5 ads (single-image)
**GL's actual hooks:**
- *"BigLaw bills $1,200 an hour to review a contract. We do it for a flat fee — roughly 10% of what they'd charge, on average."* (52,55; offer "BigLaw-caliber attorneys at ~10% of the price")
- *"Are you overpaying for contract review?"* / *"How much does your lawyer charge to review your sales contract?"* (56,57 — minimalist questions).

**What they A/B tested:** **detailed math** ("$1,200/hr, ~10% of price") vs **bare question** ("Are you overpaying?"). **Checking:** does the specific number or the open question pull more clicks.

**Charter Law ads (single-image):**
26. BigLaw bills ~$1,200/hour to read a contract. We do it for a flat fee. → *Switch.*
27. Same quality of review. A fraction of the BigLaw price. → *Compare.*
28. You don't need a Fortune 500 budget to get a contract done right. → *Get started.*
29. Top-tier contract work without the top-tier invoice. → *See pricing.*
30. Why pay BigLaw rates for run-the-company paperwork? → *Send us the contract.*

---

### Family 5 — AI output vs a real review  ·  GL: 6 ads (ALL video) — all [P0]
**GL's actual hook (one line, two proof variants):**
- *"There's a difference between 'I ran it through Claude' and 'our lawyer reviewed it.' That difference gets very real whe[n it's your deal]…"*
  - Proof variant A → *"US-barred attorneys, fixed-fee pricing. Free evaluation."* (7,17,26,39)
  - Proof variant B → *"Harvard-educated lawyers at a fraction of the cost. First contract free."* (32,41)

**What they A/B tested:** the **proof/close** on an identical hook — credentials-as-trust ("US-barred") vs prestige-as-value ("Harvard… at a fraction of the cost"). All video because it's a persuasion argument. **Checking:** which proof converts the AI-curious-but-cautious buyer.

**Charter Law ads — VIDEO, all [P0]; swap "ChatGPT" for the tool your ICP actually uses:**
31. **[VIDEO]** "There's a difference between 'I ran it through ChatGPT' and 'a lawyer reviewed it' — and you find out which on the day it matters." → *Get the real thing.* **[P0]**
32. **[VIDEO]** Screen 1: an AI flags ten issues. Screen 2: a licensed attorney circles the two that actually matter and rewrites them. → *AI flags. A lawyer decides.* **[P0]**
33. AI can spot the problem. A licensed attorney decides what to do about it. → *That's Charter Law.* **[P0]** *(image variant of the same idea)*
34. We use AI to move fast — and a licensed attorney to be right. → *See how.* **[P0]**
35. Don't sign on a chatbot's say-so. → *Get a redline from licensed counsel.* **[P0]**
36. The redline is AI-fast. The judgment is human. → *Get yours.* **[P0]**
*(A/B your own proof line: "Licensed, barred attorneys" vs "Real lawyers, a fraction of BigLaw price.")*

---

### Family 6 — AI-native engineering / built different  ·  GL: 4 ads (single-image)
**GL's actual hooks:**
- *"Legal engineers just started a law firm. General Legal's founders come from Casetext, Harvard Law, and Cooley — backed [by YC]."* (1,12,37; offer "A law firm built by lawyers and engineers")
- *"The world's preeminent legal engineers just started a law firm…"* (54,58 — bolder claim)
- *"If you're send[ing] commercial contracts to traditional outside counsel, stop. We're an AI-native law firm…"* (63).

**What they A/B tested:** **pedigree intensity** ("legal engineers" vs "the world's preeminent legal engineers") and how hard to lead with the Casetext/Harvard résumé. **You can't use their résumé** — so test your *structural* difference instead.

**Charter Law ads (single-image):**
37. A law firm that runs like software: fast, flat-fee, AI-native from day one. → *Start.* **[P0]**
38. We didn't bolt AI onto an old firm. We built around it. → *See the difference.*
39. Legal, rebuilt for the AI era. → *Send your first contract.*
40. The firm BigLaw would build if it could start over. → *Meet Charter Law.*

---

### Family 7 — Social proof / trust  ·  GL: 3 ads (single-image) — all [PROOF]
**GL's actual hook:** *"200+ growth-stage companies trust their startup legal to General Legal — with 95% client satisfaction. We're a YC-backed [firm]."* (2,24,29; offer "Trusted by 200+ growth-stage companies, 95% client satisfaction. Free evaluation.")

**What they A/B tested:** mainly a **placement/format** retest of one strong proof stack (they only needed 3 — the stat does the work). **Checking:** whether hard numbers lower CPL vs pain-led ads.

**Charter Law ads (single-image) — [PROOF], fill only when true:**
41. [X]+ startups trust Charter Law with their contracts. → *Join them.* **[PROOF]**
42. [X]% client satisfaction. Flat fees. Hours, not days. → *Start a review.* **[PROOF][SLA]**
43. "[Real one-line testimonial]." → *See why founders switch.* **[PROOF]**
44. Trusted by growth-stage teams who move fast. → *Get started.* **[PROOF]**
*(Until you have numbers, leave this whole family dark — fake proof is the one thing that can actually sink you.)*

---

### Family 8 — Fundraising docs  ·  GL: 3 ads (single-image)
**GL's actual hook:** *"Closing a round? Your SAFEs, side letters, and financing docs shouldn't be what slows it down."* (10,18,38; offer "SAFEs, notes & priced rounds on a flat fee. Free evaluation.")

**What they A/B tested:** attaching the firm to a **high-intent, high-urgency moment** (a live raise) vs general contract pain. **Checking:** whether fundraising-intent audiences convert at lower CPL (they likely do — urgent + high willingness to pay).

**Charter Law ads (single-image; time these to fundraising seasons/audiences):**
45. Closing a round? Don't let a SAFE or side letter slow it down. → *Turn it fast.*
46. SAFEs, side letters, financing docs — reviewed fast, priced flat. → *Send them over.*
47. Your raise shouldn't wait on legal. → *Get fundraising docs turned in hours.* **[SLA]**
48. Investor sent a side letter at 6pm? Have it back before your morning call. → *Start.* **[SLA]**

---

### Family 9 — Slack-native / where you work  ·  GL: 4 ads (single-image)
**GL's actual hooks:**
- *"You already run contracts through AI. You just don't fully trust the output — and you shouldn't."* (22,23,42; offer "Slack-native, full-stack law firm for founders. Free evaluation.")
- *"Does your lawyer use Slack?"* (69, minimalist).

**What they A/B tested:** **convenience as the wedge** ("we live in your Slack") vs the trust angle, and a long hook (22) vs a one-line question (69). **Checking:** does "works where you already work" pull clicks on its own.

**Charter Law ads (single-image):**
49. Does your lawyer work in Slack? Ours does. → *Add Charter Law to your channel.* **[P0]**
50. Send a contract where you already work — Slack, email, anywhere. → *Get started.*
51. No portals to learn. Drop the contract, get the redline. → *Try it.*
52. Your contracts, handled in the same chat you already use. → *Start.*

---

### Family 10 — Practical judgment / quality  ·  GL: 2 ads (single-image, minimalist)
**GL's actual hooks:**
- *"A bad lawyer gives you lots of redlines. A good lawyer tells you what matters. Commercial legal, reimagined."* (49)
- *"What terms actually matter in your sales contract? Our experienced lawyers can tell you in less than 3 hours…"* (68)

**What they A/B tested:** moving the pitch **up-market from cheap/fast to quality-of-judgment** — a different buyer motivation. Only 2 ads = a smaller bet, but a distinct angle worth having. **Checking:** does a quality message attract higher-intent (less price-shopper) leads.

**Charter Law ads (single-image):**
53. A bad review buries the 3 clauses that matter under 20 that don't. We don't. → *See.*
54. We tell you what actually matters — not just what to redline. → *Start.*
55. Good legal advice is a decision, not a pile of comments. → *Get a clear answer.*
56. Which terms should you actually push back on? We'll tell you. → *Ask us.*

---

### Family 11 — Sales-contract question  ·  GL: 1 ad (single-image)
**GL's actual hook:** *"How long will your lawyer take to review your next sales contract? Commercial legal, reimagined."* (50)

**What they A/B tested:** a single **"live document in your inbox right now"** trigger — catches a founder actively sitting on a deal. Smallest bet, sharp intent. **Checking:** intent-trigger CTR.

**Charter Law ads (single-image):**
57. How long will your lawyer take on your next sales contract? We say hours. → *Test us.* **[SLA]**
58. Got a sales contract in your inbox right now? → *Send it over.*
59. What's hiding in your customer's paper? Let's find out — fast. → *Start a review.*

---

### Family 12 — General commercial / "reimagined"  ·  GL: 10 ads (single-image) — the always-on lane
**GL's actual hooks:**
- *"Your law firm shouldn't cost hours of back-and-forth and a surprise bill every time you sign a vendor."* (6,13,35,45; offer "AI-native, flat-fee law firm for startups")
- *"BigLaw was built for the Fortune 500. Every other company just got the same bill. General Legal is the founder's law firm."* (8,19,36,51,60)
- *"General Legal saves founders $100s–1000s per contract, turns contracts in hours not days…"* (67)
- The minimalist tagline *"Commercial legal, reimagined."* recurs as the close.

**What they A/B tested:** a **broad, always-on acquisition lane** running beside the sharp pain ads — multiple framings of "the founder's law firm" so LinkedIn can find audiences the narrow ads miss. 10 ads = a big steady bet. **Checking:** broad-reach CPL as a floor under the campaign.

**Charter Law ads (single-image):**
60. The contract firm for founders who move fast. → *Start a review.*
61. Run-the-company legal — MSAs, NDAs, DPAs, vendor paper — done right, done quick. → *Send one.*
62. Commercial contracts, reimagined for startups. → *Meet Charter Law.*
63. Your outside counsel for everyday contracts, minus the everyday hassle. → *Get started.*
64. Charter Law saves founders hundreds per contract and turns them in hours, not days. → *Start.* **[SLA]**
65. Send us a contract. Get back work you can act on. That's the whole pitch. → *Start.*
66. Vendor agreement, NDA, MSA — whatever's blocking you this week, send it. → *Get started.*
67. The founder's contract firm. → *Send your first one.*
68. Stop sending run-the-company paperwork to a Fortune 500 firm. → *Switch to Charter Law.*
69. Everyday contracts shouldn't be a project. → *Make them a Charter Law ticket.*

*(Three more reserve concepts to round out a 71-strong rotation, single-image:)*
70. Your lawyer should feel like part of the team, not part of the overhead. → *Meet Charter Law.* **[P0]**
71. Legal that keeps up with your roadmap. → *Start a review.*

---

## 3. Your A/B test plan (how to actually run this)

**Phase A — find the winning family (truthful day-one only).** Run one ad each from **Flat-fee (1), $11K shock (3, video, generic figure), BigLaw contrast (4), Practical judgment (10), General commercial (12)**. Same offer across all. Judge by **cost-per-booked-call / CPL by family** over ~1–2 weeks. Hold **AI-vs-lawyer (5)** and **Social proof (7)** until the attorney structure is live / you have real numbers.

**Phase B — within the winning family, test ONE variable at a time:**
1. **Hook** first (question vs statement vs scenario) — biggest lever.
2. **Format** next (image vs a 10–15s video of the winning hook).
3. **Offer** (e.g. "First review free" vs "$250 off first contract") — GL clearly found this mattered.
4. **CTA** last (smallest lever).

**What to watch:** CTR (hook working?), cost-per-click, **cost-per-lead / cost-per-booked-call** (the real number), and **paid-conversion rate** of those leads (guards against cheap low-intent clicks). Keep winners, rewrite losers by changing the hook first.

**Cadence:** small batches (6–8 ads), weekly review, scale spend on the lowest-CPL family, retire the rest. Track everything **by family**, not by single ad.

---

## 4. Production checklist
- [ ] Attorney structure live before any **[P0]** ad runs; wording attorney-approved.
- [ ] Every **[PROOF]** placeholder is a real, defensible number (or the family stays dark).
- [ ] Every **[SLA]** time is one you can hit every time.
- [ ] No "law firm / our lawyers / US-barred" unless true (use interim phrasing).
- [ ] Video reserved for pain narratives ($-shock, deal-loss, AI-vs-lawyer); image for value props, trust, taglines.
- [ ] One headline + one CTA + clean visual per ad.
- [ ] UTM-tag every ad so CPL is tracked **by family**.
