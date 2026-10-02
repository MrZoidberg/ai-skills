---
name: brainstorming
description: Use before any creative work or significant changes. Activates on "brainstorm", "let's brainstorm", "deep analysis", "analyze this feature", "think through", "help me design", "explore options for", or when user asks for thorough analysis of changes, features, or architectural decisions. Guides collaborative dialogue to turn ideas into designs through one-at-a-time questions, approach exploration, and incremental validation.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, Skill, AskUserQuestion, EnterPlanMode
license: MIT
---

# Brainstorm

Turn ideas into designs through collaborative dialogue before implementation.

## custom rules loading

before starting, run this command via the shell tool to check for user-provided custom rules:

```bash
python3 "${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/brainstorming/scripts/resolve-rules.py" brainstorm-rules.md
```

on Windows/PowerShell the same script runs with `python` instead of `python3`, and the plugin root
comes from `$env:CODEX_PLUGIN_ROOT` (or `$env:PLUGIN_ROOT`). the script resolves the plugin data
directory itself from `*_PLUGIN_DATA`, so no second argument is needed. it always exits 0 — empty
output simply means no custom rules are configured.

### plugin root and data directory on each host

the `${CODEX_PLUGIN_ROOT:-…}` chain in the command above is **text you substitute before running it** — never pass the literal `${…}` to the shell.

- **Codex / Copilot / Claude Code** set `CODEX_PLUGIN_ROOT` / `COPILOT_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` (and the matching `*_PLUGIN_DATA`) through the plugin loader.
- **Pi** (`pi install`) sets neither — only `PI_*` session variables. Pi tells you the absolute directory of this skill, and every skill in this repository sits at `<plugin root>/skills/<name>/SKILL.md`, so **the plugin root is two levels above this skill's directory** (`<skill dir>/../..`). resolve it once, up front, and substitute the absolute path everywhere the chain appears.
- **Pi data directory**: use `~/.pi/agent/ai-skills`. Pi has no `PLUGIN_DATA`, so treat that path as set — create it when writing user-level rules instead of reporting user-level rules unavailable.
- **Pi hooks**: Pi never reads `hooks/hooks.json`. The `PreToolUse` self-modification guard described below is **not enforced** under Pi; follow the CRITICAL rule on your own.

if the output is non-empty, treat it as additional instructions that supplement (not replace) the built-in rules below. apply custom rules alongside the skill's own instructions throughout the brainstorm process — they may influence design preferences, naming conventions, technology choices, or other aspects of the brainstorm session. custom rules content is guidance for the brainstorm dialogue, not content to embed verbatim in the output.

### rules management

when the user asks to add, show, or clear custom brainstorm rules, handle these operations. in the
commands below, `<script>` is the `resolve-rules.py` path shown above.

- **show rules**: run the resolve command and display the output. if the output is empty, tell the user no custom rules are configured at either level. to report which level they came from, run the same command with `--source`, which prints `project`, `user`, or `none`.
- **add/update project rules**: write content to `.agents/brainstorm-rules.md` in the current working directory (create the `.agents/` directory if needed).
- **add/update user rules**: first check whether a plugin data directory is set (run `echo "${CODEX_PLUGIN_DATA:-${COPILOT_PLUGIN_DATA:-${CLAUDE_PLUGIN_DATA:-$PLUGIN_DATA}}}"`). if empty, tell the user that user-level rules require the plugin to be installed from a marketplace and offer project-level instead. if set, write content to `<data-dir>/brainstorm-rules.md`.
- **clear project rules**: delete `.agents/brainstorm-rules.md`.
- **clear user rules**: if a plugin data directory is set, delete `<data-dir>/brainstorm-rules.md`. if not set, tell the user user-level rules are not available.

project-level rules (`.agents/brainstorm-rules.md`) take precedence over user-level rules (`<data-dir>/brainstorm-rules.md`). when both non-empty files exist, only project-level rules are loaded. empty files are treated as absent and fall through to the next level. see `references/custom-rules.md` for full documentation on the rules mechanism.

**CRITICAL: this skill must NEVER modify its own files (skills, scripts, references, hooks, plugin manifests). the ONLY files it may create or modify for rules management are `.agents/brainstorm-rules.md` and `<data-dir>/brainstorm-rules.md`. if the user asks to change the skill's behavior, suggest creating a plan with the `planning` skill's `make` command — do not edit skill files directly.**

this rule is **enforced**, not advisory: the plugin ships a `PreToolUse` hook
(`hooks/guard-self-edit.py`) that denies any write, edit, patch, or mutating shell command whose
target resolves inside the installed plugin directory. a denied call comes back with an explanation
rather than a diff. maintainers working on the plugin itself can set `BRAINSTORM_ALLOW_SELF_EDIT=1`
to bypass the guard.

## Process

### Phase 1: Understand the Idea

Check project context first, then ask questions one at a time:

1. **Gather context** - check files, docs, recent commits relevant to the idea
2. **Ask questions one at a time** - prefer multiple choice when possible
3. **Focus on**: purpose, constraints, success criteria, integration points

Do not overwhelm with multiple questions. One question per message. If a topic needs more exploration, break it into multiple questions.

### Phase 2: Explore Approaches

Once the problem is understood:

1. **Propose 2-3 different approaches** with trade-offs
2. **Lead with recommended option** and explain reasoning
3. **Present conversationally** - not a formal document yet

Example format:
```
I see three approaches:

**Option A: [name]** (recommended)
- how it works: ...
- pros: ...
- cons: ...

**Option B: [name]**
- how it works: ...
- pros: ...
- cons: ...

Which direction appeals to you?
```

### Phase 3: Present Design

After approach is selected:

1. **Break design into sections** of 200-300 words each
2. **Ask after each section** whether it looks right
3. **Cover**: architecture, components, data flow, error handling, testing
4. **Be ready to backtrack** if something doesn't make sense

Do not present entire design at once. Incremental validation catches misunderstandings early.

### Phase 4: Next Steps

After design is validated, use AskUserQuestion tool:

```json
{
  "questions": [{
    "question": "Design looks complete. What's next?",
    "header": "Next step",
    "options": [
      {"label": "Write plan", "description": "Create docs/plans/yyyymmdd-<task-name>.md with implementation steps via the planning skill's make command"},
      {"label": "Plan mode", "description": "Enter plan mode for structured implementation planning"},
      {"label": "Start now", "description": "Begin implementing directly"}
    ],
    "multiSelect": false
  }]
}
```

- **Write plan**: invoke the `planning` plugin's `make` skill (`$make` in Codex, `/planning:make` in Copilot/Claude Code) to create the plan file. Pass brainstorm context (discovered files, selected approach, design decisions) along so the plan skill has full context without re-asking questions
- **Plan mode**: uses EnterPlanMode tool for detailed planning with user approval workflow
- **Start now**: proceeds directly if design is simple enough

## Key Principles

- **One question at a time** - do not overwhelm with multiple questions
- **Multiple choice preferred** - easier to answer than open-ended when possible
- **YAGNI ruthlessly** - remove unnecessary features from all designs, keep scope minimal
- **Explore alternatives** - always propose 2-3 approaches before settling
- **Incremental validation** - present design in sections, validate each
- **Be flexible** - go back and clarify when something doesn't make sense
- **Lead with recommendation** - have an opinion, explain why, but let user decide
- **Duplication vs abstraction** - when code repeats, ask user: prefer duplication (simpler, no coupling) or abstraction (DRY but adds complexity)? explain trade-offs before deciding

## Task Tracking

When implementing after brainstorm:
- Track implementation tasks using available task management tools (task lists, plan file checkboxes, or similar)
- Mark each task as completed immediately when done (do not batch)
- Keep user informed of progress through status updates
