# Planning Plugin

Turn a design into a task-by-task implementation plan, review it, then execute it — for
non-trivial, multi-file work. Not the default reach for a one-line fix, an obvious rename, or a
single well-understood edit; for those, just make the change directly (the skill itself asks
before running its full workflow if the ask looks small — see "Adaptive review sizing" below).

Use it for:

- Turning an approved design (e.g. from the `brainstorming` plugin) into a concrete,
  file-by-file implementation plan with checkboxed tasks.
- Reviewing a plan interactively (via Plannotator, if installed) or with an automated reviewer
  subagent before any code is written.
- Autonomously executing an approved plan: branch/worktree setup, one subagent per task, a review
  cascade sized to the plan, and a finalize/rebase step.

Folder: `planning/`

## What's included

### Commands (Slash Commands — Claude Code / Copilot CLI only)

| Command | Description |
|---------|--------------|
| `make` | Interactive plan authoring: gathers context and requirements one question at a time, proposes 2-3 approaches, writes `docs/plans/yyyymmdd-<task-name>.md`, then offers to review and/or execute it. |

### Skills

| Skill | Description |
|-------|-------------|
| `make` | Same interactive plan authoring as the `make` command above, packaged as a skill so Codex CLI (which only loads `skills/`, not `commands/`) can invoke it as `$make`. |
| `exec` | Autonomous execution of an approved plan file: branch or worktree isolation, a per-task subagent loop, an adaptive review cascade, opt-in external adversarial review, and a finalize (rebase/squash) step. |

### Bundled Resources

- `agents/plan-review.md` — read-only subagent persona that reviews a plan document for
  correctness, scope, over-engineering, and testing coverage before execution starts.
- `references/usage.md`, `references/custom-rules.md` — triggers, workflow steps, and the custom
  rules mechanism.
- `scripts/resolve-rules.py` — resolves the active rules file. Pure stdlib Python, runs on macOS,
  Linux and Windows.
- `scripts/plan-annotate.py` — fallback interactive plan-annotation tool, used when Plannotator
  isn't installed.
- `scripts/plan-review-hook.py` + `hooks/hooks.json` — the plan-review hook (see "Plannotator
  integration" below) and the `PreToolUse` self-modification guard (see below).
- `skills/exec/scripts/` — branch/worktree, VCS detection, progress-file, and review-fixer
  helpers used by `exec`.
- `skills/exec/references/agents/*.txt` — short checklists (quality, testing, simplification,
  smells, documentation, implementation) used as review-subagent prompts.
- `skills/exec/references/prompts/*.md` — prompt templates for the per-task, fixer, finalizer,
  and stats subagents.

## How to use it

```
$make                                               # Codex CLI — author a plan
$exec docs/plans/20260101-example.md                # Codex CLI — execute an approved plan
/planning:make                                      # Copilot CLI / Claude Code
/planning:exec docs/plans/20260101-example.md       # Copilot CLI / Claude Code
```

Codex CLI's skill prefix is the skill's own name (from its `SKILL.md` `name:` field), not the
plugin name — there is no `$planning <subcommand>` form. That's why this plugin ships two Codex
skills, `skills/make/` and `skills/exec/`, invoked as `$make` and `$exec` respectively.

It also activates on intent — phrases like *"write a plan for..."*, *"turn this design into
tasks"*, or *"execute this plan"*.

What happens next (`make`):

1. **Triage** — if the ask reads as small and well-understood, it asks whether you actually want
   a full plan or just want the change made directly.
2. **Gather** — one question at a time: goal, scope, constraints, testing preference, title.
3. **Approaches** — proposes 2-3 approaches, leading with a recommendation, before writing anything.
4. **Write** — creates the plan file with a fixed template (overview, approach, tasks with
   file-level detail and checkboxes).
5. **Next step** — review it (Plannotator or the fallback annotator, or an automated reviewer
   subagent), hand it to `exec`, or just commit the plan and stop.

## Custom rules

Two levels, checked in order, **first-found-wins (never merged)**:

| Level | Path |
|-------|------|
| Project | `.agents/planning-rules.md` in the repo you are working in |
| User | `<plugin-data-dir>/planning-rules.md`, set by the agent when installed from a marketplace |

`.agents/` is the directory both Codex CLI and Copilot CLI already scan for skills, so project
rules travel with the repo and work in either agent. An empty file counts as absent and falls
through to the next level.

Example `.agents/planning-rules.md`:

```markdown
## plan structure
- keep tasks small enough to review independently
- always include a rollback/revert note for schema changes

## review preferences
- default to the simplified review route for anything under 6 tasks
- never run external review without asking first
```

You can write the file yourself, or just ask the skill:

- *"show my planning rules"* — prints them and says which level they came from
- *"add a project planning rule: always include a migration task for schema changes"*
- *"clear my project planning rules"*

To check what is active from a terminal:

```bash
# macOS / Linux
python3 scripts/resolve-rules.py planning-rules.md
python3 scripts/resolve-rules.py planning-rules.md --source   # project | user | none
```

```powershell
# Windows
python scripts\resolve-rules.py planning-rules.md
```

## Self-modification guard

Same enforced-immutability approach as the `brainstorming` plugin: `hooks/hooks.json` registers a
`PreToolUse` hook that runs `hooks/guard-self-edit.py` before every write-capable tool call, and
denies the call when its target resolves inside the installed plugin directory. It covers
`Write`/`Edit`/`MultiEdit`/`NotebookEdit`/`create`/`str_replace_editor`, `apply_patch` diffs, and
shell commands that both name the plugin directory and contain a mutating construct.

Reads, greps and globs over the plugin's own files are always allowed — only writes are blocked.
`.agents/planning-rules.md` and `<plugin-data-dir>/planning-rules.md` are explicitly allowed, since
rules management is the one thing the skill is supposed to write.

A blocked call comes back to the agent as:

```
Blocked by the planning plugin's self-modification guard: <path>
This skill must never modify its own files (SKILL.md, scripts, references, hooks, plugin
manifests). Custom behaviour belongs in a rules file at .agents/planning-rules.md instead.
To change the skill itself, propose a plan with the planning skill's make command, or re-run with
PLANNING_ALLOW_SELF_EDIT=1 for deliberate maintenance.
```

**Escape hatch.** If you are actually maintaining the plugin, set `PLANNING_ALLOW_SELF_EDIT=1` in
the environment and the guard stands down for that session.

Implementation notes (same as `brainstorming`'s guard): denial is signaled with **exit code 2 +
stderr**, not a JSON decision payload, since Codex and Copilot's deny JSON shapes differ but both
honour exit 2; and the guard exits **0 on any internal error** so a crashing guard never blocks
every tool call in the session (Copilot treats a non-zero, non-2 `preToolUse` exit as a deny).

## Plannotator integration

Interactive plan review (and, separately, diff review during `exec`) defers to
[Plannotator](https://github.com/backnotprop/plannotator) when it's installed, instead of the
upstream `revdiff` TUI:

- **Detection**: `command -v plannotator` (or `shutil.which("plannotator")` from the hook/scripts).
- **If installed**: Plannotator registers its own review hook/skills per its installer
  (`/plannotator-annotate`, `/plannotator-review`, or the `$plannotator-*` Codex skill prefix), so
  this plugin steps aside and lets Plannotator own the interactive UI rather than risk a double
  prompt. `make`'s "Interactive review" option tells you to run `/plannotator-annotate <plan-file>`
  (or `$plannotator-annotate` on Codex) directly.
- **If not installed**: falls back to the bundled `scripts/plan-annotate.py` (`$EDITOR`-based
  annotation), unchanged from before.
- Set `PLANNING_DISABLE_PLANNOTATOR=1` to skip the Plannotator handoff entirely (e.g. for headless
  or remote-control sessions) and always use the fallback.

## Adaptive review sizing

`exec`'s review cascade scales to the plan, but never switches silently — it recommends a route
and asks you to confirm before starting:

- **Small plans** (`plan_size_threshold` tasks or fewer, default 4): a single sequential review
  pass covering quality, testing, and simplification together.
- **Larger plans**: the full cascade — parallel specialist review subagents, a critical re-check
  loop, and a smells pass.
- **External adversarial review** (an external tool, `codex` by default, reviewing the diff) is
  **never** automatic in either tier — both `make`'s "Auto review" option and `exec`'s review phase
  ask first, defaulting to no.

## Attribution

This plugin is a fork of the `planning` skill from Umputun's `cc-thingz` repository:

- https://github.com/umputun/cc-thingz

Upstream is MIT licensed. This fork adds Codex CLI support, the cross-platform Python scripts,
the self-modification guard hook, the Plannotator integration, and adaptive review sizing.

## Installation

### OpenAI Codex

Add the marketplace using Codex CLI:

```bash
codex plugin marketplace add MrZoidberg/ai-skills
codex plugin install planning@zoid-ai-skills
```

Or install just the skill with the universal skill installer (note: this installs the `exec`
skill only, without the plan-review hook or the self-modification guard, which ship at the plugin
level):

```bash
npx skills-installer install @MrZoidberg/ai-skills/planning/skills/exec --client codex
```

### GitHub Copilot

Add the marketplace from an interactive Copilot session:

```
/plugin marketplace add MrZoidberg/ai-skills
/plugin install planning@zoid-ai-skills
```

### Requirements

Python 3 must be on `PATH` (`python3` on macOS/Linux, `python` on Windows) for the rules resolver,
the plan-annotate fallback, and the guard hook. If it is missing, all three fail open: rules
simply do not load, annotation falls back further to plain manual editing, and the guard does not
block anything.

[Plannotator](https://github.com/backnotprop/plannotator) is optional; without it, plan and code
review use the bundled fallback tooling instead.

## License

MIT (see `LICENSE`).
