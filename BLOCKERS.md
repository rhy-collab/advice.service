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
