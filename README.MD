# AI Skills

This is a personal collection of **agent skills**: small, reusable bundles of instructions (and optional scripts/templates) that an AI coding agent can load when relevant.

This repo is **mostly written for Codex**, but should work in any agent that supports the [agent skills open standard](https://agentskills.io) (e.g. GitHub Copilot, Claude Code, Antigravity).

Learn more:

- Codex skills: <https://developers.openai.com/codex/skills>
- Agent skills open standard: <https://agentskills.io>
- GitHub Copilot agent skills: <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills>
- Claude Code skills: <https://claude.ai/docs/skills>

## Skills

| Skill | Version | Codex | Copilot | Claude Code | Antigravity |
| --- | --- | --- | --- | --- | --- |
| `coding-python` | `2.0` | Yes | Yes (installer) | Yes (installer) | N/A |

---

## Skill: `coding-python`

Practical Python project setup + everyday development tasks.

Use it for:

- Bootstrapping a new `pyproject.toml`-based Python project.
- Day-to-day tasks in an existing repo (tests, formatting/linting, adding deps, basic type-checking).

Folder: `coding-python/`

### What's included

#### Commands (Slash Commands)

N/A

#### Agents

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

or put `coding-python` to `.copilot/skills/`

## References

- [Copilot Plugins installation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing)

---

## License

MIT (see `LICENSE`).
