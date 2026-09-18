# Brainstorming Plugin

Turn a rough idea into a validated design before any code gets written.

Use it for:

- Exploring a feature you have not scoped yet — the skill asks one question at a time instead of dumping a questionnaire on you.
- Comparing 2-3 implementation approaches with honest trade-offs before you commit to one.
- Reviewing a design section by section, so a wrong assumption gets caught on page one rather than at the end.
- Handing a validated design straight to the `writing-plans` plugin.

Folder: `brainstorming/`

## What's included

### Commands (Slash Commands)

N/A

### Skills

| Skill | Description |
|-------|-------------|
| `brainstorming` | Collaborative design dialogue in four phases: understand the idea, explore approaches, present the design incrementally, then choose a next step (write a plan, enter plan mode, or start implementing). |

### Bundled Resources

- `skills/brainstorming/references/usage.md` — triggers, the four phases, and worked examples.
- `skills/brainstorming/references/custom-rules.md` — full documentation of the custom rules mechanism.
- `skills/brainstorming/scripts/resolve-rules.py` — resolves the active rules file. Pure stdlib Python, runs on macOS, Linux and Windows.
- `hooks/hooks.json` + `hooks/guard-self-edit.py` — the `PreToolUse` self-modification guard (see below).

## How to use it

Start a session and either name the skill or just describe what you want to think through.

```
$brainstorming                                     # Codex CLI
/brainstorming                                     # Copilot CLI
```

It also activates on intent — phrases like *"let's brainstorm"*, *"help me design"*,
*"explore options for"*, *"think through"*, or any request for a thorough analysis of a change.

What happens next:

1. **Understand** — it reads relevant files and recent commits, then asks questions one at a time, preferring multiple choice. Answer them as they come; it will not batch them.
2. **Explore** — it proposes 2-3 approaches with pros and cons, leading with the one it recommends and explaining why. You pick.
3. **Design** — it presents the design in 200-300 word sections and checks after each one. Say "no, that's wrong" early; backtracking is expected.
4. **Next step** — it asks whether to write a plan (hands off to `writing-plans`), enter plan mode, or start implementing.

Tip: it applies YAGNI aggressively and will push back on scope. If you want the kitchen sink, say so.

## Custom rules

You can feed the skill your own conventions — technology constraints, naming rules, how many
approaches you want — and it will apply them on top of its built-in behaviour for every session.

Two levels, checked in order, **first-found-wins (never merged)**:

| Level | Path |
|-------|------|
| Project | `.agents/brainstorm-rules.md` in the repo you are working in |
| User | `<plugin-data-dir>/brainstorm-rules.md`, set by the agent when installed from a marketplace |

`.agents/` is the directory both Codex CLI and Copilot CLI already scan for skills, so project rules
travel with the repo and work in either agent. An empty file counts as absent and falls through to
the next level.

Example `.agents/brainstorm-rules.md`:

```markdown
## design preferences
- prefer simple solutions over clever abstractions
- always consider backward compatibility
- propose at most 3 approaches

## technology constraints
- backend must be Go with standard library where possible
- frontend uses HTMX, avoid JavaScript frameworks
- database is SQLite via sqlx

## naming conventions
- use camelCase for variables
- use PascalCase for exported types
```

You can write the file yourself, or just ask the skill:

- *"show my brainstorm rules"* — prints them and says which level they came from
- *"add a project brainstorm rule: always propose a migration path"*
- *"add my Go conventions to user-level brainstorm rules"*
- *"clear my project brainstorm rules"*

To check what is active from a terminal:

```bash
# macOS / Linux
python3 skills/brainstorming/scripts/resolve-rules.py brainstorm-rules.md
python3 skills/brainstorming/scripts/resolve-rules.py brainstorm-rules.md --source   # project | user | none
```

```powershell
# Windows
python skills\brainstorming\scripts\resolve-rules.py brainstorm-rules.md
```

> **Migrating:** earlier versions read `.claude/brainstorm-rules.md`. That path is no longer
> checked — run `mkdir -p .agents && git mv .claude/brainstorm-rules.md .agents/brainstorm-rules.md`.

## Self-modification guard

A skill that can rewrite its own instructions is a skill you cannot trust. This plugin therefore
enforces its own immutability rather than just asking nicely in prose.

`hooks/hooks.json` registers a `PreToolUse` hook that runs `hooks/guard-self-edit.py` before every
write-capable tool call. The hook denies the call when its target resolves inside the installed
plugin directory. It covers:

- `Write` / `Edit` / `MultiEdit` / `NotebookEdit` / `create` / `str_replace_editor`
- `apply_patch` and unified diffs, by parsing the file paths out of the patch body
- shell commands (`Bash`, `shell`, `powershell`) that both name the plugin directory *and* contain a mutating construct — redirects, `rm`, `mv`, `cp`, `sed -i`, `Set-Content`, `Remove-Item`, and friends
- mutating shell commands run with the working directory inside the plugin

Reads, greps and globs over the plugin's own files are always allowed — only writes are blocked.
`.agents/brainstorm-rules.md` and `<plugin-data-dir>/brainstorm-rules.md` are explicitly allowed,
since rules management is the one thing the skill is supposed to write.

A blocked call comes back to the agent as:

```
Blocked by the brainstorming plugin's self-modification guard: <path>
This skill must never modify its own files (SKILL.md, scripts, references, hooks, plugin
manifests). Custom behaviour belongs in a rules file at .agents/brainstorm-rules.md instead.
To change the skill itself, propose a plan with the writing-plans skill, or re-run with
BRAINSTORM_ALLOW_SELF_EDIT=1 for deliberate maintenance.
```

**Escape hatch.** If you are actually maintaining the plugin, set `BRAINSTORM_ALLOW_SELF_EDIT=1` in
the environment and the guard stands down for that session.

Two implementation notes, if you are adapting this hook elsewhere:

- It signals denial with **exit code 2 + stderr**, not a JSON decision payload. Codex and Copilot
  both honour exit 2, but their JSON deny shapes differ (Codex nests under `hookSpecificOutput`,
  Copilot uses a top-level `permissionDecision`), so exit 2 is the only portable mechanism.
- It exits **0 on any internal error**. Copilot treats any other non-zero `preToolUse` exit as a
  deny, so a crashing guard would block every tool call in the session. Failing open is the safer
  failure mode here.

## Attribution

This plugin is a fork of the `brainstorming` skill from Umputun's `cc-thingz` repository, itself
derived from Jesse Vincent's `obra/superpowers`:

- https://github.com/umputun/cc-thingz
- https://github.com/obra/superpowers

Both upstream repositories are MIT licensed. This fork adds Codex CLI support, the cross-platform
Python rules resolver, and the self-modification guard hook.

## Installation

### OpenAI Codex

Add the marketplace using Codex CLI:

```bash
codex plugin marketplace add MrZoidberg/ai-skills
codex plugin install brainstorming@zoid-ai-skills
```

Or install just the skill with the universal skill installer (note: this installs the skill only,
without the self-modification guard hook, which ships at the plugin level):

```bash
npx skills-installer install @MrZoidberg/ai-skills/brainstorming/skills/brainstorming --client codex
```

### GitHub Copilot

Add the marketplace from an interactive Copilot session:

```
/plugin marketplace add MrZoidberg/ai-skills
/plugin install brainstorming@zoid-ai-skills
```

### Requirements

Python 3 must be on `PATH` (`python3` on macOS/Linux, `python` on Windows) for the rules resolver
and the guard hook. If it is missing, both fail open: rules simply do not load and the guard does
not block anything.

## License

MIT (see `LICENSE`).
