# Python Coding Plugin

Practical Python project setup + everyday development tasks.

Use it for:

- Bootstrapping a new `pyproject.toml`-based Python project.
- Day-to-day tasks in an existing repo (tests, formatting/linting, adding deps, basic type-checking).

Folder: `coding-python/`

## What's included

### Commands (Slash Commands)

N/A

### Agents

| Agent | Description |
|-------|-------------|
| `coding-python` | A general-purpose coding agent for Python projects. Can scaffold a new project or assist with everyday development tasks in an existing repo. It's triggered automatically when relevant. |

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
