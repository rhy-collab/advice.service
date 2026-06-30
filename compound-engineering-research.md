# Compound Engineering — Research Brief for Charter Law

*Prepared 30 June 2026. Plain-English synthesis of three deep research streams: the compound-engineering method, the best installable skills/plugins, and how power users actually run Claude Code. Sources are listed at the end.*

---

## 1. What "compound engineering" actually is

The term was coined by **Kieran Klaassen** and **Dan Shipper** at Every (every.to), who built a full AI email product (Cora) largely solo using Claude Code.

The idea in one sentence: **instead of using AI to build one thing and starting from scratch on the next, you build a system that gets smarter every time you use it.** Each task teaches the AI a lasting lesson, so future work gets faster, safer, and better — your effort compounds like interest.

Their definition:

> "Building self-improving development systems where each iteration makes the next one faster, safer, and better."

The contrast they draw:

> "AI engineering makes you faster today. Compounding engineering makes you faster tomorrow, and each day after."

**The honest caveat:** independent experts (e.g. Will Larson) point out this is mostly *well-known good engineering practice made automatic by AI*, not magic. The payoff is real, but only if you commit to the unglamorous parts — planning before building, and capturing lessons after. Skip those and you just have ordinary AI coding with extra ceremony.

---

## 2. The core loop: Plan → Work → Review → Compound

This is the daily rhythm. The first three steps are normal. The fourth is what makes it "compound."

1. **Plan** — Turn the idea into a detailed written blueprint before any code is written. "Plans are the new code." A non-technical founder can read and approve a plan even if they can't read code — this is your control point.
2. **Work** — The AI implements the approved plan in an isolated copy of the code. You monitor, you don't micromanage.
3. **Review** — Specialised AI agents review the result in parallel (security, bugs, performance, simplicity), flagging issues by priority.
4. **Compound** — Write down what was learned so the AI applies it automatically next time. The self-check is: *"Would the system catch this automatically next time?"*

Two budgeting rules they live by:
- **80/20 per feature** — ~80% of effort on planning and review, ~20% on the actual build.
- **50/50 overall** — half your time building features, half improving the system itself. ("An hour spent creating a review agent saves 10 hours of review over the year.")

**The single most important habit:** every time the AI gets something wrong, end your correction with *"update your CLAUDE.md so you don't make that mistake again."* That one file is the AI's permanent memory of how Charter Law's codebase works and what your preferences are.

---

## 3. The "generate 9 issues → smash them → repeat" workflow

This is exactly what you described, and it's a well-established pattern (Harper Reed's workflow, endorsed by Simon Willison; plus Anthropic's own GitHub-native loop). Here's how it actually runs:

**Set up once:**
- A `spec.md` in the repo — the master plan for Charter Law, honed by having the AI ask you one question at a time.
- GitHub as the **system of record**. The AI's chat memory is wiped each session by design; everything durable lives in GitHub issues, the code, and the `CLAUDE.md` file.
- Issue templates that capture **acceptance criteria** — these become the AI's spec when it picks up each issue.

**The repeating loop, per batch:**
1. Generate the next batch of **atomic, granular issues** from the spec (granular issues produce much better results than big vague ones).
2. For each issue: the AI reads it, plans, implements on its own branch, tests its own work, and opens a pull request that says `Closes #N`.
3. Review agents fire automatically on every pull request and flag problems by severity.
4. The AI fixes the flagged issues; the merge is blocked until tests pass and important issues are at zero.
5. **A human approves and merges.** Importantly, the AI structurally *cannot* approve or merge its own work by fiat — there's always a human gate. The issue auto-closes.
6. Repeat with the next batch.

**Key safety point for your peace of mind:** the AI can't ship to your users unilaterally. Tests, branch protection, and a human approval step sit between its work and production.

---

## 4. Top 10 skills & plugins to install

Ranked for someone building a production app who can't review code line-by-line. Almost all install by typing a command in Claude — no coding required.

1. **The Compound Engineering plugin (Every)** — the whole method as a free, ready-made toolkit: 26 agents, 23 workflow commands, 13 skills. Install: `/plugin marketplace add https://github.com/EveryInc/every-marketplace` then `/plugin install compound-engineering`. This is your fastest on-ramp.
2. **code-review (official Anthropic)** — `/code-review` runs 5+ agents on a pull request, scores issues by confidence, posts to GitHub. Your automated senior reviewer.
3. **GitHub MCP connector** — lets Claude read/write your issues, branches and pull requests directly. "The single highest-impact install" for an issue-driven workflow.
4. **feature-dev (official) + a spec-driven workflow** — forces a written, approvable plan before code. Stops "vibe-coding."
5. **skill-creator (official skill)** — interviews you and turns Charter Law's own rules and processes into reusable skills, so your business logic gets applied every time.
6. **security-guidance + security-review (official)** — real-time warnings on risky code and full security reviews. Essential for an app handling contracts and client data.
7. **commit-commands (official)** — `/commit`, `/commit-push-pr` handle the entire git workflow in plain English.
8. **Playwright MCP / webapp-testing skill** — Claude opens your app in a real browser and verifies its own changes before customers see them.
9. **Context7 MCP** — feeds Claude live, version-correct documentation so it doesn't use outdated or hallucinated code.
10. **Document skills (docx / xlsx / pdf / pptx) + product-management plugin** — for the founder-facing work: specs, investor docs, roadmaps, financial models, and tracking in Linear/Notion.

**Starter set if you only do a few:** Compound Engineering plugin, GitHub MCP, code-review, feature-dev, skill-creator, security-guidance.

---

## 5. The handful of habits that give the biggest leverage

From the most-repeated power-user advice (Anthropic's own team plus top practitioners):

- **Verification is the #1 tip.** Give the AI a way to check its own work (tests, a build, a screenshot) and it will iterate until it's right — instead of you being the one who catches every mistake.
- **Plan before coding.** "The expensive failure isn't a bad line of code, it's a wrong direction." Use plan mode; approve the plan; then let it build.
- **Keep CLAUDE.md lean** (under ~200 lines) and prune it — it stops working when bloated.
- **Run several sessions in parallel**, each on its own branch — described by Anthropic's team as "the biggest productivity unlock."
- **Push back on the first answer.** "Don't accept the first solution. Prove to me this works."
- **Make atomic issues.** Small, single-purpose issues with clear acceptance criteria beat big vague ones every time.

---

## Sources

**Compound engineering**
- Klaassen, *My AI Had Already Fixed the Code Before I Saw It* — https://every.to/source-code/my-ai-had-already-fixed-the-code-before-i-saw-it
- Every, *Compound Engineering* guide — https://every.to/guides/compound-engineering
- Will Larson, *Learning from Every's Compound Engineering* — https://lethain.com/everyinc-compound-engineering/
- Compound Engineering plugin — https://github.com/EveryInc/compound-engineering-plugin

**Skills & plugins**
- Official skills repo — https://github.com/anthropics/skills
- Claude Code plugins — https://github.com/anthropics/claude-code/blob/main/plugins/README.md
- Knowledge-work plugins (Cowork) — https://github.com/anthropics/knowledge-work-plugins
- awesome-claude-code — https://github.com/hesreallyhim/awesome-claude-code
- Discover/install plugins — https://code.claude.com/docs/en/discover-plugins

**Power-user workflow**
- Anthropic, Claude Code power-user tips — https://support.claude.com/en/articles/14554000-claude-code-power-user-tips
- Anthropic, best practices — https://code.claude.com/docs/en/best-practices
- Saulius Tautvaisas, GitHub-native issue-to-merge loop — https://saulius.io/blog/claude-code-github-native-agent-issue-to-merge-loop
- Harper Reed, *My LLM codegen workflow* — https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/
- HAMY, 9 parallel review agents — https://hamy.xyz/blog/2026-02_code-reviews-claude-subagents
