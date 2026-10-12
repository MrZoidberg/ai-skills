# Custom Rules for Brainstorm

Custom rules let you inject project-specific or personal conventions into the brainstorm workflow. Rules are free-form markdown loaded at skill invocation time and applied as additional instructions alongside the skill's built-in behavior.

## File Locations

Two levels, checked in order (first-found-wins, never merged):

1. **Project-level**: `.agents/brainstorm-rules.md` in the current working directory
2. **User-level**: `<plugin-data-dir>/brainstorm-rules.md` (per-plugin persistent storage)

`.agents/` is the directory both Codex CLI and Copilot CLI already scan for skills, so project rules
stay portable between the two. The plugin data directory is supplied by the host agent and resolved
from the first of `CODEX_PLUGIN_DATA`, `COPILOT_PLUGIN_DATA`, `CLAUDE_PLUGIN_DATA`, `PLUGIN_DATA`
that is set. It exists only when the plugin was installed from a marketplace.

When both non-empty files exist, only the project-level file is used. Empty or whitespace-only files are treated as absent and fall through to the next level.

## Resolution

The skill runs `scripts/resolve-rules.py` at startup:

```bash
python3 "$PLUGIN_ROOT/skills/brainstorming/scripts/resolve-rules.py" brainstorm-rules.md
```

It is plain Python with no third-party dependencies, so the same file works on macOS, Linux and
Windows — on Windows/PowerShell invoke it with `python` rather than `python3`. An optional second
argument overrides the data directory; `--source` prints `project`, `user`, or `none` instead of the
file contents. The script prints the first file found and always exits 0, so a missing or unreadable
rules file never interrupts a session.

## Managing Rules

Ask the brainstorm skill to manage rules:

- **show rules** — displays current rules and which level they came from
- **add/update project rules** — writes to `.agents/brainstorm-rules.md`
- **add/update user rules** — writes to `<plugin-data-dir>/brainstorm-rules.md`
- **clear project rules** — deletes `.agents/brainstorm-rules.md`
- **clear user rules** — deletes `<plugin-data-dir>/brainstorm-rules.md`

These two files are the only files the skill may write for rules management. Everything inside the
installed plugin directory is off-limits and blocked by the `PreToolUse` guard hook — see
[Self-modification guard](../../../README.md#self-modification-guard).

## Migrating from `.claude/brainstorm-rules.md`

Earlier versions of this skill read `.claude/brainstorm-rules.md`. That path is no longer checked.
Move any existing file:

```bash
mkdir -p .agents && git mv .claude/brainstorm-rules.md .agents/brainstorm-rules.md
```

## Example Content

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

## How Rules Apply

Rules influence design preferences, naming conventions, technology choices, and other aspects of the brainstorm dialogue. They supplement built-in instructions — they never replace them.
