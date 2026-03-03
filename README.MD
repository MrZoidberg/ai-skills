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

### Universal installer (recommended)

These installers can install any skill from this repo by prompting you (interactive) or by flags.

They ask for:
- skill name (e.g. `coding-python`)
- agentic system (`codex`, `copilot`, `claude`, `antigravity`)
- scope (`system` / `repo`)

macOS / Linux (bash):

```bash
curl -fsSL https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.sh | sh
```

Windows (PowerShell):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $s = irm https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.ps1; iex $s; Install-AiSkill }"
```

### Install for Codex

System-wide install:

```text
$skill-installer install https://github.com/MrZoidberg/ai-skills/tree/master/coding-python
```

Project-specific install:

```text
$skill-installer install https://github.com/MrZoidberg/ai-skills/tree/master/coding-python .agents/skills
```

### Install for GitHub Copilot

GitHub Copilot agent skills are discovered from either a repository location or a personal location.

**System-wide (personal) install**:

macOS / Linux (bash):

```bash
curl -fsSL https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.sh | sh -s -- --system copilot --scope system --skill coding-python -y
```

Windows (PowerShell):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $s = irm https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.ps1; iex $s; Install-AiSkill -System copilot -Scope system -Skill coding-python -Yes }"
```

**Project install**:

In the target repo:

macOS / Linux (bash, run from repo root):

```bash
curl -fsSL https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.sh | sh -s -- --system copilot --scope repo --skill coding-python -y
```

Windows (PowerShell, run from repo root):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $s = irm https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.ps1; iex $s; Install-AiSkill -System copilot -Scope repo -Skill coding-python -Yes }"
```

Interactive mode (no args):

```bash
curl -fsSL https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.sh | sh
```

Notes:

- The skill directory name should match the `name:` in the skill frontmatter.
- Copilot loads `SKILL.md` and any referenced files inside that folder.

### Install for Claude Code (skills)

Claude Code uses a similar discovery mechanism to Copilot.

**System-wide (personal) install**:

```bash
curl -fsSL https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.sh | sh -s -- --system claude --scope system --skill coding-python -y
```

**Project install**:

In the target repo:

```bash
curl -fsSL https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.sh | sh -s -- --system claude --scope repo --skill coding-python -y
```

Windows equivalents:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $s = irm https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.ps1; iex $s; Install-AiSkill -System claude -Scope system -Skill coding-python -Yes }"
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $s = irm https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.ps1; iex $s; Install-AiSkill -System claude -Scope repo -Skill coding-python -Yes }"
```

### Install for Antigravity

This repo doesn’t ship an Antigravity-specific installer.

If Antigravity supports the agent skills open standard (a directory containing `SKILL.md` plus resources), point it at the `coding-python/` directory or copy it into Antigravity’s configured skills folder.

If it only supports “custom instructions”, you can paste the contents of `coding-python/SKILL.md` into whatever Antigravity uses for per-project instructions.

---

## License

MIT (see `LICENSE`).
