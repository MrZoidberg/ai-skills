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
| `coding-python` | `0.2.0` | Yes | Yes (installer) | Yes (installer) | N/A |
| `brainstorming` | `0.1.1` | Yes | Yes (installer) | Yes (installer) | N/A |
| `writing-plans` | `0.1.0` | Yes | Yes (installer) | Yes (installer) | N/A |

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

## Plugin: `writing-plans`

Create implementation plans from approved specs before code changes begin.

Use it for:

- Turning an approved design doc, issue, PRD, or concrete requirements into a task-by-task implementation plan.
- Creating test-first task breakdowns with exact files, commands, expected results, and reviewer subagent checks.
- Continuing the `brainstorming` workflow after the design has been approved.

Folder: `writing-plans/`

### What's included

#### Commands (Slash Commands)

N/A

#### Skills

| Skill | Description |
|-------|-------------|
| `writing-plans` | Creates detailed, executable implementation plans from approved specs or concrete requirements. It routes back to `brainstorming` when requirements still need discovery or approval. |

## Installation

### GitHub Copilot CLI

**Option A – Install via the plugin marketplace (recommended):**

```bash
# Register the marketplace (one-time)
copilot plugin marketplace add MrZoidberg/ai-skills

# Install a plugin, e.g.:
copilot plugin install coding-python@zoid-ai-skills
```

Or from an interactive Copilot session:

```
/plugin marketplace add MrZoidberg/ai-skills
/plugin install coding-python@zoid-ai-skills
```

**Option B – Install a skill directly with `gh skill`:**

```bash
gh skill install MrZoidberg/ai-skills coding-python
gh skill install MrZoidberg/ai-skills brainstorming
gh skill install MrZoidberg/ai-skills writing-plans
```

**Option C – Universal installer script (macOS/Linux):**

```bash
curl -fsSL https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.sh | sh -s -- --plugin coding-python --system copilot --scope user
```

### OpenAI Codex

Add the marketplace using Codex CLI:

```bash
codex plugin marketplace add MrZoidberg/ai-skills
```

Install them or use universal installer script:

```bash
npx skills-installer install @MrZoidberg/ai-skills/{plugin}/skills/{skill} --client codex
```

## References

- [Copilot CLI plugin installation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing)
- [Copilot CLI plugin creation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-creating)
- [Copilot CLI plugin marketplace creation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace)
- [GitHub Copilot agent skills](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills)
- [Codex plugins installation](https://developers.openai.com/codex/plugins#install-and-use-a-plugin)

---

## License

MIT (see `LICENSE`).
