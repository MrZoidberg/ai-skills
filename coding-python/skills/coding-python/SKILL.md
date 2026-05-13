---
name: coding-python
description: Practical Python project setup, modern uv/ruff/ty/pytest workflows, PEP 723 scripts, and careful migration from pip, Poetry, virtualenv, black, flake8, isort, mypy, or pyright. Use for new Python projects, standalone scripts, dependency changes, tests, linting, type checking, and Python toolchain cleanup.
---

# Python Project Development

Use this skill for practical Python work: scaffold projects, edit existing repos, run tests, add dependencies, create standalone scripts, and migrate tooling when the user asks for that migration.

## When to Use

- Creating a new Python project, package, CLI, library, or script.
- Adding or removing Python dependencies.
- Running or configuring tests, linting, formatting, type checking, builds, and packaging.
- Writing PEP 723 single-file scripts with external dependencies.
- Migrating from `pip`, `virtualenv`, `requirements.txt`, Poetry, flake8, black, isort, mypy, or pyright when requested.

## When NOT to Use

- The user explicitly wants to preserve legacy tooling unchanged.
- Python is incidental to a mostly non-Python task.
- The project must support Python older than 3.11 unless the repo already handles that.
- The user asks for framework-specific behavior better covered by another skill or local project documentation.

## Core Rules

- Match the repo first. Do not turn routine edits into tool migrations.
- Prefer `pyproject.toml` as the source of truth when present.
- Prefer `uv` for new Python environments, dependency management, and command execution.
- Use `uv add` and `uv remove` for dependencies; avoid manually editing dependency arrays unless preserving an existing non-uv workflow.
- Do not manually activate virtual environments. Use `uv run <cmd>` or the repo's existing runner.
- Use dependency groups for dev/test/docs/audit tools, not package extras.
- Keep commands copy/paste-able and reproducible.
- If changing dependencies, update the lockfile consistently.

## Decision Tree

1. Existing repo?
   - Detect the current toolchain from `pyproject.toml`, `uv.lock`, `poetry.lock`, `requirements*.txt`, `tox.ini`, `noxfile.py`, and CI files.
   - Use that toolchain unless the user asked to migrate.
2. Single-file script?
   - Use PEP 723 inline metadata. See `references/pep723-scripts.md`.
3. New multi-file project not intended for packaging?
   - Use `uv init`, `src/` layout when useful, `ruff`, `pytest`, and optional `ty`.
4. New reusable package?
   - Use `uv init --package`, `src/` layout, `uv_build`, tests, linting, type checks, and build verification.
5. Migration requested?
   - Read `references/migration-checklist.md` before removing legacy files.

## Tool Defaults for New Work

| Need | Default | Notes |
| --- | --- | --- |
| Package/env management | `uv` | Replaces routine `pip`, `virtualenv`, `pip-tools`, and many `pipx` uses. |
| Format/lint | `ruff` | Use both `ruff format` and `ruff check`. |
| Type checking | `ty` | Good default for new projects; preserve configured mypy/pyright in existing repos unless migrating. |
| Tests | `pytest` + `pytest-cov` | Add coverage thresholds for package/library work. |
| Hooks | `prek` or existing hook runner | Optional hardening, especially for shared repos. |
| Audit | `pip-audit`, Dependabot | Add when the user asks for hardening or when project risk justifies it. |

## Anti-Patterns

| Avoid | Use Instead |
| --- | --- |
| `pip install <pkg>` for project deps | `uv add <pkg>` |
| `python -m pip install` | `uv add` / `uv remove` |
| `uv pip install` | `uv add`, `uv sync`, or `uv run --with` |
| `source .venv/bin/activate` | `uv run <cmd>` |
| New `requirements.txt` for projects | `pyproject.toml` + `uv.lock` |
| New Poetry setup by default | `uv` unless the user or repo requires Poetry |
| New flake8/black/isort stack | `ruff` |
| New mypy/pyright setup by default | `ty`, unless project constraints say otherwise |
| Dev tools in `[project.optional-dependencies]` | `[dependency-groups]` |
| `[tool.ty] python-version` | `[tool.ty.environment] python-version` |

## Common Commands

### uv

- Sync: `uv sync --all-groups`
- Run: `uv run <cmd>`
- Add dependency: `uv add <pkg>`
- Add dev dependency: `uv add --group dev <pkg>`
- Temporary dependency: `uv run --with <pkg> <cmd>`
- Build: `uv build`
- Tool install: `uv tool install <tool>`
- One-off tool run: `uvx <tool>`

See `references/uv-commands.md` for more examples.

### Tests

- uv: `uv run pytest`
- Coverage: `uv run pytest --cov=<package> --cov-report=term-missing`

See `references/testing.md` before changing test configuration.

### Format and Lint

- Format: `uv run ruff format .`
- Lint: `uv run ruff check .`
- Fix safe lint issues: `uv run ruff check --fix .`

See `references/ruff.md` for configuration guidance.

### Type Checking

- ty: `uv run ty check`
- Existing mypy repo: use the repo command unless migration was requested.
- Existing pyright repo: use the repo command unless migration was requested.

## Bootstrap a New Project

Start from `templates/pyproject.toml` for a conventional `uv` project.

Minimum edits after copying the template:
- Set `[project].name`.
- Replace `REPLACE_WITH_IMPORT_PACKAGE`.
- Add package files under `src/<import_package>/`.
- Add tests under `tests/`.

Install and verify:

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run ty check
```

For complete pyproject guidance, read `references/pyproject.md`.

## Standalone Scripts

Use PEP 723 inline metadata for scripts with dependencies. Start from `templates/pep723_script.py` and run with:

```bash
uv run path/to/script.py
```

For one-off dependencies that should not be written into the script:

```bash
uv run --with rich --with httpx path/to/script.py
```

See `references/pep723-scripts.md`.

## Migration Work

Only migrate when the user asks for it or the requested change cannot be done safely without migration.

Before migration:
- Inventory files and commands.
- Identify package import name and supported Python versions.
- Preserve CI behavior unless the user requested a CI cleanup.
- Make the migration in small, verifiable steps.

Read `references/migration-checklist.md` for the workflow.

## Optional Hardening

For shared repos, production projects, or security-sensitive work, consider:
- `pip-audit` dependency scanning.
- Secret detection.
- GitHub Actions linting and security checks (`actionlint`, `zizmor`).
- Dependabot for dependency updates.

Read `references/security-hardening.md` and `references/dependency-automation.md`.

## Definition of Done

For a typical PR-sized Python change:
1. Tests pass.
2. Formatting and linting pass if configured.
3. Type checks pass if configured or newly added.
4. Dependency files and lockfiles are consistent.
5. New scripts include repeatable execution instructions or PEP 723 metadata.
