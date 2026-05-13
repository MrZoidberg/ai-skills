# Ruff

Use Ruff for both formatting and linting in new projects.

## Commands

```bash
uv run ruff format .
uv run ruff format --check .
uv run ruff check .
uv run ruff check --fix .
```

Run format before lint when both are needed.

## New Project Config

For new projects, a strict-but-practical baseline is:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["ALL"]
ignore = [
  "COM812",
  "D",
  "ISC001",
]
```

`COM812` and `ISC001` conflict with formatter behavior. Ignore `D` unless the project wants docstring enforcement.

## Migration from black, isort, flake8

When migration is requested:

1. Remove black, isort, flake8, pyupgrade, and related plugins from dependency files.
2. Delete or migrate `.flake8`, `[tool.black]`, and `[tool.isort]` config.
3. Add Ruff with `uv add --group lint ruff`.
4. Run `uv run ruff check --fix .`.
5. Run `uv run ruff format .`.
6. Run tests.

Do not perform this migration as part of unrelated feature work.
