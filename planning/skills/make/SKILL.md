---
name: make
description: >-
  Create a structured implementation plan in docs/plans/. Use when the user says 'make a plan',
  'write a plan for...', 'plan this feature', or asks for a plan for non-trivial work — multi-file
  changes, new features, ambiguous scope, or an explicit "write a plan for..." ask. Not the
  default reach for a one-line fix, an obvious rename, or a single well-understood edit — for
  those, just make the change directly.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, Task, EnterPlanMode, TaskCreate, TaskUpdate, TaskList
---

# Implementation Plan Creation

create an implementation plan in `docs/plans/yyyymmdd-<task-name>.md` with interactive context gathering.

## custom rules loading

before starting, run this command via Bash tool to check for user-provided custom rules:

```bash
python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/scripts/resolve-rules.py planning-rules.md
```

if the output is non-empty, treat it as additional instructions that supplement (not replace) the built-in rules below. apply custom rules alongside the command's own instructions throughout the planning process — they may influence plan structure, testing approach, naming conventions, or other aspects of plan creation. custom rules content is guidance for creating the plan, not content to embed verbatim in the output plan file.

### rules management

when the user asks to add, show, or clear custom planning rules, handle these operations:

- **show rules**: run `python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/scripts/resolve-rules.py planning-rules.md` and display the output. if the output is empty, tell the user no custom rules are configured at either level. otherwise, to determine the source, check if `.agents/planning-rules.md` exists and is non-empty (project-level) — if not, the output came from user-level. tell the user which level it came from.
- **add/update project rules**: write content to `.agents/planning-rules.md` in the current working directory (create the `.agents/` directory if needed).
- **add/update user rules**: first check if `${CODEX_PLUGIN_DATA:-${COPILOT_PLUGIN_DATA:-${CLAUDE_PLUGIN_DATA:-$PLUGIN_DATA}}}` is set (run `echo "${CODEX_PLUGIN_DATA:-${COPILOT_PLUGIN_DATA:-${CLAUDE_PLUGIN_DATA:-$PLUGIN_DATA}}}"`). if empty, tell the user that user-level rules require the plugin to be installed from the marketplace and offer project-level instead. if set, write content to `${CODEX_PLUGIN_DATA:-${COPILOT_PLUGIN_DATA:-${CLAUDE_PLUGIN_DATA:-$PLUGIN_DATA}}}/planning-rules.md`.
- **clear project rules**: delete `.agents/planning-rules.md`.
- **clear user rules**: if `${CODEX_PLUGIN_DATA:-${COPILOT_PLUGIN_DATA:-${CLAUDE_PLUGIN_DATA:-$PLUGIN_DATA}}}` is set, delete `${CODEX_PLUGIN_DATA:-${COPILOT_PLUGIN_DATA:-${CLAUDE_PLUGIN_DATA:-$PLUGIN_DATA}}}/planning-rules.md`. if not set, tell the user user-level rules are not available.

project-level rules (`.agents/planning-rules.md`) take precedence over user-level rules (`${CODEX_PLUGIN_DATA:-${COPILOT_PLUGIN_DATA:-${CLAUDE_PLUGIN_DATA:-$PLUGIN_DATA}}}/planning-rules.md`). when both non-empty files exist, only project-level rules are loaded. empty files are treated as absent and fall through to the next level. see `${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/references/custom-rules.md` for full documentation on the rules mechanism.

**CRITICAL: this skill must NEVER modify its own files (commands, skills, agents, scripts, references, hooks, plugin.json). the ONLY files it may create or modify for rules management are `.agents/planning-rules.md` and `${CODEX_PLUGIN_DATA:-${COPILOT_PLUGIN_DATA:-${CLAUDE_PLUGIN_DATA:-$PLUGIN_DATA}}}/planning-rules.md`. if the user asks to change the skill's behavior, create a plan for it — do not edit skill files directly.**

## step 0: parse intent and gather context

### triage: is a full plan warranted?

before doing anything else, judge whether this request needs the full planning workflow at all. if it reads as small, well-understood, and single-file/obvious (an obvious rename, a one-line fix, a version bump, a config tweak with a clear solution), ask the user one question before proceeding:

> "this looks like a small, well-understood change — do you want a full structured plan, or should i just make the change directly?"

- if they say to just make the change, skip the rest of this workflow entirely and implement the change directly instead.
- if they confirm they want a plan, continue below.

skip this triage question — go straight into the rest of step 0 — when the request is already clearly substantial: multi-file changes, a new feature, ambiguous scope, or the user explicitly asked for a written plan.

before asking questions, understand what the user is working on:

1. **parse user's request** to identify intent:
   - "add feature Z" / "implement W" → feature development
   - "fix bug" / "debug issue" → bug fix plan
   - "refactor X" / "improve Y" → refactoring plan
   - "migrate to Z" / "upgrade W" → migration plan
   - generic request → explore current work

2. **gather relevant context quickly** — use direct tool calls (Read, Glob, Grep), NOT an Explore agent. keep discovery under 30 seconds:

   **for feature development:**
   - glob for files matching the feature area (e.g., `**/*auth*`, `**/*cache*`)
   - read 1-3 most relevant files to understand existing patterns
   - check project structure with a quick `ls` of key directories

   **for bug fixing:**
   - grep for error messages or function names mentioned in the request
   - read the specific file(s) involved
   - check `git log --oneline -5` for recent changes

   **for refactoring/migration:**
   - glob for files matching the area being refactored
   - read 2-3 key files to understand current structure
   - grep for imports/references to identify dependencies

   **for generic/unclear requests:**
   - check `git status` and `git log --oneline -5`
   - read README.md or CLAUDE.md for project overview
   - `ls` the top-level directory structure

   **CRITICAL: do NOT launch an Explore agent or read more than 5 files in this step. the goal is a quick scan, not exhaustive analysis. if more context is needed, ask the user in step 1.**

3. **synthesize findings** into a brief context summary (3-5 bullet points):
   - what the project is and primary language/framework
   - which files/areas are relevant to the request
   - key patterns or conventions observed

## step 1: present context and ask focused questions

show the discovered context, then ask questions **one at a time**:

"based on your request, i found: [context summary]"

**ask questions one at a time (do not overwhelm with multiple questions):**

1. **plan purpose**: ask - "what is the main goal?"
   - provide multiple choice with suggested answer based on discovered intent
   - wait for response before next question

2. **scope**: ask - "which components/files are involved?"
   - provide multiple choice with suggested discovered files/areas
   - wait for response before next question

3. **constraints**: ask - "any specific requirements or limitations?"
   - can be open-ended if constraints vary widely
   - wait for response before next question

4. **testing approach**: ask - "do you prefer TDD or regular approach?"
   - options: "TDD (tests first)" and "Regular (code first, then tests)"
   - store preference for reference during implementation
   - wait for response before next question

5. **plan title**: ask - "short descriptive title?"
   - provide suggested name based on intent

after all questions answered, synthesize responses into plan context.

## step 1.5: explore approaches

once the problem is understood, propose implementation approaches:

1. **propose 2-3 different approaches** with trade-offs for each
2. **lead with recommended option** and explain reasoning
3. **present conversationally** - not a formal document yet

example format:
```
i see three approaches:

**Option A: [name]** (recommended)
- how it works: ...
- pros: ...
- cons: ...

**Option B: [name]**
- how it works: ...
- pros: ...
- cons: ...

which direction appeals to you?
```

ask the user to select their preferred approach before creating the plan.

**skip this step** if:
- the implementation approach is obvious (single clear path)
- user explicitly specified how they want it done
- it's a bug fix with clear solution

## step 2: create plan file

check `docs/plans/` for existing files, then create `docs/plans/yyyymmdd-<task-name>.md` (use current date):

### plan structure

```markdown
# [Plan Title]

## Overview
- clear description of the feature/change being implemented
- problem it solves and key benefits
- how it integrates with existing system

## Context (from discovery)
- files/components involved: [list from step 0]
- related patterns found: [patterns discovered]
- dependencies identified: [dependencies]

## Development Approach
- **testing approach**: [TDD / Regular - from user preference in planning]
- complete each task fully before moving to the next
- make small, focused changes
- **CRITICAL: every task MUST include new/updated tests** for code changes in that task
  - tests are not optional - they are a required part of the checklist
  - write unit tests for new functions/methods
  - write unit tests for modified functions/methods
  - add new test cases for new code paths
  - update existing test cases if behavior changes
  - tests cover both success and error scenarios
- **CRITICAL: all tests must pass before starting next task** - no exceptions
- **CRITICAL: update this plan file when scope changes during implementation**
- run tests after each change
- maintain backward compatibility

## Testing Strategy
- **unit tests**: required for every task (see Development Approach above)
- **e2e tests**: if project has UI-based e2e tests (Playwright, Cypress, etc.):
  - UI changes → add/update e2e tests in same task as UI code
  - backend changes supporting UI → add/update e2e tests in same task
  - treat e2e tests with same rigor as unit tests (must pass before next task)
  - store e2e tests alongside unit tests (or in designated e2e directory)
  - example: if task implements new form field, add e2e test checking form submission

## Progress Tracking
- mark completed items with `[x]` immediately when done
- add newly discovered tasks with ➕ prefix
- document issues/blockers with ⚠️ prefix
- update plan if implementation deviates from original scope
- keep plan in sync with actual work done

## Solution Overview
- high-level approach and architecture chosen
- key design decisions and rationale
- how it fits into the existing system

## Technical Details
- data structures and changes
- parameters and formats
- processing flow

## What Goes Where
- **Implementation Steps** (`[ ]` checkboxes): tasks achievable within this codebase - code changes, tests, documentation updates
- **Post-Completion** (no checkboxes): items requiring external action - manual testing, changes in consuming projects, deployment configs, third-party verifications

## Implementation Steps

<!--
Task structure guidelines:
- Each task = ONE logical unit (one function, one endpoint, one component)
- Use specific descriptive names, not generic "[Core Logic]" or "[Implementation]"
- Each task MUST have a **Files:** block listing files to Create/Modify (before checkboxes)
- Aim for ~5 checkboxes per task (more is OK if logically atomic)
- **CRITICAL: number ALL tasks with concrete sequential integers** - the two trailing tasks below are shown as "Task N-1" and "Task N" where N is a PLACEHOLDER for the total task count, NOT literal text. Substitute real numbers continuing the sequence from your last implementation task (e.g. with 14 implementation tasks they become "Task 15: Verify acceptance criteria" and "Task 16: ... Update documentation"). NEVER write the literal strings "Task N-1" or "Task N" into the plan.
- **CRITICAL: Each task MUST end with writing/updating tests before moving to next**
  - tests are not optional - they are a required deliverable of every task
  - write tests for all NEW code added in this task
  - write tests for all MODIFIED code in this task
  - include both success and error scenarios in tests
  - list tests as SEPARATE checklist items, not bundled with implementation

Example (NOTICE: Files block + tests as separate checklist items):

### Task 1: Add password hashing utility

**Files:**
- Create: `src/auth/hash`
- Create: `src/auth/hash_test`

- [ ] create `src/auth/hash` with HashPassword and VerifyPassword functions
- [ ] implement bcrypt-based hashing with configurable cost
- [ ] write tests for HashPassword (success + error cases)
- [ ] write tests for VerifyPassword (success + error cases)
- [ ] run tests - must pass before task 2

### Task 2: Add user registration endpoint

**Files:**
- Create: `src/api/users`
- Modify: `src/api/router`
- Create: `src/api/users_test`

- [ ] create `POST /api/users` handler in `src/api/users`
- [ ] add input validation (email format, password strength)
- [ ] integrate with password hashing utility
- [ ] write tests for handler success case with table-driven cases
- [ ] write tests for handler error cases (invalid input, missing fields)
- [ ] run tests - must pass before task 3
-->

### Task 1: [specific name - what this task accomplishes]

**Files:**
- Create: `exact/path/to/new_file`
- Modify: `exact/path/to/existing`

- [ ] [specific action with file reference - code implementation]
- [ ] [specific action with file reference - code implementation]
- [ ] write tests for new/changed functionality (success cases)
- [ ] write tests for error/edge cases
- [ ] run tests - must pass before next task

<!-- replace "N-1" and "N" below with the actual next sequential numbers continuing from your last implementation task - do NOT emit the literal letter N -->
### Task N-1: Verify acceptance criteria
- [ ] verify all requirements from Overview are implemented
- [ ] verify edge cases are handled
- [ ] run full test suite: `<project test command>`
- [ ] run e2e tests if project has them: `<project e2e test command>`
- [ ] verify test coverage meets project standard

### Task N: [Final] Update documentation
- [ ] update README.md if needed
- [ ] update CLAUDE.md if new patterns discovered
- [ ] move this plan to `docs/plans/completed/`

## Post-Completion
*Items requiring manual intervention or external systems - no checkboxes, informational only*

**Manual verification** (if applicable):
- manual UI/UX testing scenarios
- performance testing under load
- security review considerations

**External system updates** (if applicable):
- consuming projects that need updates after this library change
- configuration changes in deployment systems
- third-party service integrations to verify
```

## step 3: next steps

after creating the file, count the plan's `### Task N:` sections and tell the user: "created plan: `docs/plans/yyyymmdd-<task-name>.md` (N tasks)". if N is small (≤ `plan_size_threshold`, default 4), add a brief note that it's a small plan and a formal review may be optional — but still offer the full menu below; never decide this for the user.

then ask the user, offering these options:

```json
{
  "questions": [{
    "question": "Plan created. What's next?",
    "header": "Next step",
    "options": [
      {"label": "Interactive review", "description": "Open plan in editor for manual annotation and feedback loop"},
      {"label": "Auto review", "description": "Launch AI plan-review agent for automated analysis"},
      {"label": "Implement", "description": "Commit plan and start implementing"},
      {"label": "Done", "description": "Commit plan, no further action"}
    ],
    "multiSelect": false
  }]
}
```

- **Interactive review**: check if `plannotator` is on PATH (`command -v plannotator`).
  - **if plannotator is available**: tell the user to run `/plannotator-annotate <plan-file-path>` (Claude Code / Copilot CLI slash command) or `$plannotator-annotate <plan-file-path>` (Codex skill-prefix form) themselves. Plannotator opens its own browser review UI and returns structured feedback directly into the conversation — nothing else needs to be launched from here. when the user reports feedback:
    1. read their feedback — it describes what they want changed
    2. revise the plan file to address each point
    3. tell them to run `/plannotator-annotate <plan-file-path>` (or `$plannotator-annotate`) again if they want another pass
    4. repeat until the user says they're done
  - **if plannotator is not available**: fall back to `${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/scripts/plan-annotate.py <plan-file-path>` via Bash.
    the script opens a copy of the plan in $EDITOR via terminal overlay. if the user makes annotations,
    it outputs a unified diff to stdout. when diff output is present:
    1. read the diff carefully — added lines (+) are user annotations, removed lines (-) are deletions, modified lines show requested changes
    2. revise the plan file to address each annotation
    3. run `${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/scripts/plan-annotate.py <plan-file-path>` via Bash
    4. repeat until no diff output (user closed editor without changes)
  when the annotation loop completes, ask again with the remaining options (minus "Interactive review")
- **Auto review**: spawn a subagent running the `plan-review` reviewer persona (`agents/plan-review.md`) — use a named `plan-review` subagent type if the host supports it, otherwise spawn a general-purpose subagent given that file's instructions verbatim. After review completes, ask again with the same options (minus "Auto review")
- **Implement**: commit plan with message like "docs: add <topic> implementation plan", then ask implementation mode:
  ```json
  {
    "questions": [{
      "question": "Implementation mode?",
      "header": "Mode",
      "options": [
        {"label": "Interactive", "description": "Implement task by task in this session"},
        {"label": "Autonomous", "description": "Run the exec skill for autonomous execution with reviews"}
      ],
      "multiSelect": false
    }]
  }
  ```
  - **Interactive**: begin implementing task 1 interactively in this session. Track progress against the plan's task list and mark items completed immediately (do not batch)
  - **Autonomous**: invoke the `exec` skill (`$exec <plan-file-path>` in Codex, `/planning:exec <plan-file-path>` in Copilot/Claude Code) for autonomous execution with multi-phase review. Note for the user: exec will separately ask whether to run external adversarial review (via Codex or a configured tool) and which review-cascade route to use — nothing runs automatically there either
- **Done**: commit plan with message like "docs: add <topic> implementation plan", stop

## execution enforcement

**CRITICAL testing rules during implementation:**

1. **after completing code changes in a task**:
   - STOP before moving to next task
   - add tests for all new functionality
   - update tests for modified functionality
   - run project test command
   - mark completed items with `[x]` in plan file

2. **if tests fail**:
   - fix the failures before proceeding
   - do NOT move to next task with failing tests
   - do NOT skip test writing

3. **only proceed to next task when**:
   - all task items completed and marked `[x]`
   - tests written/updated
   - all tests passing

4. **plan tracking during implementation**:
   - update checkboxes immediately when tasks complete
   - add ➕ prefix for newly discovered tasks
   - add ⚠️ prefix for blockers
   - modify plan if scope changes significantly

5. **on completion**:
   - verify all checkboxes marked
   - run final test suite
   - move plan to `docs/plans/completed/`
   - create directory if needed: `mkdir -p docs/plans/completed`

6. **partial implementation exception**:
   - if a task provides partial implementation where tests cannot pass until a later task:
     - still write the tests as part of this task (required)
     - add TODO comment in test code explaining the dependency
     - mark the test checkbox as completed with note: `[x] write tests ... (fails until Task X)`
     - do NOT skip test writing or defer until later
   - when the dependent task completes, remove the TODO comment and verify tests pass

this ensures each task is solid before building on top of it.

## key principles

- **one question at a time** - do not overwhelm user with multiple questions in a single message
- **multiple choice preferred** - easier to answer than open-ended when possible
- **DRY, YAGNI ruthlessly** - avoid unnecessary duplication and features, keep scope minimal (but prefer duplication over premature abstraction when it reduces coupling)
- **lead with recommendation** - have an opinion, explain why, but let user decide
- **explore alternatives** - always propose 2-3 approaches before settling (unless obvious)
- **duplication vs abstraction** - when code repeats, ask user: prefer duplication (simpler, no coupling) or abstraction (DRY but adds complexity)? explain trade-offs before deciding
