# AI-Native Law Firm Competitors — Research Dossier

_Last updated: 30 June 2026_

## Purpose & scope

This file consolidates research on **AI-native law firms** — firms that *deliver legal services* with AI at their core, as distinct from legaltech *software vendors* (Harvey, Legora, Robin AI, Ironclad) that sell tools to traditional firms. The focus is on the cluster most relevant to an AI-native, attorney-reviewed **commercial contract review** business: lean, lawyer+engineer teams selling fixed-fee transactional work to startups/founders/investors.

**Confidence tags used throughout:** _Confirmed_ (stated in a primary source — company site, ToS, job ad, founder interview), _Inferred_ (reasoned from indirect evidence; basis noted), _Undisclosed_ (not found after thorough searching).

**A standing caveat on foundation models:** most of these firms deliberately do *not* name their production LLM vendor. Where a vendor is "confirmed," it is named by the firm; otherwise treat model attribution as undisclosed. The recurring strategic pattern is that the foundation model is treated as a near-commodity, with the moat located in playbooks, context/retrieval, orchestration, and human review.

---

## Tier 1 — Closest comparators (startup commercial-contract / transactional cluster)

These six share the target profile most closely: a licensed AI-native firm delivering transactional legal services, lean senior team, often lawyer+engineer founders, fixed/productized pricing, frontier-model + playbook + human-in-the-loop.

### 1. General Legal — _the anchor / closest reference point_

- **Location / stage:** Union City, CA. YC W2026. ~15 people. $11.5M combined pre-seed/seed (Audacious Ventures lead; SUSA, SV Angel, Box Group, AME Cloud, YC).
- **What they do:** Commercial contracting (MSAs, NDAs, DPAs, vendor agreements) for growth-stage startups. $500 flat fee/contract, <3hr turnaround (typically ~1hr).
- **Founders:** Ryan Walker (CEO, ex-Casetext CTO, ran CoCounsel at Thomson Reuters), Javed Qadrud-Din (CTO, ex-Casetext Head of AI, ex-Meta), J.P. Mohler (CPO, ex-Cooley/WilmerHale, ex-TR ML researcher).
- **Entity:** General Legal, LLP (single CA entity); attorney signs every deliverable (UPL compliance). No public firm/IP split.

**Tech stack**
- **Cloud:** Render/Heroku for the open-source app; production cloud undisclosed (signed-URL uploads imply S3/GCS). _Inferred / Undisclosed._
- **Languages:** Python + TypeScript (job ad). Open-source app = Flask + React + PostgreSQL + gunicorn. _Confirmed._
- **Foundation model:** **Anthropic Claude (Sonnet 4)** — confirmed in their open-sourced app and all their tooling writing centers on Anthropic. The Casetext–OpenAI early-GPT-4 relationship did NOT carry over. _Confirmed (OSS) / Strong (core)._
- **Architecture:** Core product named **"Sentinel"** — single-pass first review guided by an attorney-defined strategy; generates redlines + issues list in ~10s; attorney reviews 15–30 min. Frontier-model **prompting + per-client playbook + human review — NOT fine-tuning**. Long-context over RAG/vector retrieval; custom/direct-API orchestration (no LangChain). _Strong/Inferred._
- **Delivery:** Slack (private channel + bots) + **custom Word add-in** + **production MCP server** (mcp.general.legal; Streamable HTTP, OAuth 2.1 + PKCE — first law firm with an MCP server) + client portal. _Confirmed._
- **Eng leadership:** The 3 founders (ex-Casetext/CoCounsel); no other engineers public. GitHub org has 4 public repos.
- **Security:** No SOC 2 claimed; trust story is attorney-client privilege.
- **Disclosure level:** High (open-source repos + public MCP server).
- **Their published thesis:** LLMs fail at *judgment* ("what's market"), not vocabulary — so they layer attorney judgment + per-client context on a frontier model rather than training a domain model.

**Confirmed product details (from founder screenshots, ~Apr–May 2026) — worth taking design inspiration from:**

- **"Domino's-style" contract tracker (CONFIRMED, built).** Co-founder J.P. Mohler announced a client-facing tracker "inspired by the Domino's pizza app" that shows **live status + estimated minutes to the next step / delivery**. The client sees a horizontal progress bar with five named stages: **Received → AI Review → Queued for Attorney → Attorney Review → Delivered**, each lit up as it completes, with an ETA under the current stage (e.g. "Queued for Attorney ~2m", "Attorney Review ~42m"). The matter list shows columns: **File name · Versions · Status · Submitted**. Pitch: "10x'ing top law firms on price and speed is table-stakes; you also deserve *predictability* — never wonder exactly what time your mark-up will be finished." → _This is the visible, client-facing front end of the same `received → ai_review → attorney_queue → attorney_review → delivered` pipeline the MCP server exposes. Cheap to build, strong trust/UX differentiator._
- **The redline "workbench" UI (CONFIRMED).** They review inside **Microsoft Word using Anthropic's Claude Word plugin**, with Track Changes on so edits land as native redlines. The plugin shows a stack of **suggestion cards** with an **"Apply all (N)"** button and, per card: a title (e.g. "Convert to mutual NDA — redefine Confidential Information to cover both parties"), an inline tracked-changes preview, an expandable **"> Reasoning"**, and **Dismiss / Apply** buttons (i.e. per-suggestion accept/reject). Nuance: they initially found Anthropic's plugin "unusable," then "the best Word plugin on the market" after an Anthropic update — and their stance is "we build for *clients*, not lawyers… we just use the best tools" (so they'll ride 3rd-party tooling rather than build their own redline editor).
- **Client portal AI assistant is named "Clerk" (CONFIRMED).** At portal.general.legal/dashboard: "Ask **Clerk** for the AI answer, or toggle to **'Attorney'** and a lawyer will respond." Upload-a-contract box + canned prompts ("Summarize this contract for me", "What are the key risks here?", "Is there anything unusual I should ask about?", "Should I get a lawyer involved?") + "View all matters". Includes an honest SLA banner ("our lawyers may not be able to respond until tomorrow 8am ET"). → _A single chat surface with an AI/human toggle is a neat, low-cost pattern._
- **"Find The Fuckup" free lead-gen tool (CONFIRMED).** Their open-sourced app is a live marketing funnel: "Your expensive lawyer is making mistakes." Drag-drop a .docx → free AI error check. Footer reassurance: "We never save or store your contract." Tied to a sharp insight they publicised: after two months, "the vast majority of contracts our lawyers review (often drafted by the top law firms in the world) are riddled with minor typos, missed section references" — i.e. the free tool both generates leads and proves the value prop.

**Design-inspiration takeaways for Charter Law:** (1) build the Domino's-style status tracker early — it's cheap and it's a real differentiator on *predictability*; (2) the attorney review surface can be Word + a plugin with Apply/Dismiss-per-suggestion + a reasoning expander, rather than a bespoke console; (3) a single client chat surface with an AI-answer / talk-to-attorney toggle ("Clerk") is a clean front door; (4) a free "find the mistakes" .docx checker is a strong, low-cost lead magnet with a built-in privacy reassurance.

- **Sources:** general.legal/blog/contract-review-the-ai-native-model · general.legal/blog/we-build-for-clients · github.com/General-Legal/findthefuckup-open · legalmcp.org · ycombinator.com/companies/general-legal · J.P. Mohler & General Legal LinkedIn posts (Apr–May 2026)

### 2. Crosby — _closest overall twin_

- **Location / stage:** New York. Founded Sept 2024. ~$85M+ raised (Sequoia seed → Index/BCV/Elad Gil → Index + Lux Series B).
- **What they do:** Agentic contract review for startups (clients: Cursor, Clay, UnifyGTM). Fixed fee / "deal velocity" pricing; <1hr review.
- **Founders:** Ryan Daniels (CEO, Stanford Law, ex-Cooley), John Sarihan (CTO, ex-Ramp engineer/tech lead, ex-Google SWE intern).
- **Entity:** Real licensed law firm + in-house AI engineers.

**Tech stack**
- **Cloud:** GCP (inferred — founding infra engineer Anthony Corletti is a FastAPI-on-Cloud-Run/Kubernetes specialist); officially undisclosed. _Inferred._
- **Languages:** Python backend; React + Vite + TanStack frontend. _Confirmed (job ads + public repo)._
- **Foundation model:** **OpenAI + Anthropic + Google Gemini** via a multi-vendor model router. _Confirmed._
- **Architecture:** 8-agent "swarm"; intake/orchestrator internally named **"Bailiff"** (contracts in via Slack/email → triage → route to agents). **Selective fine-tuning** + RAG + prompting + human-in-the-loop; trained on ~50k hand-labeled clauses. Confidence score routes low-confidence work to a human. Manipulates Word OOXML directly. _Confirmed._
- **Eval stack:** Public **RedlineBench** benchmark on the **Harbor** framework + **Modal**, scored by a 3-model LLM judge panel. Research arm = "Crosby Intelligence."
- **Delivery:** Slack/email + native Word (.docx tracked changes) + "Client Console" (React/Vite app with dynamic playbooks + kanban).
- **Eng leadership:** CTO John Sarihan (ex-Ramp); founding infra eng Anthony Corletti (ex-Galileo/Algorithmia, GCP/K8s).
- **Security:** SOC 2 status undisclosed; leans on being a licensed firm (privilege, malpractice cover).
- **Disclosure level:** High.
- **Sources:** crosby.ai · intelligence.crosby.ai · github.com/crosbylegal/redline-bench · Forbes (Mar 2026, "Bailiff")

### 3. Moritz (formerly "Arcline") — _between General Legal and Crosby_

- **Location / stage:** SF + NY + **Oslo engineering hub**. YC W2026. ~10 people. $9M seed (YC + 20VC).
- **What they do:** Commercial/corporate/employment contracts; flat fee; ~4hr turnaround; "AI does 80%, lawyer does final 20%." Startups + larger companies. "$2bn in deals" in first 3 months.
- **Founders:** Pamir Ehsas (CEO, lawyer, ex-outside counsel to OpenAI & Google), Stefan Mandaric (CTO, ex-Fulbright MIT, ML/data engineer).
- **Entity:** **MSO structure** — Moritz Law PC (the firm) + **Parlai, Inc.** (management/tech entity, holds the platform IP, received the $9M) + **Moritz AS** (Norwegian subsidiary housing the Oslo eng team). Routes around ABA Rule 5.4.

**Tech stack**
- **Cloud:** **AWS** (job ad: "own infrastructure and observability... on AWS"; trust-center assets on S3 us-east-1). Marketing site = Framer; app = Next.js. _Confirmed._
- **Languages:** Next.js + React + TypeScript front end; **Python** backend; SQL. _Confirmed (Arcline-era job ads)._
- **Foundation model:** **Undisclosed.** The ex-OpenAI tie was Pamir's *legal counsel* role, NOT a tech partnership — do not infer GPT. (Codex/Claude appear only as dev coding tools.) _Undisclosed._
- **Architecture:** Agentic platform — named **intake agent**, **document-generation pipelines** drafting from playbooks, **playbook-generation systems** learning from historical docs. RAG/semantic search over precedent. Dedicated evals function. **Fine-tuning IS a real workstream** (ToS reserves right to train/fine-tune on client content, opt-out via engagement letter). Orchestration framework + vector DB undisclosed (likely custom). _Confirmed architecture; libraries Undisclosed._
- **Delivery:** Email + Slack + Next.js portal. No Word add-in, no public API. _Confirmed._
- **Eng leadership:** CTO Stefan Mandaric; core eng/research roles Oslo-based; no other engineers named publicly.
- **Security:** ISO 27001 + GDPR "compliant" (Comp AI trust portal); **SOC 2 appears in-progress, not achieved** (no published attestation). SAML SSO.
- **Disclosure level:** Medium-high (stack confirmed; model undisclosed).
- **Sources:** trust.moritzlegal.com · moritzlegal.com/terms · ycombinator.com/companies/arcline/jobs · Law.com (Parlai MSO)

### 4. LegalOS — _closest confirmed-components match (but immigration, not contracts)_

- **Location / stage:** San Francisco. YC W2026. ~3 people (founders). ~$1.5M annualized revenue ~4 months post-launch. Investors: YC, Pioneer Fund, Rice Capital.
- **What they do:** AI-native US **immigration** law firm (O-1, H-1B, L-1, TN, EB-1/EB-2 NIW). 48hr turnaround; "studied 12,000 successful petitions"; licensed attorney signs. Positions vs BigLaw's $10–35k/petition.
- **Founders:** Matthew Asir (CEO, ex-"Legal Bullet" founder, Forbes 30u30), Rachel Asir (COO), Claire Jutabha (CTO, ex-TikTok LLM safety / Notarize / NASA JPL; CS USC). Father Joseph Asir, Esq. provides attorney oversight.

**Tech stack**
- **Cloud:** Marketing site = **Webflow**; app (app.legalos.ai) = **Vercel** (confirmed via Sentry `vercel-production` header + deployment URL). Database = Supabase/Postgres (on AWS). _Confirmed._
- **Languages:** **TypeScript end-to-end** — Next.js/React + Supabase/Postgres + **pgvector**. _Confirmed._
- **Foundation model:** **Undisclosed.** Homepage "your data never trains *public models*" implies a hosted commercial frontier API under a no-train tier (OpenAI or Anthropic most likely), not open-source. _Inferred / Undisclosed._
- **Architecture:** **24 specialized agents** on a TypeScript-native stack — job ad names **Vercel AI SDK + Mastra + MCP + agent sandboxes** (NOT LangChain/Python). RAG over the 12k-petition corpus via **pgvector — not fine-tuning** ("source attribution," retrieval UI, no training language). Agent roles: eligibility mapping, narrative drafting, evidence compilation, RFE anticipation. _Confirmed architecture; Mastra "familiarity" per JD._
- **Delivery:** Web portals only (client + internal ops + attorney review). Onboarding via Cal.com booking; no Slack/API/Word add-in. Public lead-gen tools: O-1A Eligibility Checker (separate Vercel app, LLM-backed), USCIS Fee Calculator (client-side). _Confirmed._
- **Eng leadership:** CTO Claire Jutabha (built the 24 agents); GitHub empty; hiring first non-founder engineer.
- **Security:** **SOC 2 Type II self-asserted** (no trust center, no auditor named, no `/security` page; copy says "certified" where SOC 2 is "attested"). Data residency undisclosed (inferably US).
- **Disclosure level:** Medium-high (stack confirmed; model undisclosed).
- **Note:** On raw components + no-fine-tuning philosophy, arguably the closest match to General Legal in the whole set; differs by leaning harder into multi-agent orchestration and being all-TypeScript / immigration.
- **Sources:** legalos.ai · ycombinator.com/companies/legalos/jobs/XY5Ek7M-founding-engineer · app.legalos.ai/login

### 5. Vector Legal

- **Location / stage:** San Francisco. YC W2026. ~5 people. Founded 2026.
- **What they do:** "Hybrid AI law firm & legal OS for startups" (platform **VectorOS™**). Priced rounds, customer contracts, formations, M&A, cap table, data rooms. Software + white-glove lawyer support.
- **Founders:** Mitch Duncombe (ex-Fenwick + YC Legal), Keenan Venuti (CTO, ex-Staff AI SWE at **Ironclad**, ex-Accenture ML / knowledge graphs).

**Tech stack**
- **Cloud:** Undisclosed.
- **Languages:** **TypeScript + Python**; **LangChain + "Deep Agents"** for agent orchestration; OCR/document-ingestion pipelines. _Confirmed (Founding AI Engineer JD)._
- **Foundation model:** Undisclosed (model-agnostic via LangChain — _Inferred_).
- **Architecture:** **Agentic + RAG + evals + human-in-the-loop**; "agentic data rooms"; memory/context/retrieval layers; evaluation frameworks. Clearly Ironclad-influenced (evals-first reliability culture). No fine-tuning mentioned. _Confirmed._
- **Delivery:** VectorOS web portal/app (smart data room, e-sign, cap table, AI assistant). Slack/Word/API undisclosed.
- **Eng leadership:** CTO Keenan Venuti (ex-Ironclad).
- **Security:** Undisclosed (no SOC 2/ISO found; do not confuse with unrelated ad-tech "Vector").
- **Disclosure level:** Medium (good JD detail; cloud/model undisclosed).
- **Sources:** vectorlegal.com · ycombinator.com/companies/vector-legal/jobs/SoiB0TW-founding-ai-engineer

### 6. Covenant — _investor-side analog (own less-contested lane)_

- **Location / stage:** New York. $4M seed (Flybridge Capital; Neil Barsky). Launched Jan 2024. ~6 lawyers.
- **What they do:** AI-native firm for **private-market investors** (buy-side only). Fund Investment Review (LPAs), Venture Investment Review (SAFEs/notes), first AI MFN-election tool, NDA mark-up, "Investment Data" queryable term database. 2-business-day SLA.
- **Founders:** Jen Berrent (ex-WeWork COO/CLO, ex-WilmerHale partner), Richard Perris (ex-GC CVC Capital, ex-Clifford Chance).
- **Entity:** Covenant Law, PLLC (firm) + separate IP/tech company that holds tech and licenses it to the firm.

**Tech stack**
- **Cloud:** **Google Cloud Platform** (confirmed — GCS is a monitored dependency on their status page). _Confirmed._
- **Auth/infra:** **WorkOS** (SSO, SCIM, FGA, audit logs), **Vanta** trust center, **Atlassian Statuspage**; marketing site Next.js + Sanity CMS. _Confirmed._
- **Languages:** Product app undisclosed (Next.js marketing site). _Undisclosed._
- **Foundation model:** **Vendor-agnostic multi-model ensemble** — every doc reviewed by multiple models in parallel ("5 AI associates"); **model disagreement triggers human review**. Specific vendors undisclosed. _Confirmed approach._
- **Architecture:** Deliberately **rejects RAG/chunking** for core review — feeds entire 120-page documents into large-context windows (couldn't launch until Nov 2023 when context windows grew). Lawyer-verified data feeds the queryable "Investment Data" store (DB undisclosed; BigQuery/AlloyDB likely on GCP). _Confirmed._
- **Delivery:** Dashboard + API.
- **Eng leadership:** None public; one unnamed ex-BlackRock hire. No public job ads.
- **Security:** **SOC 2 Type II**; zero data retention; no training on client data; full anonymization.
- **Disclosure level:** Medium.
- **Note:** No new dedicated investor-side AI-native *law firm* competitor surfaced in research — that niche is dominated by software vendors (SwiftLaw, ProVision, Justee), so Covenant largely stands alone.
- **Sources:** covenant.statuspage.io · trust.covenant.co · artificiallawyer.com/2025/09/11/covenant-the-hybrid-ai-law-firm/

---

## Tier 2 — Adjacent AI-native firms (different practice/customer, but well-researched)

### 7. Avantia (now Carta Law)

- **Location / stage:** London / New York. Acquired by **Carta** (May 2026) → "Carta Law." Serves 200+ asset managers; $15T+ AUM. Backed pre-acquisition by Hoxton, Smedvig, Ace Cap.
- **What they do:** AI-native firm for funds & PE; contract/NDA review, AML/KYC, LP transfers. Platform **"Ava."**
- **Tech stack:**
  - **Cloud:** AWS (corporate site; production inferred). **ISO 27001** certified (+ likely Cyber Essentials).
  - **Architecture (confirmed by CEO):** Ava's orchestrator is an **open-source LLM** (unnamed — likely Llama/Mistral family) that **routes tasks to multiple smaller specialist models fine-tuned on Avantia's own data**. Flagship = NDA-markup model trained on **~55,000 NDAs**. **Fully self-hosted on Avantia servers — never calls public LLMs.** RAG over ~1M docs.
  - **Delivery:** Microsoft Word + Outlook (Graph API).
  - **Eng leadership:** CTO **Paul Gaskell** (ex-BlackRock VP of ML, Aladdin/eFront), VP AI Thomas Barillot (ex-BlackRock/Bloomberg), VP Eng Varun Balupuri (ex-BlackRock/Bloomberg), Sr Data Scientist Firuza Mamedova. A BlackRock-Aladdin/Bloomberg alumni cluster.
  - **Note:** The "Claude" integrations in Carta news belong to *Carta's* broader ERP, NOT Ava's core models.
- **Disclosure level:** Medium-high.
- **Sources:** avantialaw.com/news/lpm-avantia-laws-ai-advantage · businesswire (Carta Law announcement)

### 8. Manifest (Manifest OS / Manifest Law)

- **Location / stage:** New York (+ SF, Phoenix). $60M Series A at ~$750M valuation (Menlo Ventures led; Kleiner Perkins, First Round, Quiet Capital). ~55 people. Largest Series A in legal-tech history.
- **What they do:** AI-native firm, **business immigration** first (Arizona ABS). 3,000+ engagements, 100+ attorneys. Platform "Manifest OS"; integrates with clients' HR/recruiting software.
- **Tech stack:**
  - **Cloud:** **GCP** (job ad "GCP preferred"; ex-Google CPTO). _High confidence._
  - **Languages:** **TypeScript end-to-end** — React/Next.js + Node.js + PostgreSQL (Ashby job ad). Internal AI dev tools: Cursor, Copilot, v0. _Confirmed._
  - **Foundation model:** **Undisclosed** (GCP + ex-Google CPTO makes Vertex/Gemini a plausible guess, no more). Vector DB + orchestration undisclosed.
  - **Architecture:** RAG + embeddings + semantic search + agents in production; field-level **confidence scoring** (strong/medium/weak); mandatory two-attorney sign-off; trained on USCIS evidence standards / RFE patterns.
  - **Delivery:** Client portal + bidirectional **HRIS/ATS sync** (Rippling, Workday, Gusto, Deel, Greenhouse, Ashby, Lever; Merge/Finch aggregator inferred).
  - **Eng leadership:** CPTO **James Cariello** (ex-Google decade, Bloomberg, DigitalOcean, Gro Intelligence); Suhas Shetty leads AI Chat eng (ex-SoFi).
  - **Security:** SOC 2 Type II; no training on user data without consent.
- **Disclosure level:** Medium.
- **Sources:** jobs.ashbyhq.com/manifest-os · manifestos.com/the-company

### 9. Tacit Legal / Tilder

- **Location / stage:** UK (Haywards Heath). SRA-regulated. Small LLP, 4 lawyer-partners, no CTO. Privately held.
- **What they do:** Contract-review platform **"Tilder"**; per-contract flat fee from ~£95; human 2+PQE review. For in-house/sales/procurement teams.
- **Tech stack:**
  - **Cloud:** **DigitalOcean** (app) + **AWS** (disaster recovery only); Sentry monitoring; Microsoft 365 integration hub; NetDocuments; Cloudflare; Plausible. **UK data residency.** _Confirmed (privacy notice)._
  - **Foundation model:** Undisclosed — sub-processor list names NO LLM vendor. Vendor-agnostic; whitepaper says +2pp max from model upgrades.
  - **Architecture:** Contract-risk **taxonomy** (every clause → queryable data point + risk score) + rapidly-configurable policy/playbook layer + LLM-generated amendment requests + senior-lawyer sign-off. Whitepaper thesis: **~80% of cost reduction from operating model, +40pp from 15–20 min playbook engineering, not the model.** Cost £2,500 (2023) → £340 today.
  - **Delivery:** Web portal + BI export; no Word add-in.
  - **Eng leadership:** Chris Bridges (Partner/COO, developer ~25 years, effectively sole builder).
  - **Security:** UK-GDPR-first; no SOC 2/ISO published.
- **Disclosure level:** Low on stack, but very candid on economics.
- **Sources:** tacit.legal/legal/privacy-notice · tilder-tldr.com/whitepapers/why-ai-hasnt-solved-contract-review

### 10. Norm Law (Norm Ai)

- **Location / stage:** New York. Founded 2023 by John Nay (ex-Stanford CodeX legal-NLP). $140M+ raised (Vanguard, Blackstone, BCV, Citi, TIAA, Coatue). Norm Law launched with a $50M Blackstone investment (Nov 2025).
- **What they do:** Financial-services regulatory compliance — convert regulations/policies into executable "Regulatory AI Agents." Clients with $25–30T combined AUM.
- **Tech stack:** Proprietary **LEAP** (Legal Engineering Automation Platform) — no-code; 30+ "Legal Engineers" compile regulations into **decision trees** that LLM agents traverse, with a rationale per determination (**neuro-symbolic / regulation-as-code**). Model-agnostic; has benchmarked Claude. Compliance Agent for Microsoft 365 Copilot. Eng team ex-Google/Meta/Stanford; in-house ex-regulators (ex-SEC Commissioner, ex-NY DFS). SOC 2 Type I & II.
- **Note:** Primarily a *compliance-tech company*; the law firm is secondary. Enterprise/institutional customer, not the startup cluster.
- **Sources:** norm.ai/post/legal-engineering · norm.ai/platform

### 11. Eudia

- **Location / stage:** Palo Alto. Up to $105M Series A (General Catalyst). $2M→$20M ARR in 12 months. Customers: Cargill, DHL, Duracell, Coherent.
- **What they do:** "Augmented Intelligence" platform for **enterprise/Fortune 500 in-house legal teams**. NOT a law firm — an enterprise software platform.
- **Tech stack:** Proprietary "Enterprise Brain" (knowledge/ontology layer), "Expert Digital Twins," "MINDs" decision engines. Model-agnostic — confirmed **OpenAI + Anthropic** + custom reasoning models on **Azure AI Foundry**. **Azure** backbone; Microsoft 365, ServiceNow, Consilio integrations. Thesis: "the end of LLM wrappers."
- **Note:** Adjacent — enterprise software, not a service-delivering firm.
- **Sources:** eudia.com/blog/the-end-of-llm-wrappers · eudia.com/news/eudia-announces-collaboration-with-microsoft

### 12. Lawhive

- **Location / stage:** London. $60M Series B (Feb 2026; Mitch Rales lead; TQ, GV, Balderton, Jigsaw). Revenue >$35M, 7x YoY. ~500 regulated lawyers across 3 firms; expanding to 35 US states. Acquired UK firm Woodstock Legal.
- **What they do:** AI-native firm for **consumer/SME** law (not commercial B2B contracts). AI assistant **"Lawrence."**
- **Tech stack:** Built on Lawhive's **own fine-tuned in-house LLM** (reportedly passed the UK SQE ~81%) + mixed foundation models. Lawhive Labs R&D doing autonomous task prediction. Specific foundation vendors unnamed. CTO Jaime Van Oers; founding AI engineer.
- **Note:** Strong "we build our own models" posture, but consumer/SME practice at large scale.
- **Sources:** labs.lawhive.co.uk · fortune.com/2026/02/05/lawhive-ai-law-firm-startup-series-b

### 13. Garfield AI

- **Location / stage:** London. First fully AI-powered firm **authorized by the UK SRA**. ~600+ claims, ~£500k recovered.
- **What they do:** Small-business **debt recovery / small claims** (England & Wales). £2 chaser letter → court-claim prep from £50.
- **Tech stack:** **Deterministic expert system is in charge** and constrains what the LLMs may do ("a codified version of my brain"); multiple LLMs run in parallel; hard rules handle the £10k cap, limitation periods; explicitly **barred from proposing case law**. Deep API integration with the County Court, Companies House, accounting platforms. LLM self-simulation testing. Model vendor undisclosed (GPT-4 was the inspiration). Architect Daniel Long (ex-quantum physicist).
- **Note:** Litigation/debt-recovery niche; deterministic-first design.
- **Sources:** adr.org podcast "Inside the World's First AI-Native Law Firm" · sra.org.uk press release

---

## Tier 3 — Tool-users, regional, or mislabeled (lighter relevance)

### 14. Compound Law

- **Location:** Düsseldorf/Berlin, Germany. AI-native firm for startups/scale-ups in DACH; 1hr response; fixed-fee/retainer.
- **Build vs use:** Builds a **thin proprietary "skills" layer** on third-party infra. Cloud = **Hetzner + Cloudflare (Workers + D1) + Azure (AI/LLM)** — all EU-resident. Foundation model = OpenAI-via-Azure (inferred). RAG + playbook + fractional-GC sign-off. Delivery **embedded in Slack/email/Teams/Drive** ("no portals, no tickets"). CTO Mohit Tilwani; founders ex-Gleiss Lutz, ex-Trade Republic. GDPR/EU-residency-led; no SOC 2/ISO.
- **Note:** Strong cluster fit on model/customer but **German jurisdiction**. Delivery-in-Slack is notable.
- **Sources:** compound.law/en-DE · compound.law/en-DE/trust-center

### 15. Farringdon Law

- **Location:** UK. Launched April 2026. Backed by/spun out of legaltech **Orbital** (Orbital Witness).
- **Build vs use:** Builds (via parent Orbital). AI-native residential **conveyancing** firm running on Orbital's platform ("Orbital Copilot"). Cloud = **Azure** (historical; "stack has since evolved"). Multi-model: OpenAI + Anthropic + Google (published eval table). Agentic + RAG + some fine-tuning + solicitor oversight ("Conveyancing Engineers"). Regulated by the CLC.
- **Note:** Property/conveyancing niche, UK.
- **Sources:** artificiallawyer.com/2026/04/13/orbital-launches-its-own-real-estate-law-firm · tech.orbitalwitness.com

### 16. Three Points Law

- **Location:** UK (trading name of Excello Law). Boutique AI-native firm, **sports & tech law**, value-based fees.
- **Build vs use:** **USES** — tool-user, no proprietary stack. Primary tool = **Legora** (private cloud, UK regulatory compliance). Founders Simon Leaf & Tom Murray (ex-Mishcon de Reya). No CTO/engineering.
- **Sources:** threepointslaw.com/legal-tech · nonbillable.co.uk

### 17. ElevateNext

- **Location:** US. Lawyer-led AI-augmented firm affiliated with ALSP **Elevate**. Enterprise/in-house oriented.
- **Build vs use:** **USES** parent Elevate's platforms (**Elevate ELM** + **ELMA** agentic AI), with some co-built tools. ELMA is LLM-agnostic (integrates Claude + OpenAI), agentic + playbook + human-in-loop. Lawyer-led (Patrick Lamb, Nicole Auerbach); eng sits in Elevate. First US ABS (Arizona) integrating an ALSP with an affiliated firm.
- **Sources:** elevatenextlaw.com · elevate.law/news/meet-elma

### 18. AgileCounsel — _mislabeled; no real AI stack_

- **Location:** San Francisco + Singapore. Venture financings + cross-border M&A.
- **Reality:** A traditional 1–2 person boutique with **no engineers, no product, no AI stack**. "AI-native" label comes only from the AI Firm Index directory. Static Squarespace site; founder Raj Barot is a lawyer. Every stack field is genuinely empty.
- **Note:** Included for completeness; not a real AI-native competitor.
- **Sources:** agilecounsel.com · crunchbase.com/organization/agile-counsel

### 19. Others noted but not deep-researched

- **Soxton** — US (NY), AI-native "NewMod" for startups (incorporations, equity, fundraising), flat fee from ~$100, $2.5M pre-seed (Moxxie + Strobe). Founder Logan Brown (ex-Cooley). Strong cluster fit on customer/model; lighter data.
- **Lexsy** — San Francisco, startups, ex-Cooley founder. AI-native.
- **Alaro** — UK, SME contracts.
- **Paralex** — Washington DC, small business.
- **LawFairy** — London, "technology-only" practice built on a fully deterministic legal model (vs probabilistic AI).

---

## Cross-cutting patterns

**Build vs. use.** Genuine *builders* with their own stack: General Legal, Crosby, Covenant, Moritz, Vector Legal, LegalOS, Avantia, Manifest, Compound (thin layer). *Tool-users* on someone else's platform: Three Points (Legora), ElevateNext (Elevate ELM/ELMA). *Hybrid:* Farringdon (builds, but the tech is parent Orbital's).

**Fine-tuning is rare.** Only **Crosby** (selective), **Avantia** (specialist models), and **Lawhive** (own fine-tuned LLM) actually fine-tune. Most — including General Legal, Covenant, Tacit, LegalOS, Compound — treat the foundation model as a swappable commodity and locate value in playbooks, context/retrieval, orchestration, and human review.

**Model vendors are mostly undisclosed.** Confirmed: Crosby (OpenAI + Anthropic + Gemini), Eudia (OpenAI + Anthropic + Azure custom), General Legal (Anthropic Claude), Farringdon (OpenAI + Anthropic + Google via Orbital). Undisclosed: Moritz, LegalOS, Manifest, Covenant (agnostic ensemble), Tacit, Avantia (open-source, unnamed), Vector (agnostic via LangChain).

**Cloud:** GCP appears for Covenant (confirmed), Crosby + Manifest (inferred/preferred); AWS for Moritz (confirmed) + Avantia; Vercel + Supabase/AWS for LegalOS; DigitalOcean for Tacit; Azure for Farringdon/Compound (EU).

**Architecture spectrum:** from **simplest** (General Legal's single-pass "Sentinel"; Covenant's large-context ensemble — both reject heavy agentic complexity) to **most agentic** (Crosby's 8-agent "Bardiff"/Bailiff swarm; LegalOS's 24 agents; Moritz's intake-agent + pipelines). Several deliberately put a **deterministic/rules layer in control of the LLM** to suppress hallucination (Garfield, Norm, Tacit's taxonomy).

**Similarity to General Legal (tech-stack lens):** General Legal → Crosby → **Moritz** (closest on architecture/philosophy) → **LegalOS** (closest on confirmed components + no-fine-tuning) → Vector Legal (shares TS+Python but leans on LangChain/agents).

---

## Key directories / trackers

- **AI Firm Index** (aifirmindex.com, by Lupl co-founder Matt Pollins) — the best living tracker, now ~40 listings (up from ~27). JS-rendered, so filter by "Commercial Contracts" / "Funds & Private Equity" in a browser to catch new entrants. Inclusion criteria are loose/self-applied (e.g. AgileCounsel mislabeled).
- **Lupl "AI law firms to watch"** roundups; **Artificial Lawyer**, **Law.com Legaltech News**, **Legal IT Insider** for ongoing coverage.

---

_Research method note: findings drawn from company sites, terms of service, trust centers/status pages, job postings (the richest source of real stack data), engineer GitHub/LinkedIn footprints, founder interviews/podcasts, and press. Confidence tags reflect source quality at time of writing; very recent 2026 model-version references (e.g. "GPT-5.5", "Claude Opus 4.8") should be sanity-checked before quoting exact figures._
