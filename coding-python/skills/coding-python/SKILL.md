---
name: coding-python
description: Practical Python project setup + everyday development tasks. Supports existing repo toolchains (uv/poetry/pip) and can scaffold a new pyproject.toml-based project.
---

# Python Project Development

Use this skill for:
- Scaffolding a **new Python project** with `pyproject.toml`.
- **Everyday tasks** in existing Python repos (run tests, add deps, format/lint, type-check, build).

## Principles

- **Match the repo first.** Don’t force migrations as part of routine work.
- Prefer **`pyproject.toml`** as the source of truth when present.
- Keep commands **copy/paste-able** and reproducible.

Then prefer these command patterns:

### uv
- Install/sync: `uv sync` (optionally `--all-groups`)
- Run: `uv run <cmd>`
- Add dep: `uv add <pkg>` (or `uv add --group dev <pkg>`)

## Bootstrap a new project (default: uv + pyproject)

Create a small, conventional layout:
- `src/<import_package>/__init__.py`
- `tests/`
- `pyproject.toml`

Start from the template files in `templates/`:
- `templates/pyproject.toml`

Minimum edits after copying the template:
- Set `[project].name`
- Replace `REPLACE_WITH_IMPORT_PACKAGE` in pytest `--cov=...`

Install (if using uv):
- `uv sync --all-groups`

## Everyday tasks

### Run tests
- uv: `uv run pytest`

### Format + lint (ruff)
- Format: `ruff format .`
- Lint: `ruff check .`

Run them via the repo toolchain:
- uv: `uv run ruff format .` / `uv run ruff check .`

### Add/remove dependencies

Always use the project’s dependency manager:
- uv: `uv add ...` / `uv remove ...`

### Type checking (only if the repo already uses it)

Use what the repo has configured:
- `ty` (replaces `mypy`/`pyright`): `uv run ty`

## 3) Single-file scripts (PEP 723)

For one-off scripts, use the template:
- `templates/pep723_script.py`

Run with uv when available:
- `uv run path/to/script.py`

## Definition of Done (routine change)

Before calling work “done” on a typical PR-sized change:
1. Tests pass.
2. Formatting/linting passes (if configured in the repo).
3. If deps changed, the lockfile (if any) is updated consistently.

For small scripts or changes, ensure at least tests + linting are passing.
