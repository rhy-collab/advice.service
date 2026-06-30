# Charter Law — Tech Stack (Path A, committed)

> Companion to `charter-law-roadmap.md`. This is the **decided** technology stack, modelled on General Legal and updated to current (2026) best practice. Written so a non-technical founder can understand every choice and **vibe-code straight from it with Claude Code** — there is no separate developer.
> Status: **DRAFT v1** — this is your build spec. Get a one-off security review (see the roadmap) before real client documents flow through it.

---

## The shape of the system (plain English)

Think of Charter Law as **five surfaces sharing one brain**:

1. A **marketing website** that sells the service and takes the first payment.
2. A **customer portal** where clients upload contracts and track/download their work.
3. An **attorney app** where your lawyer reviews the AI's draft and approves it.
4. A **backend** (the "brain") that holds all the data, runs the AI, and enforces the rule that nothing ships without attorney approval.
5. A **database** where every customer, matter, and file lives.

General Legal runs exactly this shape (we confirmed it from their public infrastructure). We're copying the shape, not their content.

```
                    ┌───────────────────────────┐
  Customer  ─────►  │  Marketing site (Webflow) │
                    └────────────┬──────────────┘
                                 │ sign up / pay
                                 ▼
   ┌──────────────────┐    ┌───────────────────────┐
   │ Customer portal  │    │  Attorney app         │
   │ (React SPA)      │    │  (React SPA, internal)│
   └────────┬─────────┘    └──────────┬────────────┘
            │   both call the same backend          │
            ▼                                        ▼
        ┌───────────────────────────────────────────────┐
        │      Backend API  (Python + FastAPI)          │
        │   • verifies login (Clerk)                    │
        │   • runs the AI prep (Claude)                 │
        │   • enforces "attorney must approve"          │
        │   • talks to Stripe, file storage             │
        └───────────────┬───────────────────────────────┘
                        ▼
              ┌────────────────────┐     ┌──────────────────┐
              │ PostgreSQL (data)  │     │ Cloud Storage    │
              │ users, matters     │     │ contract files   │
              └────────────────────┘     └──────────────────┘
```

---

## The decided stack, layer by layer

| Layer | General Legal | **Charter Law (decided)** | Why |
|-------|---------------|---------------------------|-----|
| Marketing site | Webflow | **Webflow** | No-code, you can edit copy yourself; clean and fast; same as GL |
| Customer portal | Vite + React + TS | **Vite + React + TypeScript** | Fast, standard, easy to hire for; identical to GL |
| Attorney app | Separate React app | **Separate React app, same stack** | Keeps internal tools cleanly apart from customer-facing app |
| Backend API | Python + FastAPI | **Python + FastAPI** | Best ecosystem for AI + document work; fast; identical to GL |
| Database | PostgreSQL | **PostgreSQL** via Google Cloud SQL | Reliable, standard, managed; identical to GL |
| Auth / login | Clerk | **Clerk** (organisation-based) | Handles login, orgs, sessions; identical to GL |
| Payments | Stripe | **Stripe** | Industry standard; identical to GL |
| File storage | Google Cloud | **Google Cloud Storage** | Secure contract storage next to the rest of the stack |
| AI / LLM | Anthropic Claude | **Anthropic Claude** | The engine; identical to GL |
| Word/redline | python-docx + Word plugin | **Claude for Word add-in** (+ structured redline tooling) | Produces real tracked changes lawyers expect |
| Hosting | Google App Engine | **Google Cloud Run** | Modern successor to App Engine; container-based, scales to zero |
| CDN / DNS | Cloudflare | **Cloudflare** | Speed + security in front of everything; identical to GL |
| Error monitoring | Sentry | **Sentry** | Tells you when something breaks; identical to GL |
| Analytics | Segment | **Segment** (add in Phase 5) | Product usage data; identical to GL |
| Email | Google Workspace | **Google Workspace** | Business email + identity |
| Agent interface | MCP server | **MCP server** (Phase 5) | Lets AI assistants use Charter Law; GL was first to do this |
| Package mgmt (Python) | — | **uv** | Much faster than pip; modern default |
| DB migrations | — | **Alembic + SQLAlchemy** | Safe, version-controlled schema changes |

---

## Notes on the choices that differ from General Legal

**Hosting → Cloud Run (not App Engine).** General Legal is on Google App Engine. For a brand-new project in 2026, Google itself steers you to **Cloud Run**: it runs your code in a container, scales to zero when idle (so you pay nothing when no one's using it), and avoids App Engine's "one app per project" limit. It runs the exact same FastAPI code. Think of it as the same destination via a newer, cheaper door.

**Redlines → Claude for Word (not raw python-docx).** This is the most important technical subtlety. The popular `python-docx` library **cannot create true Word "tracked changes"** — it's a well-known, long-standing limitation. Since lawyers live in tracked-changes redlines, we get them one of two ways: (1) the **Claude for Word add-in** (launched April 2026), which produces native tracked changes directly in Word — this is what General Legal uses; or (2) a structured pipeline where Claude outputs proposed edits as data and a specialised tool (e.g. open-source `legal-redline-tools`) renders them as real accept/reject markup. We'll lean on the Word add-in first because it matches how the attorney already works.

---

## How login works (so you understand the security model)

1. A customer logs in through **Clerk** on the React app.
2. Clerk hands the app a short-lived secure token (a "JWT").
3. Every time the app asks the backend for something, it attaches that token.
4. The **backend verifies the token on every single request** before doing anything — checking it's genuine, unexpired, and belongs to a real user.
5. The backend only ever returns data belonging to **that customer's organisation** — so one client can never see another's contracts.

This "verify on every request, scope to the org" pattern is the standard, secure way to do it, and Clerk's organisation feature maps cleanly onto "a client company with several team members." It's the same identity layer General Legal uses across both their portal and their AI agents.

---

## Recommended project structure (tell Claude Code to follow this)

Two top-level folders, clean separation, feature-organised frontend:

```
charter-law/
├── frontend/                 # Vite + React + TypeScript (customer portal)
│   └── src/features/         # organised BY FEATURE (matters, billing, auth…)
│                             #   each feature owns its components, hooks, API calls, types
├── attorney-app/             # second React app, internal-only
├── backend/                  # Python + FastAPI
│   ├── app/
│   │   ├── routers/          # thin API routes
│   │   ├── services/         # business logic (the real work lives here)
│   │   ├── models/           # SQLAlchemy DB models
│   │   ├── schemas/          # Pydantic request/response shapes (kept separate from models)
│   │   └── ai/               # Claude prompts + the prep pipeline
│   ├── alembic/              # database migrations
│   └── pyproject.toml        # managed with uv
└── infra/                    # deployment config (Cloud Run, etc.)
```

Build-quality principles to hold Claude Code to: thin routes + a service layer (don't pile logic into the API endpoints), SQLAlchemy models separate from Pydantic schemas, all secrets in environment variables (never in code or git), Alembic for every schema change, and automated tests against a throwaway test database.

---

## The data model, in plain terms (what the database holds)

The heart of it is the **matter** — one piece of legal work — and its status as it moves through the pipeline:

```
intake → ai_review → attorney_queue → attorney_review → delivered → completed
```

Core tables to start (Phase 3): **organisations** (client companies), **users** (people, linked to an org), **matters** (each contract job, with status + price + timestamps), **files** (the uploaded contract and the deliverable, stored in Cloud Storage with only references in the DB), and **events/audit** (who did what when — important for an attorney-accountable business).

Tables for the AI engine + playbook + workbench (Phase 4 — see `charter-law-super-prompt.md` Parts B4–B7):
- **issues** — each AI-found issue/edit on a matter, with a **confidence rating** (strong/medium/weak), the proposed redline/comment, and the attorney's disposition (applied/edited/dismissed + a reason tag).
- **playbooks** and **playbook_checks** — the structured risk/clause library: per contract type, each check holds a detection, **severity tier**, remediation intent, **preferred / acceptable / unacceptable fallback language**, and a tracked **per-check accuracy** stat. A **client_playbook_overlay** layers a client's house positions on the firm-wide base.
- **review_log (HuRT)** — attorney-minutes per matter (the core margin/automation metric).
- **benchmark_terms** (Phase 5) — anonymised, structured clause terms accumulated across matters to power "what's market" (capture early even if the feature ships later).

The single most important business rule, enforced in the backend: **a matter cannot move to `delivered` without a recorded attorney approval** (recorded in `events/audit`).

---

## Rough running costs while small

Webflow, Clerk, Stripe (a % of revenue), Cloud Run + Cloud SQL + Cloud Storage, Cloudflare, Sentry, the Anthropic API, and Google Workspace together land in the **low hundreds of dollars per month** until you have real volume — Cloud Run scaling to zero keeps the quiet periods cheap. Your dominant cost is the **developer**, then the **attorney** (paid per matter / on retainer as a cost-of-goods, not fixed overhead).

---

## Build order (mirrors the roadmap phases)

1. **Accounts + skeleton** — set up Google Cloud, Clerk, Stripe, GitHub, a "hello world" FastAPI on Cloud Run, an empty React app, an empty Postgres. Prove the pipes connect.
2. **Auth + matters** — login via Clerk; create/list matters; upload a file to Cloud Storage.
3. **Payments** — Stripe checkout wired to creating a matter.
4. **AI prep** — on upload, Claude generates summary + issue list + redline (internal only).
5. **Attorney app** — review queue, approve gate, deliver.
6. **Polish + scale** — Slack delivery, batch upload, analytics, MCP server, Word plugin.

---

## Sources (research behind this doc)

- [Cloud Run vs App Engine for FastAPI (2026)](https://oneuptime.com/blog/post/2026-02-17-how-to-choose-between-cloud-run-cloud-functions-app-engine-and-gke-for-your-workload/view) · [Google: deploy FastAPI to Cloud Run](https://docs.cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-fastapi-service) · [Compare App Engine and Cloud Run](https://docs.cloud.google.com/appengine/migration-center/run/compare-gae-with-run)
- [Clerk: verifyToken / backend auth](https://clerk.com/docs/reference/backend/verify-token) · [Authenticating API requests with Clerk + FastAPI](https://blog.lamona.tech/how-to-authenticate-api-requests-with-clerk-and-fastapi-6ac5196cace7) · [fastapi-clerk-middleware](https://github.com/OSSMafia/fastapi-clerk-middleware)
- [FastAPI + React + Vite production setup](https://dev.to/stamigos/modern-full-stack-setup-fastapi-reactjs-vite-mui-with-typescript-2mef) · [Production-ready FastAPI](https://oneuptime.com/blog/post/2026-01-26-fastapi-production-ready/view)
- [Cloud SQL Postgres + FastAPI + SQLAlchemy + Alembic](https://blog.devops.dev/a-scalable-approach-to-fastapi-projects-with-postgresql-alembic-pytest-and-docker-using-uv) · [Cloud SQL Python Connector](https://github.com/GoogleCloudPlatform/cloud-sql-python-connector/blob/main/README.md)
- [Claude contract redlining + tracked changes](https://claude.com/resources/use-cases/contract-redlining-and-negotiation) · [Claude for Word native redlines](https://www.smithstephen.com/p/claude-for-word-gives-lawyers-native) · [python-docx tracked-changes limitation / legal-redline-tools](https://github.com/evolsb/legal-redline-tools)
