---
name: Build task
about: A small, atomic unit of build work for Charter Law
title: "[Phase X] <short, specific title>"
labels: build
assignees: ''
---

## Goal
<One or two sentences: what this issue achieves and why it matters.>

## Context
<Anything the AI needs to know. Link the relevant part of the spec, e.g. `charter-law-super-prompt.md` Part B4, or the roadmap phase.>

## Acceptance criteria (the definition of "done")
- [ ] <Specific, checkable outcome 1>
- [ ] <Specific, checkable outcome 2>
- [ ] <Specific, checkable outcome 3>

## Out of scope
<What this issue deliberately does NOT cover, so it stays small.>

## Verification
<How we'll confirm it works: which test runs, what to click-test on the preview deploy, expected result.>

## Compliance / security check
- [ ] Does not let any AI output reach a customer as legal advice
- [ ] Does not allow a matter to reach `delivered` without recorded attorney approval
- [ ] Keeps all data scoped to the requesting organisation
- [ ] No secrets in code; real client documents kept out of test environments

*(Tick the ones relevant to this issue; delete if none apply.)*
