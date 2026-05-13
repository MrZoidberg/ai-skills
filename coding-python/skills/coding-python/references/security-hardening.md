# Security Hardening

Apply these tools when the user asks for hardening, when the project is shared, or when dependency and CI risk are in scope.

## Dependency Audit

```bash
uv add --group audit pip-audit
uv run pip-audit
```

Run after dependency changes in production-facing projects.

## Secret Detection

Use the repo's existing secret scanning if present. If adding a new setup, prefer a hook-based scanner and make sure the initial baseline is reviewed instead of blindly accepting all findings.

## GitHub Actions

For repos with GitHub Actions:

- `actionlint` catches workflow syntax and shell issues.
- `zizmor` audits workflow security posture.

Run these in CI or hooks when workflows are important to the project.

## Hooks

Use the repo's existing hook runner when present. For new uv-first projects, `prek` is a fast option:

```bash
uv add --group dev prek
uv run prek install
uv run prek run --all-files
```

Do not add hooks that block common workflows without explaining the replacement command in the error message.
