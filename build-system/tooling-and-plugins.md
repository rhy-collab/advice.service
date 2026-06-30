# Tooling & Plugins — Install Guide

*Plain-English. These are the skills, plugins, and connectors that make Claude Code dramatically more effective at building Charter Law. Install them in this order. None of this requires you to write code — you type a short command in Claude Code, or click in the Claude app.*

---

## How installing works (30-second version)

There are three kinds of add-on:

- **Skills** — knowledge Claude pulls in automatically when relevant (e.g. how to make a Word doc). Install once.
- **Plugins** — bundles of commands + helper agents + checks. You add a "marketplace" (a source), then install the plugin from it.
- **Connectors (MCP)** — live links to outside tools like GitHub. You log in once to authorise.

In Claude Code you install with a slash command like `/plugin install <name>`. That's it.

---

## Install in this order

### 1. The Compound Engineering plugin *(your fastest on-ramp)*
The whole "plan → build → review → learn" method, ready-made — 26 helper agents, 23 commands, 13 skills.
```
/plugin marketplace add https://github.com/EveryInc/every-marketplace
/plugin install compound-engineering
```
Gives you commands like `/workflows:plan` (research + write a plan before building) and `/workflows:review` (many review agents check the work in parallel).

### 2. The GitHub connector *(the highest-impact single install)*
Lets Claude read and write your issues, branches, and pull requests directly — essential for the issue-driven loop. Connect it from the Connectors section of Claude's settings and log into the `Charter-Law` GitHub account when prompted.

Also install the `gh` command-line tool on your computer and log in — without it Claude hits strict rate limits and stalls. (Ask me and I'll walk you through this when you're ready.)

### 3. code-review *(your automated senior reviewer)*
Runs several review agents on every pull request, scores issues by confidence, and posts feedback to GitHub. This is how a non-technical founder gets code quality they can trust.
```
/plugin install code-review
```

### 4. feature-dev *(stops "vibe-coding into a mess")*
A structured plan-then-build workflow so a written, approvable plan exists before code is written.
```
/plugin install feature-dev
```

### 5. skill-creator *(teach Claude *your* business)*
Interviews you and turns Charter Law's own rules — your contract-review playbook, your conventions — into reusable skills Claude applies automatically.
```
/plugin install skill-creator
```

### 6. security-guidance *(non-negotiable for this business)*
Warns in real time when code touches risky areas, and runs full security reviews. Essential — you handle confidential contracts.
```
/plugin install security-guidance
```

### 7. commit-commands *(git in plain English)*
`/commit`, `/commit-push-pr` — handles the whole save-and-publish-code workflow for you.
```
/plugin install commit-commands
```

---

## Add when you reach that phase

- **Playwright / webapp-testing** — Claude opens your app in a real browser and checks its own work. Add when the customer portal exists (Phase 3).
- **Context7 connector** — feeds Claude up-to-date documentation so it doesn't use outdated code. Add when you start building.
- **Document skills (docx / xlsx / pdf / pptx)** — already available in the Claude app; use them for specs, investor docs, and financial models. No install needed.
- **Sentry connector** — pipes live error alerts to Claude so it can help debug production issues. Add at Phase 4–5.

---

## The starter set (if you only do a few)
Compound Engineering plugin · GitHub connector · code-review · feature-dev · skill-creator · security-guidance. That covers planning, building, reviewing, security, and git — the full production loop.

*Full reasoning and sources are in `compound-engineering-research.md`.*
