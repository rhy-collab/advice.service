# Batch 05 Progress Log

## Issue 1 — Retention: delete the actual storage objects

**Status:** Completed

**What changed**
- Added `StorageService.delete_object(bucket, object_name)`.
- Retention now calls storage deletion before removing expired delivered/completed matter file rows.
- Retention reports `storage_objects_deleted`.
- Added attorney/admin trigger endpoint: `POST /v1/attorney/retention/purge`.
- Added tests with a fake storage service proving object deletion is called before rows disappear.

**Commands run**
- `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q`
- `npm run build`
- `git diff --check`

**Result**
- Backend tests passed: 52 passed, 3 existing warnings.
- Frontend production build passed.
- Whitespace check passed.

**Remaining work**
- Wire this endpoint to Cloud Scheduler or equivalent once production deployment exists.

## Issue 2 — Playbook-driven AI prep

**Status:** Completed

**What changed**
- Persisted `contract_type` on matters, including an Alembic migration for existing databases.
- AI prep now resolves the matching playbook for the matter's contract type during upload completion.
- Generated AI prep issues can reference `playbook_check_id` and `playbook_check_key`.
- The deterministic fallback still works when no matching playbook exists.
- Added tests for contract-type persistence and playbook-grounded AI prep output.

**Commands run**
- `/tmp/charter-law-backend-ci-venv/bin/python -m pytest -q`
- `npm run build`
- `git diff --check`

**Result**
- Backend tests passed: 53 passed, 3 existing warnings.
- Frontend production build passed.
- Whitespace check passed.

**Remaining work**
- Later Anthropic integration should use the same playbook-check context instead of inventing a separate prompt shape.
