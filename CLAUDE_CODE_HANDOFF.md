# Claude Code Handoff: Charter Law Web Portal Build

This document is a detailed implementation handoff for Claude Code or any other AI coding agent taking over the Charter Law repository after the first major Codex build pass.

Read it before making changes. It explains what was built, why the choices were made, what was intentionally left unfinished, and where a future agent is most likely to make a harmful assumption.

## 1. Current Repository State

Repository remote:

```text
https://github.com/Charter-Law/Charter-Law.git
```

Active branch during this handoff:

```text
feat/charter-law-web-portal
```

The working objective was:

```text
Use the existing Standard Legal context, but follow the Charter Law roadmap and tech stack strictly as far as possible. Recover context, write a self-directed implementation super-prompt, build the Charter Law landing page and client portal using the provided stack, include Clerk where appropriate, and use browser/computer mode to inspect General Legal public/portal references.
```

The result is not yet production-ready, but it is no longer just a static concept. The repo now contains:

- A Vite + React + TypeScript customer-facing frontend in `frontend/`.
- A FastAPI backend in `backend/`.
- SQLAlchemy models and Alembic migrations for matters, matter events, matter files, upload state, payment state, and checkout session IDs.
- Clerk-ready frontend composition and backend JWT verification with explicit local demo auth.
- Stripe Checkout integration with explicit demo fallback and webhook handling.
- Google Cloud Storage upload-target generation with explicit demo fallback.
- A landing page at `/`.
- A customer portal at `/portal`.
- An internal attorney/admin review queue at `/admin`.
- Documentation that should help future agents continue without rediscovering the whole context.

## 2. Primary Planning Sources

The implementation should continue to treat these files as source-of-truth planning material:

```text
charter-law-super-prompt.md
charter-law-roadmap.md
charter-law-tech-stack.md
general-legal-dossier.md
charter-law-operating-playbook.md
frontend/API_CONTRACT.md
frontend/IMPLEMENTATION_PROMPT.md
build-system/issues-batch-01-engineering-foundation.md
build-system/issues-backlog-batches-02-07.md
```

The important strategic decision from the roadmap and tech-stack docs is:

```text
Follow the Charter Law stack, not the old Standard Legal app stack.
```

That means:

- Customer frontend: Vite + React + TypeScript.
- Backend: Python + FastAPI.
- Database: PostgreSQL/Cloud SQL eventually; local SQLite is only a development stand-in.
- Migrations: Alembic.
- ORM: SQLAlchemy.
- Auth: Clerk, organisation-based.
- Payments: Stripe hosted checkout only.
- File storage: Google Cloud Storage with signed URLs.
- Deployment target: Google Cloud Run.
- AI: Anthropic Claude later, internal-only until attorney approval.

Do not rebuild this as a Next.js app simply because Standard Legal had Next.js foundations. That would diverge from the Charter Law roadmap.

## 3. General Legal Reference Checks Already Done

The build was influenced by live checks of:

```text
https://general.legal/
https://portal.general.legal/dashboard
```

Observed public landing positioning from `https://general.legal/`:

- "Outside counsel that scales like software" style positioning.
- Flat-fee legal services.
- Contract review as a clear wedge.
- Portal/email/Slack-style work channels.
- AI behind the scenes.
- Attorney review as the trust layer.
- Pricing and process sections.

Observed portal gate from `https://portal.general.legal/dashboard`:

- `CLIENT PORTAL`.
- Sign in to view matters.
- Sign in with Google.
- Work email/password.
- Forgot password.
- Sign up.
- Encrypted/authenticated access wording.

These checks were used as product inspiration, not as code cloning. The Charter Law implementation must stay truthful to Charter Law's current legal and operational reality.

## 4. Legal Boundary To Preserve

This is the most important invariant:

```text
AI prepares. A reviewing attorney approves and owns.
```

Never expose AI-generated legal work to a customer as legal advice. Do not let a matter become `delivered` unless attorney approval is recorded server-side.

The backend currently enforces part of this by:

- Rejecting raw `transition_status(..., "delivered")` unless `attorney_approved=True`.
- Requiring upload complete and payment paid before `approve_deliverable`.
- Recording an `attorney_approved` event before enabling customer download.
- Returning a download URL only after the matter is delivered and a deliverable file exists.

Future AI features must preserve that same gate. If Claude Code adds document summarisation, issue extraction, redline generation, or assistant answers, those outputs should be internal-only until the attorney approval route says they can be delivered.

## 5. Frontend Overview

Frontend root:

```text
frontend/
```

Main files:

```text
frontend/package.json
frontend/vite.config.ts
frontend/tsconfig.json
frontend/src/main.tsx
frontend/src/styles.css
frontend/src/components/SiteHeader.tsx
frontend/src/components/MatterCard.tsx
frontend/src/components/AssistantCard.tsx
frontend/src/features/landing/LandingPage.tsx
frontend/src/features/portal/PortalPage.tsx
frontend/src/features/admin/AdminPage.tsx
frontend/src/lib/demoData.ts
frontend/src/lib/portalApi.ts
frontend/API_CONTRACT.md
frontend/IMPLEMENTATION_PROMPT.md
```

### Current Frontend Routes

Routing is intentionally simple for now. `frontend/src/main.tsx` uses `window.location.pathname` to pick one of:

```text
/        -> LandingPage
/portal  -> PortalPage
/admin   -> AdminPage
```

This should eventually be replaced with a real Vite/React routing convention, probably React Router. That was intentionally not done in the last slice because the user asked to push current work, not start another larger refactor.

### Landing Page

Path:

```text
/
```

Component:

```text
frontend/src/features/landing/LandingPage.tsx
```

The landing page is serious, plain, and trust-led. It is not a marketing-only placeholder; it reflects the wedge:

- Attorney-reviewed contract redlines for startup teams.
- Flat-fee contract-review tiers.
- AI prep plus attorney approval.
- A preview of the matter tracker/assistant concept.
- CTA for intake at `hello@charterlaw.services`.

Future work:

- Replace mailto intake with real intake/checkout flow.
- Add more General Legal-inspired process detail without copying text.
- Improve public trust/compliance copy after attorney review.
- Add analytics once Cloud/Vercel/Cloudflare decisions are made.

### Client Portal

Path:

```text
/portal
```

Component:

```text
frontend/src/features/portal/PortalPage.tsx
```

The portal currently supports:

- Clerk-ready sign-in controls.
- Demo fallback when `VITE_CLERK_PUBLISHABLE_KEY` is absent.
- Matter list loaded from FastAPI when available.
- Demo data fallback when FastAPI is unavailable.
- `.docx` selection and validation.
- Matter creation through `POST /v1/matters`.
- GCS upload only when backend returns `upload.mode === "gcs"`.
- Demo upload skip when backend returns `upload.mode === "demo"`.
- Upload completion through `POST /v1/matters/{matter_id}/upload-complete`.
- Checkout creation through `POST /v1/matters/{matter_id}/checkout`.
- Table columns for file, status, upload, payment, deliverable, submitted, and next update.
- Download action for delivered matters through `GET /v1/matters/{matter_id}/download`.
- Assistant shell that is carefully framed as preparation, not legal advice.

Important frontend fallback behavior:

- If API calls fail, the portal falls back to demo matters.
- In demo mode, `createPortalMatter` returns a local fake matter and fake Stripe demo checkout URL.
- This makes local visual review easy but can hide backend failures if you only look at the UI. Always run API smoke checks when validating backend changes.

### Internal Admin / Attorney Review Page

Path:

```text
/admin
```

Component:

```text
frontend/src/features/admin/AdminPage.tsx
```

This is a first internal review queue, not a full attorney app. It exists because the backend already had an attorney approval route and the user wanted the project to keep moving toward an end-to-end workflow.

It currently:

- Lists matters from the same `GET /v1/matters` endpoint.
- Shows upload, payment, and delivery readiness.
- Shows counts for ready-to-approve, delivered, and total matters.
- Allows approval through `POST /v1/matters/{matter_id}/attorney-approval`.
- Keeps the wording explicit that this is internal and attorney-controlled.

Limitations:

- It is not role-gated yet.
- It is not a separate `attorney-app/`.
- It uses the same demo auth fallback as the portal when Clerk is not configured.
- It does not display AI prep output, redline diffs, issue lists, or confidence scoring yet.

Future agent warning:

Do not expose `/admin` publicly in production without role checks. It is a local internal workflow shell, not production access control.

## 6. Backend Overview

Backend root:

```text
backend/
```

Main files:

```text
backend/pyproject.toml
backend/.env.example
backend/alembic.ini
backend/alembic/env.py
backend/alembic/versions/20260701_0001_create_matter_tables.py
backend/alembic/versions/20260701_0002_create_matter_files.py
backend/alembic/versions/20260701_0003_add_upload_and_payment_state.py
backend/app/main.py
backend/app/db/session.py
backend/app/models/matter.py
backend/app/routers/users.py
backend/app/routers/matters.py
backend/app/schemas/matters.py
backend/app/services/auth.py
backend/app/services/checkout_service.py
backend/app/services/matter_service.py
backend/app/services/storage_service.py
backend/tests/
backend/uv.lock
```

### Backend Dependencies

Defined in:

```text
backend/pyproject.toml
```

Current major dependencies:

- FastAPI.
- Uvicorn.
- SQLAlchemy.
- Alembic.
- Pydantic.
- PyJWT with crypto.
- Stripe.
- Google Cloud Storage.
- Pytest and HTTPX for tests.

### Backend Local Environment

Example env:

```text
backend/.env.example
```

Important variables:

```text
CLERK_DEMO_AUTH=true
CLERK_JWKS_URL=https://example.clerk.accounts.dev/.well-known/jwks.json
CLERK_JWT_ISSUER=https://example.clerk.accounts.dev
DATABASE_URL=sqlite:///./charter_law_dev.db
RUN_MIGRATIONS_ON_STARTUP=true
STRIPE_SECRET_KEY=sk_test_replace_me
STRIPE_PRICE_SIMPLE_REVIEW=price_replace_me
STRIPE_PRICE_STANDARD_REDLINE=price_replace_me
STRIPE_PRICE_FULL_NEGOTIATION=price_replace_me
STRIPE_SUCCESS_URL=http://127.0.0.1:5173/portal?checkout=success
STRIPE_CANCEL_URL=http://127.0.0.1:5173/portal?checkout=cancelled
STRIPE_WEBHOOK_SECRET=whsec_replace_me
GCS_BUCKET=charter-law-contracts-dev
GCS_SIGNED_URL_TTL_MINUTES=15
```

Do not commit real secrets.

### Backend Routes

Defined mostly in:

```text
backend/app/routers/matters.py
backend/app/routers/users.py
```

Current routes:

```text
GET  /health
GET  /v1/me
GET  /v1/matters
POST /v1/matters
GET  /v1/matters/{matter_id}
POST /v1/matters/{matter_id}/upload-complete
POST /v1/matters/{matter_id}/checkout
GET  /v1/matters/{matter_id}/download
POST /v1/matters/{matter_id}/attorney-approval
POST /v1/assistant/messages
POST /v1/stripe/webhook
```

### Auth

Implemented in:

```text
backend/app/services/auth.py
```

Current behavior:

- If `CLERK_DEMO_AUTH=true`, unauthenticated local requests are allowed as `org_demo`.
- If demo auth is false, requests must include `Authorization: Bearer <token>`.
- JWTs are verified against Clerk JWKS and issuer env vars.
- `org_id` is required.
- Every protected route receives an `AuthContext`.

Production risk:

Demo auth must be disabled before real client data touches the system.

### Data Model

Implemented in:

```text
backend/app/models/matter.py
```

Current tables:

- `matters`
- `matter_events`
- `matter_files`

Current matter lifecycle:

```text
intake -> ai_review -> attorney_queue -> attorney_review -> delivered -> completed
```

Current matter state fields include:

- `status`
- `upload_status`
- `payment_status`
- `checkout_session_id`
- `submitted_at`
- `next_update_eta_minutes`
- `deliverable_available`

Current file roles:

- `source_contract`
- `approved_redline`

### Migrations

Alembic migrations:

```text
20260701_0001_create_matter_tables.py
20260701_0002_create_matter_files.py
20260701_0003_add_upload_and_payment_state.py
```

Local backend startup runs migrations when:

```text
RUN_MIGRATIONS_ON_STARTUP=true
```

This is convenient locally but may not be the final production migration strategy.

### Matter Service

Implemented in:

```text
backend/app/services/matter_service.py
```

Important behavior:

- `create_matter` creates matter, event, and source file metadata.
- `mark_upload_complete` marks `upload_status = uploaded`.
- `mark_checkout_created` records checkout session ID and marks `payment_status = checkout_pending`.
- `mark_payment_status` marks payment states, including `paid`.
- `approve_deliverable` enforces:
  - matter exists;
  - upload is complete;
  - payment is paid;
  - then records `approved_redline`, marks delivered, clears ETA, and enables download.
- `delivery_download_url` refuses download until delivered and a deliverable file exists.

### Storage Service

Implemented in:

```text
backend/app/services/storage_service.py
```

Current behavior:

- If `GOOGLE_APPLICATION_CREDENTIALS` exists, generate a V4 signed GCS PUT URL.
- Otherwise return a deterministic demo upload URL.
- Stores object paths like:

```text
matters/{matter_id}/source/{file_name}
matters/{matter_id}/deliverables/{deliverable_file_name}
```

Important limitation:

Download currently returns a deterministic GCS URL built from stored bucket/object metadata. For production, replace this with real signed download URLs.

### Checkout Service

Implemented in:

```text
backend/app/services/checkout_service.py
```

Current behavior:

- If Stripe secret key and tier price ID exist, creates a real Stripe Checkout Session.
- Otherwise returns a fake but clearly marked demo checkout URL.
- Stripe webhook validates signature if `STRIPE_WEBHOOK_SECRET` is present.
- Without webhook secret, local development accepts Stripe-shaped JSON for smoke testing.

Production risk:

Real production must set `STRIPE_WEBHOOK_SECRET` and verify webhook signatures.

## 7. Local Run Commands

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL:

```text
http://127.0.0.1:5173/
```

Backend:

```bash
cd backend
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend health:

```text
http://127.0.0.1:8000/health
```

Current local review URLs:

```text
http://127.0.0.1:5173/
http://127.0.0.1:5173/portal
http://127.0.0.1:5173/admin
http://127.0.0.1:8000
```

## 8. Verification Commands Already Used

Backend tests:

```bash
cd backend
uv run pytest
```

Current result at handoff:

```text
13 passed
```

Frontend build:

```bash
cd frontend
npm run build
```

Current result at handoff:

```text
passed
```

Browser checks were performed in the in-app browser:

- `/` opened successfully.
- `/portal` connected to FastAPI, showed upload/payment/deliverable table, no page overflow.
- `/admin` connected to FastAPI, showed attorney delivery queue, readiness states, approval controls, no page overflow.

API smoke flows were also run locally:

1. Create matter.
2. Mark upload complete.
3. Create checkout.
4. Simulate Stripe checkout-completed webhook.
5. Approve deliverable.
6. Fetch download URL.

That smoke proved the event chain:

```text
matter_created
upload_completed
checkout_created
payment_paid
attorney_approved
```

## 9. Current End-to-End Flow

The current local flow is:

1. Customer opens `/portal`.
2. Customer selects a `.docx`.
3. Frontend posts to `POST /v1/matters`.
4. Backend creates matter, source file metadata, and upload target.
5. Frontend uploads file only if `upload.mode === "gcs"`.
6. In demo mode, frontend skips real upload.
7. Frontend calls `POST /v1/matters/{matter_id}/upload-complete`.
8. Frontend calls `POST /v1/matters/{matter_id}/checkout`.
9. Backend marks payment as `checkout_pending`.
10. Stripe webhook marks payment as `paid`.
11. Internal user opens `/admin`.
12. Internal user approves ready matter.
13. Backend records `approved_redline`, marks matter `delivered`, and enables download.
14. Customer sees `Download redline` on `/portal`.
15. Customer requests `GET /v1/matters/{matter_id}/download`.

This is a serious scaffold of the General Legal-like workflow, but it is still local-demo infrastructure until real Clerk, Stripe, GCS, database, and deployment are configured.

## 10. Where The Roadmap Was Followed Exactly

The implementation followed the Charter Law roadmap/tech stack in these areas:

- Used Vite + React + TypeScript for the customer-facing frontend.
- Used Python + FastAPI for the backend.
- Used SQLAlchemy and Alembic for data persistence.
- Used Clerk on the frontend and server-side JWT verification structure on the backend.
- Used Stripe hosted Checkout only; no card handling in app code.
- Used Google Cloud Storage signed-upload architecture; local demo mode only when credentials are absent.
- Enforced the legal gate that a final deliverable is not available until attorney approval.
- Kept AI output out of the customer-facing workflow for now.
- Preserved organisation-scoped request design through `AuthContext.organisation_id`.
- Created a portal with upload, status, payment, delivery, and download primitives.
- Created an internal attorney/admin queue rather than letting delivery happen only through raw API calls.

## 11. Where The Implementation Is Still A Compromise

These are not failures, but they matter:

1. Local SQLite stands in for Postgres/Cloud SQL.
   - The roadmap says PostgreSQL/Cloud SQL.
   - Local SQLite was used to move quickly and keep the prototype runnable.
   - Future work should add a real local Postgres/test DB and Cloud SQL deployment config.

2. Clerk is not fully configured.
   - Frontend uses Clerk if `VITE_CLERK_PUBLISHABLE_KEY` exists.
   - Backend can verify Clerk JWTs if env vars are set.
   - Local demo auth is enabled by `CLERK_DEMO_AUTH=true`.
   - Production must disable demo auth and add role/org enforcement.

3. `/admin` is not role-gated.
   - It is a local internal workflow shell.
   - Do not expose it publicly until Clerk role/permission checks exist.

4. GCS upload is demo unless credentials exist.
   - The architecture is ready for signed PUT URLs.
   - Production requires real GCS bucket, service account, CORS settings, object lifecycle policy, and signed download URLs.

5. Stripe is demo unless env keys exist.
   - The code uses hosted checkout.
   - Local checkout returns `https://checkout.stripe.com/c/pay/demo-...`.
   - Production requires real price IDs and webhook secret.

6. No real AI prep pipeline exists yet.
   - No Claude document ingestion.
   - No issue list.
   - No Word tracked-changes redline.
   - No internal confidence scoring.
   - That is later roadmap work.

7. No separate `attorney-app/` exists.
   - The current `/admin` page is inside the same frontend.
   - The backlog still describes a future separate internal app.
   - Do not mistake the current `/admin` for the final lawyer workbench.

8. No production deployment exists yet.
   - No Cloud Run config.
   - No Dockerfiles.
   - No Sentry.
   - No CI.
   - No Cloudflare/domain wiring.

9. Routing is simple path switching.
   - `main.tsx` manually checks `window.location.pathname`.
   - Replace with React Router or another agreed Vite routing convention soon.

10. File validation is light.
   - Frontend validates `.docx` extension.
   - Backend does not yet enforce file type/size strongly.

11. Download URL is not a real signed URL.
   - It returns deterministic GCS URL from stored metadata.
   - Production should return short-lived signed URLs.

## 12. High-Risk Mistakes For A Future Agent

Avoid these:

1. Do not delete the attorney approval gate.
2. Do not let customers download AI drafts.
3. Do not enable `CLERK_DEMO_AUTH=true` in production.
4. Do not expose `/admin` without role checks.
5. Do not store contract file bytes in the database.
6. Do not add card handling to the frontend or backend.
7. Do not commit `.env`, service-account JSON, SQLite DBs, `.venv`, `node_modules`, or `dist`.
8. Do not switch to Next.js without an explicit user/roadmap decision.
9. Do not rely on frontend-sent organisation IDs for access control.
10. Do not treat the General Legal references as permission to copy proprietary copy, design, or code.
11. Do not present Charter Law as a fully operational law firm until the attorney/legal-structure layer is truly set up.
12. Do not call AI output legal advice.

## 13. Suggested Next Implementation Order

If Claude Code continues from here, a good order is:

1. Replace the manual route switch in `frontend/src/main.tsx` with React Router.
   - Keep `/`, `/portal`, and `/admin`.
   - Preserve current browser behavior.

2. Add Clerk role/permission checks.
   - Customer users can access `/portal`.
   - Internal attorney/admin users can access `/admin`.
   - Backend should enforce roles too, not just frontend hiding.

3. Strengthen backend auth tests.
   - Add cross-org isolation tests for matters.
   - Add tests proving one org cannot fetch/download another org's matter.

4. Add real signed download URLs.
   - Extend `StorageService` with download signed URL generation.
   - Replace deterministic URL in `delivery_download_url`.
   - Test demo and GCS paths.

5. Add backend file validation.
   - Extension.
   - MIME/content type.
   - Size.
   - Possibly malware scanning later.

6. Add a proper matter detail view.
   - Timeline events.
   - File metadata.
   - Download state.
   - Assistant thread shell.

7. Add Cloud SQL/Postgres config.
   - Keep SQLite only for quick local dev if desired.
   - Add test DB strategy.

8. Add CI.
   - Backend tests.
   - Frontend build.
   - Lint/format if introduced.

9. Add deployment config.
   - Cloud Run.
   - Dockerfiles.
   - Runtime env docs.
   - Sentry.

10. Start AI prep engine only after the legal and access gates are solid.

## 14. Exact Files To Read Before Continuing

Claude Code should read these in this order:

```text
CLAUDE_CODE_HANDOFF.md
charter-law-roadmap.md
charter-law-tech-stack.md
frontend/IMPLEMENTATION_PROMPT.md
frontend/API_CONTRACT.md
backend/app/models/matter.py
backend/app/services/matter_service.py
backend/app/routers/matters.py
frontend/src/lib/portalApi.ts
frontend/src/features/portal/PortalPage.tsx
frontend/src/features/admin/AdminPage.tsx
```

Then run:

```bash
cd backend && uv run pytest
cd frontend && npm run build
```

Then browser-check:

```text
http://127.0.0.1:5173/
http://127.0.0.1:5173/portal
http://127.0.0.1:5173/admin
```

## 15. Current Quality Bar

Do not call a future slice done unless:

- Backend tests pass.
- Frontend build passes.
- A browser check confirms the relevant route renders.
- Any backend route change has a service or integration test.
- The legal gate remains intact.
- The handoff docs stay truthful.

## 16. Plain-English Product Summary

Charter Law is being built as a flat-fee contract-review service for startup teams. Customers should be able to upload a Word contract, pay a clear price, track progress, and download an attorney-approved redline. AI can help prepare the work internally, but the customer-facing legal output must be approved by a reviewing attorney. The current codebase now has the first working skeleton of that journey: landing page, client portal, matter creation, upload state, payment state, attorney approval, and download state. It still needs real production auth, real cloud storage, real deployment, role-gated admin access, and the AI/attorney workbench.
