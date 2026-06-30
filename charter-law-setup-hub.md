# Charter Law — Setup Hub 🧭

> Your single home base. Every account, link, and status lives here so that when we build, everything is one glance away. Keep this file updated as you go — it's the first thing to check at the start of any session.
>
> Last updated: 30 June 2026

---

## ⚠️ Read this first — the security rule

**Never type a password, secret key, or API key into this file.** This doc holds *links and statuses only*. All actual passwords and secret keys live in your **password manager** (1Password / Bitwarden). In this doc, when a service has a secret, we just write *"in password manager"* — never the secret itself. This is the one rule that protects the whole business.

---

## Business identity

| Thing | Value |
|-------|-------|
| Business name | Charter Law |
| Domain (web address) | `charterlaw.services` |
| Registrar (where domain is bought) | GoDaddy |
| Business email (Google Workspace) | `info@charterlaw.services` |
| Reviewing attorney | Engaged (per-matter) — _name/contact to add_ |

---

## Accounts — master checklist

Status key: ✅ done · 🟡 in progress · ⬜ not started

| Service | What it does (plain English) | Status | Login URL | Signed in with | Secret stored? |
|---------|------------------------------|--------|-----------|----------------|----------------|
| GoDaddy | Where the domain (web address) is rented | ✅ | godaddy.com | _your GoDaddy login_ | in password manager |
| Google Workspace | Business email + login identity | ✅ | admin.google.com | `info@charterlaw.services` | in password manager |
| GitHub | Stores all the code | ✅ | github.com/Charter-Law | `info@charterlaw.services` | in password manager |
| Password manager | Holds every password/secret safely | ⬜ | — | — | — |
| Claude Code | The tool you build the software with | ⬜ | claude.com | `info@charterlaw.services` | in password manager |
| Cloudflare | Speed + security in front of the site; DNS | ⬜ | dash.cloudflare.com | `info@charterlaw.services` | in password manager |
| Google Cloud | Runs the backend, database, file storage | ⬜ | console.cloud.google.com | `info@charterlaw.services` | in password manager |
| Clerk | Handles customer login/sign-up | ⬜ | dashboard.clerk.com | `info@charterlaw.services` | in password manager |
| Stripe | Takes payments | ⬜ | dashboard.stripe.com | `info@charterlaw.services` | in password manager |
| Sentry | Alerts you when something breaks | ⬜ | sentry.io | `info@charterlaw.services` | in password manager |
| Anthropic API | The AI engine (separate from Claude Code) | ⬜ | console.anthropic.com | `info@charterlaw.services` | in password manager |
| Webflow | The marketing website | ⬜ | webflow.com | `info@charterlaw.services` | in password manager |

**Golden rule for all of these: sign up with `info@charterlaw.services`, not your personal Gmail.** That keeps the business owning everything.

---

## Quick links (the stuff we'll open constantly)

- **GitHub org:** https://github.com/Charter-Law
- **Google Workspace admin:** https://admin.google.com
- **GoDaddy domain dashboard:** https://dcc.godaddy.com
- **Project docs folder:** this "Charter Law" folder on your computer
  - `charter-law-roadmap.md` — the full plan, phase by phase
  - `charter-law-tech-stack.md` — what we're building with and why
  - `charter-law-setup-hub.md` — this file

---

## What's left in Phase 0 (foundation)

In rough order:

1. ⬜ **Password manager** — set this up next, before creating more accounts, so every new login goes straight in.
2. ⬜ **Claude Code** — sign up under the business email; this is your build tool.
3. ⬜ **Cloudflare** — point `charterlaw.services` at it (DNS).
4. ⬜ **Google Cloud** — create the project, turn on billing.
5. ⬜ **Clerk, Stripe, Sentry, Anthropic API** — create accounts, drop keys in the password manager.
6. ⬜ **Webflow** — when we reach the marketing-site phase.

Once these exist, Phase 0 is done and we can start building the "hello world" skeleton.

---

## What I (Claude) need from you to help build

When we sit down to build, the things that actually unblock me are:

1. **This doc kept current** — tick off accounts as you create them. The links matter more than anything.
2. **Tell me when a key exists, not the key itself** — e.g. "the Stripe key is in my password manager." I'll tell you exactly where to paste it (always into a safe `.env` file, never into code).
3. **Screenshots when you're stuck on a screen** — like you've been doing. That's the fastest way for me to see exactly what you see.
4. **The Claude in Chrome extension connected** — so for fiddly setup screens I can click through *with* you instead of just describing it.

You don't need to know any code to give me these. That's the whole point.
