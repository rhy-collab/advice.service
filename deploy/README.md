# Deploy (Google Cloud Run)

Both services are containerised (`backend/Dockerfile`, `frontend/Dockerfile`). Secrets are supplied
via Cloud Run environment configuration only — never baked into images.

## Backend
```
gcloud run deploy charter-law-api \
  --source ./backend \
  --region <REGION> \
  --set-env-vars APP_ENV=production,RUN_MIGRATIONS_ON_STARTUP=true \
  --set-secrets DATABASE_URL=charter-db-url:latest,CLERK_JWKS_URL=clerk-jwks:latest,\
CLERK_JWT_ISSUER=clerk-issuer:latest,STRIPE_SECRET_KEY=stripe-sk:latest,\
STRIPE_WEBHOOK_SECRET=stripe-whsec:latest,GCS_BUCKET=charter-bucket:latest,\
SENTRY_DSN=sentry-dsn:latest \
  --allow-unauthenticated
```
On boot the app **validates production config and refuses to start** if a required secret is
missing or demo auth is enabled (see `backend/app/config.py`).

## Frontend
```
gcloud run deploy charter-law-web --source ./frontend --region <REGION> --allow-unauthenticated
```

## Human steps still required (blockers)
- Create the GCP project, Cloud SQL (Postgres) instance, and the GCS bucket.
- Store the secrets above in Secret Manager.
- Set `GOOGLE_APPLICATION_CREDENTIALS` for signed-URL generation.
These cannot be done in code; wire them once the accounts exist.
