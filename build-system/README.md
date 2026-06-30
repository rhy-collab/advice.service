# Charter Law — Build System

*This folder holds the files that make the compound-engineering, issue-driven build loop work. When you create the code repository under the `Charter-Law` GitHub org, copy the contents of this folder into the **root of that repo**. Until then they live here, ready to go.*

---

## What's in here and where it goes

| File | Drops into | What it does |
|------|------------|--------------|
| `CLAUDE.md` | repo root | The AI's always-on standing instructions — read at the start of every Claude Code session. The single most important file. |
| `DECISIONS.md` | repo root | A running log of decisions made, so you and the AI stay oriented across sessions. |
| `.github/ISSUE_TEMPLATE/build-task.md` | repo `.github/ISSUE_TEMPLATE/` | Forces every build issue to state clear acceptance criteria. |
| `.github/ISSUE_TEMPLATE/bug.md` | repo `.github/ISSUE_TEMPLATE/` | Standard bug report shape. |
| `.github/pull_request_template.md` | repo `.github/` | Forces every pull request to link its issue and confirm tests/checks. |
| `tooling-and-plugins.md` | keep in docs | Plain-English guide to the plugins, skills, and connectors to install, in order. |

---

## The loop, in one picture

This is your "generate issues → smash them → repeat" rhythm:

1. **Spec** is already written — `charter-law-super-prompt.md` is the authoritative feature spec; `charter-law-roadmap.md` is the phase order.
2. **Generate a batch of issues** for the current phase — small, atomic, each with acceptance criteria (use the build-task template).
3. **For each issue:** the AI reads it, plans the smallest slice, you approve the plan, it builds on its own branch with tests, opens a pull request that says `Closes #N`.
4. **Review** runs automatically (the code-review plugin / review agents) and flags problems.
5. The AI fixes flagged problems; **you approve and merge.** The issue auto-closes.
6. **Compound:** whenever the AI gets something wrong, you tell it *"update CLAUDE.md so you don't repeat this."* The system gets smarter.
7. Repeat with the next batch.

The golden rule: **GitHub is the memory, not the chat.** Every session starts fresh, so anything that must survive lives in issues, the code, `CLAUDE.md`, or `DECISIONS.md`.

---

## What to do first

1. Set up the **password manager** and finish the Phase 0 accounts (see `charter-law-setup-hub.md`).
2. Install the tooling in `tooling-and-plugins.md`.
3. Create the code repo, copy these files in.
4. Ask me to generate the **first batch of GitHub issues** for whatever phase you're starting.
