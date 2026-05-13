# pyproject.toml

Prefer `pyproject.toml` as the single source of truth for new Python projects.

## New Project Baseline

Start from `templates/pyproject.toml`, then set:

- `[project].name`
- `[project].description`
- `requires-python`
- pytest coverage package name
- `tool.ty.environment.python-version`
- `tool.ruff.target-version`

Use a `src/` layout for reusable packages:

```text
myproject/
  pyproject.toml
  src/myproject/__init__.py
  tests/
```

## Dependency Groups

Use PEP 735 dependency groups for development tooling:

```toml
[dependency-groups]
dev = [
  { include-group = "lint" },
  { include-group = "test" },
  { include-group = "type" },
]
lint = ["ruff"]
test = ["pytest", "pytest-cov"]
type = ["ty"]
```

Do not put dev tools in `[project.optional-dependencies]` unless the package intentionally exposes installable extras to downstream users.

## Build Backend

For new uv-first packages, prefer:

```toml
[build-system]
requires = ["uv_build>=0.8"]
build-backend = "uv_build"
```

Keep an existing backend if the repo already relies on Hatchling, Setuptools, Maturin, PDM, or Poetry-specific behavior.

## Python Version

Default new projects to Python 3.12 when no compatibility requirement is given. Use 3.11+ when broader deployment compatibility matters. Preserve older versions only when the repo or user explicitly requires them.
