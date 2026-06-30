# Decisions Log — Charter Law

*Append-only running log of decisions that shape the build, so you and the AI stay oriented across sessions. Newest at the top. One short entry per decision: what was decided, why, and the date.*

---

## 2026-06-30 — Build system stood up
Created the compound-engineering build scaffolding (`CLAUDE.md`, issue/PR templates, this log, tooling guide). The issue-driven loop is the operating model: GitHub is the system of record; the AI's chat is disposable. **Why:** so every session starts oriented and lessons compound into the files rather than being lost.

## 2026-06-30 — Build order follows the existing roadmap (not engine-first)
Despite an instinct to build the AI engine first, we keep the roadmap's deliberate order: legal foundation → manual MVP → marketing → portal → AI engine + attorney app → scale. **Why:** prove the business and margins manually before building, per the "sell and deliver before you build" strategy. All of it still gets built — just in this order.

## Committed stack (do not re-litigate)
Vite + React + TypeScript · Python + FastAPI (`uv`, Alembic + SQLAlchemy) · PostgreSQL on Cloud SQL · Clerk (org-based auth) · Stripe (hosted checkout) · Google Cloud Storage · Anthropic Claude · Claude for Word add-in (redlines) · Google Cloud Run · Cloudflare · Sentry. **Why:** mirrors the proven General Legal architecture; Python is strongest for the AI/document-heavy core. Source: `charter-law-tech-stack.md`.

---

*Template for new entries:*
*`## YYYY-MM-DD — <short title>`*
*`<What was decided.> **Why:** <reason.>`*
