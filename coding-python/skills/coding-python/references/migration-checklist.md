# Migration Checklist

Only migrate tooling when the user asks or when the requested work cannot be completed safely without migration.

## Before Editing

- Inspect `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`, `poetry.lock`, `uv.lock`, `tox.ini`, `noxfile.py`, `.pre-commit-config.yaml`, and CI workflows.
- Identify the import package, supported Python versions, package build backend, and test command.
- Save the current verification command output when practical.

## requirements.txt / pip to uv

1. Run `uv init --bare` if no `pyproject.toml` exists.
2. Add runtime dependencies with `uv add <pkg>`.
3. Add dev dependencies with `uv add --group dev <pkg>`.
4. Run `uv sync --all-groups`.
5. Run tests.
6. Remove `requirements*.txt` only after equivalent dependencies are represented and the user wants the cleanup.

Review lines with `-r`, `-e`, direct URLs, platform markers, and constraints manually.

## Poetry to uv

1. Confirm the user wants this migration.
2. Translate package metadata and dependency groups into `pyproject.toml`.
3. Replace Poetry-only scripts or document their uv equivalents.
4. Generate `uv.lock`.
5. Update CI and docs.
6. Run tests and build.

Do not delete `poetry.lock` until `uv.lock` and CI are working.

## setup.py / setup.cfg to pyproject.toml

1. Preserve metadata: name, version, authors, license, classifiers, entry points.
2. Move dependencies to `[project]`.
3. Pick a build backend. Use `uv_build` for simple new packages; preserve Setuptools/Hatchling/Maturin when project behavior depends on them.
4. Run `uv build`.
5. Run tests.

## black / flake8 / isort to ruff

Read `ruff.md`, then migrate formatting first, lint second. Expect some lints to require code changes; avoid mixing those with unrelated feature work.

## mypy / pyright to ty

Use `ty` for new projects. For existing repos, migrate only when requested. Remove old config after ty is wired into commands and CI.
