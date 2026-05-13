# Writing Plans Plugin

Create implementation plans from approved specs before code changes begin.

Use it for:

- Turning a design doc, issue, PRD, or concrete requirements into a task-by-task implementation plan.
- Creating test-first task breakdowns with exact files, commands, expected results, and reviewer subagent checks.
- Continuing the `brainstorming` workflow after the design has been approved.

Folder: `writing-plans/`

## What's included

### Commands (Slash Commands)

N/A

### Skills

| Skill | Description |
|-------|-------------|
| `writing-plans` | Creates detailed, executable implementation plans from approved specs or concrete requirements. It routes back to `brainstorming` when requirements still need discovery or approval. |

### Bundled Resources

- `references/plan-document-reviewer-prompt.md` contains the subagent reviewer prompt used to check completed plans before handoff.

## Attribution

This plugin adapts the `writing-plans` skill from Jesse Vincent's `obra/superpowers` repository:

- https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md
- https://github.com/obra/superpowers/blob/main/skills/writing-plans/plan-document-reviewer-prompt.md

The upstream `obra/superpowers` repository is licensed under MIT. This repository's own code remains under its stated license.

## Installation

### GitHub Copilot

Add the marketplace using Copilot CLI:

```
/plugin marketplace add MrZoidberg/ai-skills
/plugin install writing-plans@zoid-ai-skills
```

### OpenAI Codex

Add the marketplace using Codex CLI:

```bash
codex plugin marketplace add MrZoidberg/ai-skills
```

Install the skill directly with the universal skill installer:

```bash
npx skills-installer install @MrZoidberg/ai-skills/writing-plans/skills/writing-plans --client codex
```

## License

MIT (see `LICENSE`).
