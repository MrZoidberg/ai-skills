# Dependency Automation

Use dependency automation for shared or long-lived projects. Keep it conservative by default.

## Dependabot

For GitHub projects, add `.github/dependabot.yml` with package ecosystem entries for:

- `uv` or `pip` for Python dependencies, depending on what GitHub supports for the repo.
- `github-actions` for workflow actions.

Use weekly updates unless the project has a reason for faster cadence.

## Review Guidance

- Require tests for dependency update PRs.
- Watch for major version updates and transitive dependency churn.
- Keep lockfile changes in the same PR as dependency metadata changes.
- Run `uv sync --locked` in CI when lockfile integrity matters.

## Supply Chain Notes

Prefer pinned action versions or trusted major tags for GitHub Actions. For security-sensitive repos, consider pinning actions to full commit SHAs and using automation to refresh them.
