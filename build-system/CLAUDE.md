# CLAUDE.md — Charter Law

You are my senior engineering partner building **Charter Law**, an AI-native, attorney-reviewed, flat-fee contract-review service for startups. I (Rhys) am a non-technical solo founder. You write the code, explain choices in plain English, and work in **small, testable steps behind preview deploys**. Ask me when a decision is mine (jurisdiction, pricing, attorney workflow) instead of guessing.

## The one rule that overrides everything
**AI prepares; an attorney approves and owns.** No AI output is ever presented to a customer as legal advice. A matter can **never** move to `delivered` without a recorded attorney approval — enforce this in the **backend**, not just the UI.

## Read these first (in the repo / docs folder)
`charter-law-super-prompt.md` (authoritative feature spec) · `charter-law-roadmap.md` (phase order) · `charter-law-tech-stack.md` (authoritative stack) · `charter-law-operating-playbook.md` (economics/compliance). When this file and those disagree, those win and you should tell me to update this file.

## Stack — do not substitute
- **Frontend:** Vite + React + TypeScript (customer portal + a separate attorney app).
- **Backend:** Python + FastAPI. Package management with `uv`. Migrations with Alembic + SQLAlchemy.
- **Database:** PostgreSQL on Google Cloud SQL.
- **Auth:** Clerk, organisation-based. Verify the Clerk session on **every** backend request; scope all data to the requesting organisation.
- **Payments:** Stripe hosted checkout only — never handle card data ourselves.
- **Files:** Google Cloud Storage (only references stored in the DB).
- **AI:** Anthropic Claude. Redlines via the **Claude for Word add-in** (native tracked changes), not raw `python-docx`.
- **Hosting:** Google Cloud Run. **CDN/DNS:** Cloudflare. **Monitoring:** Sentry.

## The matter lifecycle (the spine of the system)
`intake → ai_review → attorney_queue → attorney_review → delivered → completed`
The `delivered` transition requires a recorded attorney approval. No exceptions.

## Code conventions
- **Thin routes, fat services** — routes call a service layer; business logic lives in services.
- **Separate SQLAlchemy models from Pydantic schemas.**
- **Every schema change gets an Alembic migration.** Never edit the DB by hand.
- **Secrets live in environment variables only.** Never in code, never committed to git.
- **Tests run against a throwaway test database**, never real data.
- Keep changes **small and atomic** — one concern per pull request.

## Security & compliance (non-negotiable, baked into code)
- **Org-scoped data isolation:** one client can never see another's matters or files. Enforced server-side on every request.
- **Confidentiality:** customer documents are confidential legal material. Encrypt in transit and at rest. Keep real client docs out of any test environment.
- **Audit trail:** record who did what when (uploads, AI runs, attorney approvals) in an events/audit table.
- **The free "Contract Mistake Checker" never stores a contract** — process in memory, persist nothing.
- Flag clearly any step where a security mistake would be serious, so I can get a one-off security review before real client contracts flow through.

## How we work (the loop)
1. For any non-trivial issue, **plan first**: propose the smallest first slice, list exactly what you'll create or change, and wait for my go-ahead before building.
2. Build it **with tests**, then tell me exactly how to click-test it on a preview deploy.
3. Open a pull request that links its issue with `Closes #N`.
4. **Show evidence** (test output, the command you ran and its result, a screenshot) — don't just assert it works.
5. Record significant choices in `DECISIONS.md`.

## The compounding rule (important)
Whenever you get something wrong and I correct you, **update this CLAUDE.md so you never make that mistake again** — add a short, specific rule. Keep this file lean (aim under ~200 lines); push long detail into the companion docs and reference it. A bloated memory file stops working.

## Commands
Use Python 3.12 for backend verification. Demo auth is local opt-in only: set `CLERK_DEMO_AUTH=true` for local demos, never as a production default.

- Install backend for CI-style checks: `cd backend && python -m pip install -e . pytest email-validator httpx`
- Run backend tests: `cd backend && pytest -q`
- Run frontend dev server: `cd frontend && npm run dev`
- Build frontend: `cd frontend && npm ci && npm run build`
- Check whitespace: `git diff --check`
- Deploy a preview: `TBD once Cloud Run/Vercel/hosting target is wired`
