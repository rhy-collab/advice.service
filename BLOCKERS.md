# Blockers

## GitHub Branch Protection

**Status:** External / owner settings blocked.

`main` CI is green, but enabling or verifying branch protection through the GitHub API returned:

```text
HTTP 403: Upgrade to GitHub Pro or make this repository public to enable this feature.
```

Owner action required:
- Upgrade/adjust the GitHub plan, or make the repository public if appropriate.
- Enable branch protection on `main`.
- Require the CI workflow to pass.
- Require at least one pull request review before merge.

## Anthropic Production Key

**Status:** External / secret required.

The backend now supports real internal AI preparation when `ANTHROPIC_API_KEY` is set. Production setup still needs:

- Add `ANTHROPIC_API_KEY` to the backend runtime secret store.
- Confirm `ANTHROPIC_MODEL`, currently `claude-sonnet-4-20250514`.
- Keep generated results internal-only until attorney approval.
- Do not log document content or prompts. API use should follow Anthropic's commercial data-use/no-training posture for API traffic.
