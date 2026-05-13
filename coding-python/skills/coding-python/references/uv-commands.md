# uv Commands

Use `uv` as the default package, environment, and command runner for new Python work.

## Project Setup

```bash
uv init myproject
uv init --package mypackage
uv sync --all-groups
```

Use `uv init --bare` when adding uv metadata to an existing repo without creating a new package layout.

## Dependencies

```bash
uv add httpx rich
uv add --group dev pytest ruff ty
uv remove httpx
uv sync
uv sync --group dev
uv sync --all-groups
```

Do not use `uv pip install` for project dependencies. Prefer `uv add`, `uv remove`, and `uv sync` so `pyproject.toml` and `uv.lock` stay consistent.

## Running Commands

```bash
uv run python -m package
uv run pytest
uv run ruff check .
uv run ruff format .
uv run ty check
```

Do not activate `.venv` manually for normal agent work. `uv run` gives repeatable command execution without shell-local state.

## One-Off Dependencies

Use `--with` when a dependency is temporary and should not become a project dependency.

```bash
uv run --with rich python -c "from rich import print; print('ok')"
uv run --with httpx --with rich scripts/check_endpoint.py
```

Use `uv add` when code in the project imports the dependency.

## Tools

```bash
uvx ruff --version
uv tool install ruff
uv tool list
uv tool upgrade --all
```

Use `uvx <tool>` for one-off CLI use and `uv tool install <tool>` for tools that should live on the user's PATH.
