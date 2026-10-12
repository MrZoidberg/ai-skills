# Adopting `brainstorming` for Codex CLI

Summary of the work done to adapt the forked `brainstorming` plugin (originally from
`umputun/cc-thingz`, itself derived from `obra/superpowers`) for Codex CLI, while keeping it
working under GitHub Copilot CLI. Corresponds to commit `334ec0b` (branch
`brainstorming-codex-adoption`, bumped the plugin to v0.2.0).

## Requirements given

1. Target Codex CLI instead of Claude Code, using Codex's own documentation for plugins, skills,
   and hooks — and use Codex features the fork wasn't using yet. Specifically: enforce the skill's
   existing "CRITICAL: never modify its own files" rule via a hook, instead of leaving it as
   unenforced prose.
2. `brainstorming/skills/brainstorming/scripts/resolve-rules.sh` must work on macOS, Linux (fish
   shell), and Windows (PowerShell).
3. Add a `brainstorming/README.md` explaining the skill to a human.

Follow-up requirements during implementation:
- Since the repo already carries dual Codex/Copilot support (`coding-python` as the working
  example), keep both agents working rather than going Codex-only.
- Where the two agents' hook mechanics differ, verify with real research rather than assuming
  parity — this surfaced two load-bearing incompatibilities (below).
- Add a root `TODO.md` recording the dangling `/planning:make` reference and the plan to re-point
  it once a proper planning skill exists, citing its origin.
- Verify the PowerShell hook wrapper actually runs, once `pwsh` was available, rather than leaving
  it syntax-unchecked.
- Commit the result.

## Research that shaped the design

Before writing code, I verified (not assumed) how Codex CLI and Copilot CLI's hook systems compare:

- Both auto-discover `hooks/hooks.json` at the plugin root and accept the PascalCase `PreToolUse`
  event with a compatible snake_case payload (`tool_name`, `tool_input`, `cwd`).
- Their **deny JSON shapes differ**: Codex nests the decision under `hookSpecificOutput`; Copilot
  puts `permissionDecision` at the top level. The one mechanism both honor is **exit code 2 +
  stderr** — so the guard hook uses that, not a JSON payload.
- **Copilot's `preToolUse` is fail-closed**: any non-zero exit other than 2 denies the tool call.
  A hook that crashes would silently block every tool call in the session. This drove the
  guard's blanket `try/except -> exit 0` and the wrapper-level checks for a missing script or
  missing interpreter (discovered because `python3 <missing-file>.py` itself exits 2 — a wrong
  `PLUGIN_ROOT` would otherwise have turned into a session-wide deny).
- Both agents scan `.agents/skills` (project) and `~/.agents/skills` (user) for skills, which is
  why `.agents/` was chosen as the new project-level rules directory over `.codex/` or `.claude/`.
- Per-OS command fields differ (Codex: `commandWindows`; Copilot: `bash`/`powershell`), so the
  hook config sets both plus a POSIX `command` fallback.

## What changed

**Cross-platform rules resolver** — `scripts/resolve-rules.sh` replaced by
`scripts/resolve-rules.py` (Python stdlib only, no dependencies), so the same file runs on macOS,
Linux, and Windows. Resolves the plugin data directory from `CODEX_PLUGIN_DATA` →
`COPILOT_PLUGIN_DATA` → `CLAUDE_PLUGIN_DATA` → `PLUGIN_DATA`, adds a `--source` flag
(project/user/none), and always exits 0.

**Self-modification guard, now enforced** — `hooks/hooks.json` + `hooks/guard-self-edit.py`
register a `PreToolUse` hook that denies any write, edit, patch, or mutating shell command whose
target resolves inside the *installed* plugin directory. Reads/greps/globs are unaffected. The two
legitimate rules files (`.agents/brainstorm-rules.md`, `<plugin-data-dir>/brainstorm-rules.md`) are
allowlisted. `BRAINSTORM_ALLOW_SELF_EDIT=1` bypasses it for deliberate plugin maintenance. Verified
to scope correctly to the `brainstorming` plugin only — it does not touch sibling plugins
(`coding-python`, `writing-plans`) or the repo root.

**Rules path** — moved from `.claude/brainstorm-rules.md` to `.agents/brainstorm-rules.md` (no
`.claude/` fallback), with migration notes in the README and `references/custom-rules.md`.

**`brainstorming/README.md`** (new) — follows the `writing-plans/README.md` skeleton, plus two
sections unique to this plugin: custom rules (paths, precedence, example file, how to ask the
skill to manage them) and the self-modification guard (what it blocks, the deny message, the
escape hatch).

**Also fixed along the way**:
- Renamed the skill from `brainstorm` to `brainstorming` to match its directory and both
  marketplace entries (invocation is now `$brainstorming` in Codex, `/brainstorming` in Copilot).
- Re-pointed every dangling `/planning:make` reference (a namespace from the upstream fork that
  never existed in this repo) at the repo's own `writing-plans` skill, and recorded the origin and
  a proper follow-up in `TODO.md` for when a dedicated planning script lands.
- Fixed the `author` mismatch between `plugin.json` and `.codex-plugin/plugin.json`, and dropped
  the "visual companion for sketching ideas" claim — no such skill exists in the plugin.
- Bumped `0.1.1` → `0.2.0` across both manifests, both marketplace files, and the root README.

## Verification performed

- 41 bats test cases across `resolve-rules.bats` (15) and `guard-self-edit.bats` (26), covering:
  precedence and fallback for the resolver; deny/allow scoping, path resolution (relative,
  symlinked `/tmp` vs `/private/tmp`), shell command detection, `apply_patch` diff parsing,
  camelCase/snake_case payload tolerance, the escape hatch, and fail-open behavior on malformed
  input for the guard.
- All 5 JSON manifests validated with `python3 -m json.tool`.
- The POSIX hook wrapper verified end-to-end (deny, allow, escape hatch, fail-open on a bogus
  `PLUGIN_ROOT`).
- The PowerShell wrapper (`commandWindows` and `powershell` fields) syntax-checked via
  `[System.Management.Automation.Language.Parser]::ParseFile` under pwsh 7.6.6, then
  behavior-tested under both `-File` and `-Command` invocation forms (9 and 4 cases
  respectively) — including confirming the deny reason reaches stderr intact.

## Known gaps

- No end-to-end install/run inside an actual Codex CLI or Copilot CLI session — only local
  simulation of the hook payloads and manifests.
- Codex's documentation doesn't state which interpreter runs `commandWindows` (PowerShell assumed,
  matching Copilot's convention); worth confirming during a real Codex install on Windows.
- `TODO.md` tracks one deliberate loose end: the plan-handoff currently points at `writing-plans`
  as a stopgap and should be re-pointed once a dedicated planning skill/script exists.
