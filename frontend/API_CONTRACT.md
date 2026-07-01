# Charter Law Portal API Contract

This is the frontend-to-backend contract for the first real portal slice. It follows `../charter-law-tech-stack.md`: Vite + React + TypeScript frontend, Python + FastAPI backend, PostgreSQL, Google Cloud Storage, Stripe hosted checkout, and Clerk organisation-based auth.

## Auth Boundary

Every request from `/portal` to the backend must include the Clerk session token:

```http
Authorization: Bearer <clerk_jwt>
```

The FastAPI backend must verify that token on every request. It must derive the user and organisation from Clerk, then scope every query by `organisation_id`. The frontend must never send an organisation id as a trust source for access control.

Local development can run with `CLERK_DEMO_AUTH=true`, which allows unauthenticated demo requests while the Clerk project is not configured. Production must set `CLERK_DEMO_AUTH=false` and configure `CLERK_JWKS_URL`, `CLERK_JWT_ISSUER`, and `CLERK_JWT_AUDIENCE`.

The current local backend persists matters/events through SQLAlchemy. Local development defaults to SQLite through `DATABASE_URL=sqlite:///./charter_law_dev.db`; production should use PostgreSQL/Cloud SQL. Schema is versioned through Alembic under `backend/alembic/`.

## Public Lead-Gen Routes

These routes are intentionally outside the authenticated portal. They do not grant access to customer matters and must not expose legal advice.

### `POST /v1/public/check-contract`

Accepts a single `.docx` upload for the free Contract Mistake Checker. The backend reads the document in memory, returns a preparation-only report, and stores nothing.

Request:

```http
Content-Type: multipart/form-data
file=<contract.docx>
```

Response:

```json
{
  "fileName": "vendor-saas-agreement.docx",
  "stored": false,
  "wordCount": 1240,
  "findings": [
    {
      "type": "broken_cross_reference",
      "severity": "warning",
      "title": "Referenced section 9.1 was not found",
      "detail": "The document refers to Section 9.1, but no matching numbered heading was detected.",
      "evidence": "Section 9.1"
    }
  ],
  "disclaimer": "Free preparation check only. This is not legal advice and no contract is saved or stored.",
  "nextStep": "For a legal review, submit the contract for an attorney-approved Charter Law redline."
}
```

Privacy invariant: `stored` must remain `false`; the checker must not create matter rows, intake rows, GCS objects, or logs containing contract text.

### `POST /v1/public/intake`

Captures pre-login review interest for the manual MVP / public site flow. This is a lead record, not a customer matter and not the start of legal advice.

Request:

```json
{
  "name": "Maya Founder",
  "email": "maya@example.com",
  "company": "Acme Labs",
  "contractType": "vendor_saas",
  "urgency": "standard",
  "serviceTier": "standard_redline",
  "notes": "Need a clean redline before Friday."
}
```

Response:

```json
{
  "intakeId": "intake_abc123",
  "status": "new",
  "createdAt": "2026-07-01T10:00:00Z",
  "message": "Thanks. Charter Law will review the intake and follow up before any legal work begins."
}
```

## Matter Lifecycle

Frontend status labels map to backend states:

| UI label | Backend state |
| --- | --- |
| Received | `intake` |
| AI Review | `ai_review` |
| Queued for Attorney | `attorney_queue` |
| Attorney Review | `attorney_review` |
| Delivered | `delivered` |
| Completed | `completed` |

Invariant: the backend must reject any transition to `delivered` unless an attorney approval event exists for the matter.

## Required Routes

### `GET /v1/me`

Returns the authenticated user and active Clerk organisation.

```json
{
  "user": {
    "id": "user_123",
    "email": "founder@example.com",
    "name": "Founder Example"
  },
  "organisation": {
    "id": "org_123",
    "name": "Acme Labs"
  }
}
```

### `GET /v1/matters`

Returns only matters belonging to the active organisation.

```json
{
  "matters": [
    {
      "id": "matter_123",
      "fileName": "vendor-saas-agreement.docx",
      "serviceTier": "standard_redline",
      "status": "attorney_review",
      "uploadStatus": "uploaded",
      "paymentStatus": "checkout_pending",
      "submittedAt": "2026-07-01T10:00:00Z",
      "nextUpdateEtaMinutes": 42,
      "deliverableAvailable": false
    }
  ]
}
```

### `POST /v1/matters`

Creates an intake matter before upload and returns a signed upload target or resumable upload instruction.

Request:

```json
{
  "fileName": "vendor-saas-agreement.docx",
  "serviceTier": "standard_redline",
  "contractType": "vendor_saas",
  "notes": "Please focus on liability cap and DPA terms."
}
```

Response:

```json
{
  "matterId": "matter_123",
  "status": "intake",
  "upload": {
    "method": "PUT",
    "url": "https://storage.googleapis.com/...",
    "expiresAt": "2026-07-01T10:15:00Z",
    "mode": "gcs"
  }
}
```

Current local behavior: when `GOOGLE_APPLICATION_CREDENTIALS` is absent, the backend returns `"mode": "demo"` and a deterministic demo Google Storage URL. When credentials are present, it returns a V4 signed GCS `PUT` URL. The frontend uploads the selected `.docx` file only for `"mode": "gcs"` and skips the network upload for demo mode.

### `POST /v1/matters/{matter_id}/upload-complete`

Marks the source contract as uploaded after the browser finishes the GCS `PUT` request. The frontend also calls this route in demo mode after skipping the fake upload.

Response:

```json
{
  "matter": {
    "id": "matter_123",
    "fileName": "vendor-saas-agreement.docx",
    "serviceTier": "standard_redline",
    "status": "intake",
    "uploadStatus": "uploaded",
    "paymentStatus": "unpaid",
    "submittedAt": "2026-07-01T10:00:00Z",
    "nextUpdateEtaMinutes": 15,
    "deliverableAvailable": false
  }
}
```

### `POST /v1/matters/{matter_id}/checkout`

Creates a Stripe hosted checkout session for the selected flat-fee tier.

Response:

```json
{
  "checkoutUrl": "https://checkout.stripe.com/c/pay/...",
  "mode": "stripe",
  "sessionId": "cs_test_123"
}
```

When Stripe keys/price IDs are not configured, local development returns a clearly marked demo checkout URL with `"mode": "demo"`. Production must use Stripe hosted checkout only; the app must never handle card data directly.

### `POST /v1/stripe/webhook`

Receives Stripe `checkout.session.completed` events and marks the matter payment state as `paid`. Production should configure `STRIPE_WEBHOOK_SECRET`; local development accepts Stripe-shaped JSON without a signature so the flow can be smoke-tested.

### `GET /v1/matters/{matter_id}`

Returns matter details, timeline events, current status, assistant-safe context, and deliverable metadata.

### `GET /v1/matters/{matter_id}/download`

Returns a short-lived signed download URL for the approved deliverable. Only available after `delivered`.

## Attorney Routes

These routes power `/attorney`. They require an attorney/admin role claim server-side through `require_attorney_context`.

### `GET /v1/attorney/queue`

Returns matters in `attorney_queue` or `attorney_review` for the active organisation.

### `GET /v1/attorney/matters/{matter_id}/ai-prep`

Returns the latest internal-only AI preparation summary and issue list for an attorney/admin. This is never returned by customer matter routes.

### `POST /v1/attorney/matters/{matter_id}/approve`

Approves the final client deliverable. It requires attorney/admin auth, source upload complete, payment `paid`, and a matter status of `attorney_queue` or `attorney_review`. It records an `approved_redline` file, marks the matter `delivered`, and enables customer download.

Request:

```json
{
  "deliverableFileName": "vendor-saas-agreement-redline.docx",
  "note": "Attorney approved the redline for client delivery."
}
```

### `POST /v1/assistant/messages`

Sends a portal assistant message. The backend decides whether the message can receive an AI preparation answer or must route to the attorney.

Request:

```json
{
  "matterId": "matter_123",
  "mode": "ai_preparation",
  "message": "What are the key risks?"
}
```

Response:

```json
{
  "mode": "ai_preparation",
  "answer": "This is preparation only, not legal advice...",
  "routedToAttorney": false
}
```

## Frontend States To Implement Next

- Signed out portal gate. Current shell is Clerk-ready with demo fallback.
- Signed in empty matter list.
- `.docx` selected but not uploaded. Implemented locally.
- Upload pending. Implemented locally.
- Upload success with matter in `intake`. Implemented locally with demo/GCS mode status.
- Upload validation error for non-`.docx` file. Implemented locally.
- Stripe checkout pending. Implemented locally; checkout creation sets `paymentStatus` to `checkout_pending`.
- Stripe payment completed. Implemented locally through the webhook; production requires `STRIPE_WEBHOOK_SECRET`.
- Matter delivered with download button. Implemented locally after attorney approval.
- Internal attorney approval route and `/admin` review queue. Implemented locally as the first internal attorney/admin surface.
- Assistant answer routed to attorney.

## Security Notes

- Never store real client contracts in local fixtures.
- Never expose Google Cloud Storage object names directly as durable public URLs.
- Never trust frontend-sent status transitions.
- Never show AI-generated legal work to the client until attorney approval is recorded.
