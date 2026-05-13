# Testing

Use pytest for new Python tests. Preserve an existing test runner unless changing it is part of the request.

## Commands

```bash
uv run pytest
uv run pytest tests/test_example.py
uv run pytest -k "expression"
uv run pytest --maxfail=1
```

## Coverage

For package/library work, add `pytest-cov` and configure coverage:

```toml
[tool.pytest.ini_options]
addopts = [
  "--strict-config",
  "--strict-markers",
  "--cov=my_package",
  "--cov-report=term-missing",
  "--cov-fail-under=80",
]
testpaths = ["tests"]
```

For small scripts, coverage thresholds may be unnecessary. Prefer targeted tests that cover parsing, error handling, and external boundary behavior.

## Test Structure

Use `tests/` at repo root. Name files `test_*.py`. Keep fixtures local until duplication justifies `conftest.py`.

For code that touches the network, filesystem, subprocesses, time, or environment variables, test both the happy path and a failure path.
