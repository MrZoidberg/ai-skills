# AI Skills

This is a personal collection of **agent skills**: small, reusable bundles of instructions (and optional scripts/templates) that an AI coding agent can load when relevant.

This repo is **mostly written for Codex**, but should work in any agent that supports the [agent skills open standard](https://agentskills.io) (e.g. GitHub Copilot, Claude Code, Antigravity).

Learn more:

- Codex skills: <https://developers.openai.com/codex/skills>
- Agent skills open standard: <https://agentskills.io>
- GitHub Copilot agent skills: <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills>
- Claude Code skills: <https://claude.ai/docs/skills>

## Plugins

| Plugin | Version | Codex | Copilot | Claude Code | Antigravity |
| --- | --- | --- | --- | --- | --- |
| `coding-python` | `0.1.0` | Yes | Yes (installer) | Yes (installer) | N/A |
| `brainstorming` | `0.1.0` | Yes | Yes (installer) | Yes (installer) | N/A |

---

## Plugin: `coding-python`

Practical Python project setup + everyday development tasks.

Use it for:

- Bootstrapping a new `pyproject.toml`-based Python project.
- Day-to-day tasks in an existing repo (tests, formatting/linting, adding deps, basic type-checking).

Folder: `coding-python/`

### What's included

#### Commands (Slash Commands)

N/A

#### Skills

| Skill | Description |
|-------|-------------|
| `coding-python` | A general-purpose coding skill for Python projects. Can scaffold a new project or assist with everyday development tasks in an existing repo. It's triggered automatically when relevant. |

## Plugin: `brainstorming`

Structured approach to brainstorming and design. Guides users through clarifying questions, proposing approaches, and writing design docs. Includes a visual companion for sketching ideas.

Use it for:

- Brainstorming solutions to a problem.
- Designing a new feature or system.
- Generating a design doc.

Folder: `brainstorming/`

### What's included

#### Commands (Slash Commands)

N/A

#### Skills

| Skill | Description |
|-------|-------------|
| `brainstorming` | A general-purpose brainstorming and design skill. Guides users through clarifying questions, proposing approaches, and writing design docs. It can be triggered automatically when relevant or invoked directly. |

## Installation

### GitHub Copilot

Add the marketplace using Copilot CLI:

```
/plugin marketplace add MrZoidberg/ai-skills
/plugin install {plugin}@zoid-ai-skills, e.g. /plugin install coding-python@zoid-ai-skills
```

### OpenAI Codex

Install them or use universal installer script:

```bash
npx skills-installer install @MrZoidberg/ai-skills/{plugin}/skills/{skill} --client codex
```

## References

- [Copilot Plugins installation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing)
- [Copilot CLI plugins installation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing)
- [Codex plugins installation](https://developers.openai.com/codex/plugins#install-and-use-a-plugin)

---

## License

MIT (see `LICENSE`).
