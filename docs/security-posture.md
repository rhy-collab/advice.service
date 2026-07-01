# Security Posture (current)

Enforced in code and covered by tests:

- **Attorney-owned delivery.** A matter reaches `delivered` only via a recorded approval by a user
  with an attorney/admin role (`require_attorney_context`); enforced server-side, tested.
- **Legal lifecycle only.** Status moves follow `LEGAL_TRANSITIONS`; illegal jumps return 409.
- **Organisation isolation.** Every matter/event/report query is scoped to the caller's org; a
  cross-org read returns 404/empty. Negative tests included.
- **Fail-closed auth.** Demo auth is off unless `CLERK_DEMO_AUTH=true`; production config validation
  refuses to boot with demo auth on or required secrets missing (`app/config.py`).
- **Confidential files.** Uploads and downloads use short-lived **signed** URLs; no public object
  URL path exists for real files; file bytes never stored in the DB.
- **Auditability.** Every action writes a `matter_events` row; readable via the audit endpoint.
- **Payments.** Stripe hosted checkout only; webhook signatures verified.

Still required before real client contracts (human/external):
- The one-off freelance security review.
- Real Clerk/GCS/Stripe/Sentry accounts + Secret Manager.
- Encryption-at-rest confirmation on Cloud SQL + GCS; retention/deletion policy.
