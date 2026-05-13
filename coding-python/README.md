# Python Coding Plugin

Practical Python project setup, modern tooling, and everyday development tasks.

Use it for:

- Bootstrapping a new `pyproject.toml`-based Python project with `uv`, `ruff`, `ty`, and `pytest`.
- Day-to-day tasks in an existing repo: tests, formatting/linting, adding deps, basic type-checking, builds.
- Writing PEP 723 standalone scripts.
- Migrating legacy Python tooling when explicitly requested.

Folder: `coding-python/`

## What's included

### Commands (Slash Commands)

N/A

### Agents

| Agent | Description |
|-------|-------------|
| `coding-python` | A general-purpose coding agent for Python projects. Can scaffold a new project, assist with everyday development tasks, create PEP 723 scripts, or migrate legacy tooling when requested. It's triggered automatically when relevant. |

### Bundled Resources

- `references/` contains focused guides for uv, pyproject.toml, ruff, pytest, PEP 723 scripts, migration, and optional hardening.
- `templates/` contains starter `pyproject.toml` and PEP 723 script templates.
- `hooks/` contains future-ready PATH shims that can steer bare `python`, `pip`, `pipx`, and `uv pip` commands toward uv workflows in runtimes that support plugin hooks.

## Attribution

This plugin incorporates ideas and hook patterns from Trail of Bits' `modern-python` plugin:

- https://github.com/trailofbits/skills/tree/main/plugins/modern-python

The upstream Trail of Bits skills repository is licensed under CC-BY-SA-4.0. This repository's own code remains under its stated license.

## Installation

### GitHub Copilot

Add the markplace using Copilot CLI:

```
/plugin marketplace add MrZoidberg/ai-skills
/plugin install coding-python@zoid-ai-skills
```

or put contents of `coding-python` folder to `~/.copilot/skills/`

### OpenAI Codex

OpenAI Codex doesn't have a built-in plugin system, but you can run $skill-installer with each skill URL:

```
$skill-installer install https://github.com/MrZoidberg/ai-skills/tree/master/coding-python/skills/coding-python
```

or use universal installer script:

```bash
curl -fsSL https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.sh | sh -s -- --system copilot --scope system --plugin coding-python -y
```


## License

MIT (see `LICENSE`).
