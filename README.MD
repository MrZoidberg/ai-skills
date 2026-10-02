# AI Skills

This is a personal collection of **agent skills**: small, reusable bundles of instructions (and optional scripts/templates) that an AI coding agent can load when relevant.

This repo is **mostly written for Codex**, but should work in any agent that supports the [agent skills open standard](https://agentskills.io) (e.g. GitHub Copilot, Claude Code, Antigravity, Pi).

Learn more:

- Codex skills: <https://developers.openai.com/codex/skills>
- Agent skills open standard: <https://agentskills.io>
- GitHub Copilot agent skills: <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills>
- Claude Code skills: <https://claude.ai/docs/skills>
- Pi coding agent: <https://pi.dev>

## Plugins

| Plugin | Version | Codex | Copilot | Claude Code | Antigravity | Pi |
| --- | --- | --- | --- | --- | --- | --- |
| `coding-python` | `0.2.0` | Yes | Yes (installer) | Yes (installer) | N/A | Yes |
| `brainstorming` | `0.2.0` | Yes | Yes (installer) | Yes (installer) | N/A | Yes (hooks not loaded) |
| `planning` | `0.1.2` | Yes | Yes (installer) | Yes (installer) | N/A | Yes (hooks not loaded) |

Pi installs this repo as a single **Pi package** through the `pi` manifest in the root `package.json`,
which exposes every plugin's `skills/` directory. See [Pi coding agent](#pi-coding-agent) for the
install command and caveats.

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

Structured approach to brainstorming and design. Guides users through clarifying questions, exploring 2-3 approaches with trade-offs, and validating a design incrementally before any code is written.

Use it for:

- Brainstorming solutions to a problem.
- Designing a new feature or system.
- Generating a design doc.

Folder: `brainstorming/` — see [`brainstorming/README.md`](brainstorming/README.md) for full usage.

Supports project-level custom rules in `.agents/brainstorm-rules.md`, and ships a `PreToolUse` hook
that blocks the skill from modifying its own files.

### What's included

#### Commands (Slash Commands)

N/A

#### Skills

| Skill | Description |
|-------|-------------|
| `brainstorming` | A general-purpose brainstorming and design skill. Guides users through clarifying questions, proposing approaches, and writing design docs. It can be triggered automatically when relevant or invoked directly. |

## Plugin: `planning`

Structured implementation planning (`make`) and autonomous plan execution (`exec`).

Use it for:

- Turning an approved design doc, issue, PRD, or concrete requirements into a task-by-task implementation plan.
- Creating test-first task breakdowns with exact files, commands, expected results, and reviewer subagent checks.
- Executing a plan task by task with branch/worktree isolation and an adaptive review cascade.
- Continuing the `brainstorming` workflow after the design has been approved.

Folder: `planning/` — see [`planning/README.md`](planning/README.md) for full usage.

### What's included

#### Commands (Slash Commands)

| Command | Description |
|-------|-------------|
| `make` | Claude Code / Copilot: `/planning:make`. Skill form: `planning/skills/make/SKILL.md`. |

#### Skills

| Skill | Description |
|-------|-------------|
| `make` | Creates detailed, executable implementation plans from approved specs or concrete requirements. It routes back to `brainstorming` when requirements still need discovery or approval. |
| `exec` | Executes a plan file task by task with isolated subagents and a review cascade sized to the plan. |

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

### Pi coding agent

**Option A – Install as a Pi package (recommended):**

```bash
pi install git:github.com/MrZoidberg/ai-skills@master
```

This installs one package that exposes all three plugins' skills (`brainstorming`, `coding-python`,
`make`, `exec`) through the `pi` manifest in the root `package.json`. Pi identifies git packages by
repository URL *without* the ref, so a single root package is the only way to install this repo from
git — the per-plugin `plugin.json` manifests are for the other hosts. Pin a ref (`@v2`, a tag, or a
commit) to freeze the version.

```bash
pi list                      # show configured packages
pi config                    # enable/disable individual skills
pi update --extensions       # reconcile package installations
```

Skills are addressable by name — `/skill:make`, `/skill:exec`, `/skill:coding-python` — and are also
selectable automatically from their descriptions.

**Option B – Universal installer script (skill directories, no package):**

```bash
curl -fsSL https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.sh | sh -s -- --plugin planning --system pi --scope user
```

Pi also reads the shared Agent Skills locations `~/.agents/skills/` (user) and `.agents/skills/`
(project), so the installer symlinks the plugin's skills there. Symlinks resolve through to the
cloned repo, which keeps the plugin-root-relative script paths working.

#### Pi caveats

- **Hooks are not loaded.** Pi has no `plugin.json`/`hooks.json` concept and never reads
  `hooks/hooks.json`, so the `PreToolUse` self-edit guard (`planning`, `brainstorming`) and the
  `SessionStart` shim setup (`coding-python`) do not run under Pi. The guard is stated as an
  instruction inside the skills instead. Pi's equivalent mechanism is a `tool_call` handler in a
  TypeScript extension.
- **No plugin data directory.** Pi sets no `*_PLUGIN_DATA`, so user-level custom rules live in
  `~/.pi/agent/ai-skills/` (`planning-rules.md`, `brainstorm-rules.md`). Project-level rules still
  resolve from `.agents/` in the working directory.
- **`$PLUGIN_ROOT` is skill-relative.** Pi sets only `PI_*` session variables, so the plugin-root
  resolution chain falls through. Each skill's *plugin root and data directory on each host* note
  resolves it as two levels above the skill's own directory.
- **Claude-only tool names.** `planning`'s `make`/`exec` bodies are written against Claude Code tool
  names — `Task` (spawn subagent), `EnterPlanMode`, `EnterWorktree`, `AskUserQuestion`,
  `TaskCreate`/`TaskUpdate`/`TaskList`. Pi's analogues are `subagent` (with worktree isolation),
  `/plan` mode, `ask_user_question`, and `todo`. The agent adapts, but `exec`'s review cascade is the
  least portable part of the repo — expect to intervene there.
- `coding-python` is the fully portable one: instructions and references only, no scripts, no
  plugin-root paths, no Claude-only tools.

## References

- [Copilot CLI plugin installation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing)
- [Copilot CLI plugin creation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-creating)
- [Copilot CLI plugin marketplace creation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace)
- [GitHub Copilot agent skills](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills)
- [Codex plugins installation](https://developers.openai.com/codex/plugins#install-and-use-a-plugin)
- [Pi coding agent](https://pi.dev)

---

## License

MIT (see `LICENSE`).
