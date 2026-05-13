# PEP 723 Scripts

Use PEP 723 inline metadata for standalone scripts that need dependencies.

## Template

Start from `templates/pep723_script.py`:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "httpx>=0.27",
# ]
# ///
```

Run with:

```bash
uv run scripts/example.py
```

`uv` reads the metadata, creates an isolated environment, and runs the script.

## When to Use

- One-off automation.
- Small utilities not worth packaging.
- Reproducible scripts with a short dependency list.

## When Not to Use

- Multi-module applications.
- Reusable libraries.
- Scripts that need extensive test fixtures or packaging metadata.

## Temporary Dependencies

Use `uv run --with` when the dependency should not be written into the script:

```bash
uv run --with rich scripts/example.py
```

If the script imports the dependency permanently, put it in the PEP 723 block.
