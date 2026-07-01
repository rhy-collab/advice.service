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
