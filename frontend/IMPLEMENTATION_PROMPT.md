# Charter Law Frontend Implementation Prompt

Use this prompt to continue the local Charter Law website and client portal build.

You are building Charter Law from the existing repo, using the Charter Law roadmap and tech stack as the source of truth. The public site should eventually live at `charterlaw.services`. The local development app is in `frontend/` and currently runs at `http://127.0.0.1:5173/`.

Read first:

1. `../charter-law-super-prompt.md`
2. `../charter-law-roadmap.md`
3. `../charter-law-tech-stack.md`
4. `../general-legal-dossier.md`

Live references checked in this build pass:

- `https://general.legal/` visible public positioning: outside counsel that scales like software, flat-fee contract review, portal/email/Slack-style channels, AI behind the scenes, attorney review, process and pricing sections.
- `https://portal.general.legal/dashboard` visible portal gate: client portal sign-in, Google sign-in, work email/password, sign-up, forgot password, encrypted/authenticated access message.

Current implementation:

- `/` is the Charter Law landing page.
- `/portal` is the Clerk-ready client portal shell.
- `/admin` is the first internal attorney-review/admin queue for approving deliverables.
- Clerk is installed through `@clerk/clerk-react`.
- Add `VITE_CLERK_PUBLISHABLE_KEY` from `.env.example` when a real Clerk app exists.
- Without a Clerk key, the portal stays in demo mode so design and layout can be reviewed locally.
- `src/main.tsx` is only routing/composition glue.
- Shared UI lives in `src/components/`.
- Landing UI lives in `src/features/landing/`.
- Portal UI lives in `src/features/portal/`.
- Demo matter data lives in `src/lib/demoData.ts`.
- The future FastAPI contract lives in `API_CONTRACT.md`.
- The FastAPI skeleton now lives in `../backend/`.
- The portal API client lives in `src/lib/portalApi.ts`.
- When `VITE_CLERK_PUBLISHABLE_KEY` exists, the frontend gets a Clerk token and sends it as `Authorization: Bearer <token>`.
- Backend demo auth is explicit through `CLERK_DEMO_AUTH=true`; production should set `CLERK_DEMO_AUTH=false`, `CLERK_JWKS_URL`, and `CLERK_JWT_ISSUER`.
- Backend matters/events now persist through SQLAlchemy models in `../backend/app/models/matter.py`.
- Local development defaults to SQLite via `DATABASE_URL=sqlite:///./charter_law_dev.db`; production should use PostgreSQL/Cloud SQL.
- Alembic migrations live under `../backend/alembic/`; the initial migration creates `matters` and `matter_events`.
- `../backend/alembic/versions/20260701_0002_create_matter_files.py` adds `matter_files` for source contract storage metadata.
- `../backend/alembic/versions/20260701_0003_add_upload_and_payment_state.py` adds `upload_status`, `payment_status`, and `checkout_session_id` on matters.
- Storage is wired through `../backend/app/services/storage_service.py`: real V4 Google Cloud Storage signed `PUT` URLs when `GOOGLE_APPLICATION_CREDENTIALS` exists, explicit demo upload targets otherwise.
- The portal now passes the selected `File` into `src/lib/portalApi.ts`; it uploads the file to GCS only when the backend returns `upload.mode === "gcs"`, skips network upload for demo mode, then calls `POST /v1/matters/{matter_id}/upload-complete`.
- Checkout is wired through `../backend/app/services/checkout_service.py`: real Stripe Checkout when `STRIPE_SECRET_KEY` and tier price IDs exist, explicit demo checkout otherwise.
- Checkout creation now sets matter `payment_status` to `checkout_pending`; `POST /v1/stripe/webhook` marks Stripe `checkout.session.completed` matters as `paid`.
- `POST /v1/matters/{matter_id}/attorney-approval` is an internal stand-in for attorney/admin approval. It requires upload complete + payment paid, records an `approved_redline` deliverable file, marks the matter `delivered`, and enables `GET /v1/matters/{matter_id}/download`.
- The portal table now shows upload, payment, and deliverable state; delivered matters show a `Download redline` action that asks the backend for the deliverable URL.
- The admin review queue lives in `src/features/admin/AdminPage.tsx`; it lists matters, shows upload/payment/delivery readiness, and calls the attorney approval route for matters ready to deliver.

Rules to preserve:

- Follow the committed stack: Vite + React + TypeScript for this customer-facing frontend.
- Do not rebuild this as Next.js just because the old Standard Legal app used Next.
- Keep the legal boundary visible: AI prepares; a reviewing attorney approves and owns.
- The portal should be organisation-scoped once the FastAPI backend exists.
- Never imply AI output is legal advice.
- Keep the public landing page serious, plain, and trust-led rather than clever or playful.

Next implementation slice:

1. Add real client-side routing with React Router or the repo's chosen Vite routing convention.
2. Add Clerk organisation-aware route guards in the frontend once real Clerk keys exist.
3. Replace the lightweight path switch in `src/main.tsx` with a real Vite/React routing convention.
4. Add real signed download URLs for approved GCS deliverables instead of deterministic demo URLs.
5. Replace the local SQLite URL with PostgreSQL/Cloud SQL in deployment config.
6. Run `npm run build`, `uv run pytest`, and browser-check `/`, `/portal`, and `/admin` after each slice.
