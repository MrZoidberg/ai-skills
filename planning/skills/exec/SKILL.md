---
name: exec
description: >-
  Execute plan tasks sequentially using subagents, with branch/worktree isolation and a
  multi-phase review cascade. Use when user says 'exec', 'execute plan', 'run plan', or wants to
  implement a plan file task by task with isolated subagents. For non-trivial plans (multi-task,
  multi-file) — a single-task plan is usually faster to just implement directly; confirm with the
  user before running the full pipeline on one.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(bash:*), Agent, AskUserQuestion, TaskCreate, TaskUpdate, EnterWorktree
---

# exec

Execute plan file tasks sequentially, each in an isolated subagent.

Before starting: if the plan has only 1 task, this whole pipeline (branch/worktree setup, review
cascade, finalize) may be more overhead than the change needs. Ask the user to confirm they want
the full autonomous pipeline rather than just implementing the change directly — proceed with
whichever they choose. Skip this check for plans with more than 1 task.

## Arguments

- `$ARGUMENTS` — path to plan file (optional; if omitted, ask user to pick from `plans_dir` userConfig directory, default: `docs/plans/`)

## File Resolution

ALWAYS use the resolve script to read prompt and agent files. NEVER construct the override chain manually:
```
python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/resolve-file.py prompts/task.md
python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/resolve-file.py agents/quality.txt
```
The script checks project overrides, user overrides, and bundled defaults automatically.

### Placeholder Substitution

After reading a prompt file, replace ALL placeholders with actual values before passing to a subagent. Subagents run in fresh contexts without plugin env vars.

Always substitute: `PLAN_FILE_PATH`, `PROGRESS_FILE_PATH`, `DEFAULT_BRANCH`, `${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}` (resolve to actual absolute path), `RESOLVE_SCRIPT` (absolute path to `${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/resolve-file.py`), `PLUGIN_DATA_DIR` (resolved `${CODEX_PLUGIN_DATA:-${COPILOT_PLUGIN_DATA:-${CLAUDE_PLUGIN_DATA:-$PLUGIN_DATA}}}` path — passed as second argument to resolve-file.py so it can find user overrides), `USER_RULES` (resolved custom rules content from the rules loading step, or empty string if no rules found), and phase-specific values (`FINDINGS_LIST`, `REVIEW_PHASE`, `DIFF_COMMAND`).

## Custom Rules Loading

Before starting execution, run this command via Bash tool to check for user-provided custom rules:

```bash
python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/scripts/resolve-rules.py planning-rules.md
```

If the output is non-empty, store it as the resolved custom rules content. When substituting `USER_RULES` in task prompts, wrap the content with a label so the subagent understands it: use "ADDITIONAL CUSTOM RULES:\n<content>" as the substitution. If the output is empty, substitute an empty string for `USER_RULES`. See `${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/references/custom-rules.md` for full documentation on the rules mechanism.

## Process

### Step 1. Resolve plan file

If `$ARGUMENTS` contains a file path, use it. Otherwise, list `.md` files in the `plans_dir` userConfig directory (default: `docs/plans/`), excluding `completed/`. If exactly one plan found, use it automatically. If multiple found, ask the user to pick one.

Read the plan file. Count total Task sections (`### Task N:` or `### Iteration N:`) to know the scope.

Determine the default branch: `python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/detect-branch.py`

### Step 2. Ask about worktree isolation

First detect current branch state — run `git branch --show-current` and compare with the default branch detected earlier (from `detect-branch.py`). Two cases:

**Case A — currently on the default branch (master/main/trunk).** Step 4 will create a new feature branch. Ask the user where it should live, with this payload:

```json
{
  "questions": [{
    "question": "Where should the feature branch be created?",
    "header": "Branch location",
    "options": [
      {"label": "Worktree (isolated)", "description": "Create the feature branch in a new isolated git worktree (in a host-managed worktree directory). Main working directory stays on the default branch."},
      {"label": "In-place", "description": "Create the feature branch in this working directory. Main directory switches to the feature branch for the duration of the run."}
    ],
    "multiSelect": false
  }]
}
```

**Case B — currently on a feature branch.** Step 4 will keep using this branch. Ask whether to move it to an isolated worktree or stay here, with this payload:

```json
{
  "questions": [{
    "question": "You're already on a feature branch. Run the plan here, or in an isolated worktree?",
    "header": "Isolation",
    "options": [
      {"label": "Stay here", "description": "Run the plan in this working directory, on the existing feature branch."},
      {"label": "Move to worktree", "description": "Copy this branch into a new isolated git worktree (in a host-managed worktree directory). Main directory stays untouched."}
    ],
    "multiSelect": false
  }]
}
```

In BOTH cases: ask the user **now**, do not generate text first, do not skip, do not assume. Auto mode does NOT exempt this question — the choice affects the user's working directory and the orchestrator cannot decide on their behalf.

**If the user picks "Worktree (isolated)" or "Move to worktree"** — the main working directory MUST NOT be touched at all: no branch is created or checked out there, and no file changes land there. That isolation is the entire point of this mode. Set `worktree_mode = true` and do this:

1. Record the main tree's path and current branch so you can verify it stayed untouched: `main_tree=$(git rev-parse --show-toplevel)` and `main_branch=$(git branch --show-current)`.
2. Derive the feature branch name with NO git side effects: `name=$(python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/create-branch.py --print-name <plan-file-path>)`.
3. Create an isolated git worktree for this work, passing `<name>` as the worktree name. It creates the worktree (location depends on the host's worktree tooling — Claude Code uses `.claude/worktrees/<name>/`) on a new branch `worktree-<name>` forked from the current HEAD and switches the session into it. Capture the worktree's absolute path as `worktree_path`.
4. Drop the `worktree-` prefix so the branch is just `<name>`, operating on the worktree only: `git -C <worktree_path> branch -m <name>`.
5. **This means Step 4 (create-branch.py) is SKIPPED** — the branch already exists inside the worktree. Running create-branch.py here would `git checkout -b` in the main tree and break isolation.
6. **Isolation guard**: verify the main tree is untouched — `git -C "$main_tree" branch --show-current` MUST still equal `main_branch`. If it changed, STOP and report the isolation breach instead of continuing.
7. Every later step (task execution, reviews, finalize, stats, the plan move) runs inside the worktree; use `<name>` wherever a branch name is needed. At completion, report `worktree_path` and `<name>` so the user can review and merge.

**If the user picks "In-place" or "Stay here"** — set `worktree_mode = false` and proceed normally; Step 4 creates the branch in this working directory.

### Step 3. Create task list

ALWAYS start tracking progress against the plan's task list before starting any work. Track one item per plan Task section plus review phases:

For each `### Task N:` section in the plan, track: "Task N: <title>" (details: the checkbox items).

Then add review-phase items to track: "Review phase 1: comprehensive" (5 parallel review agents + fixer), "Review phase 2: code smells" (smells agent + fixer), "Review phase 3: external" (adversarial external review loop, if the user opts in), "Review phase 4: critical only" (2 review agents + fixer), "Finalize" (rebase, clean up commits, verify), "Stats summary" (aggregate token/duration/git stats, best-effort).

Mark each item in-progress when starting and completed when done.

### Step 4. Create branch

**Skip this step entirely when `worktree_mode` is true** — Step 2 already created the branch (`<name>`) inside the isolated worktree, and running this here would `git checkout -b` in the main working tree and break isolation. Carry `<name>` forward as the branch name and go to Step 5.

Otherwise (in-place mode), **MANDATORY**: run the script below. Do NOT create the branch manually — the script strips the date prefix from the plan filename (e.g., `20260329-feature-name.md` → branch `feature-name`).

```
python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/create-branch.py <plan-file-path>
```

The script creates a feature branch if currently on main/master, or stays on the current branch if already on a feature branch. Capture and use the branch name it outputs.

### Step 5. Initialize progress file

Initialize the progress file: `python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/init-progress.py /tmp/progress-<plan-name>.txt <plan-file-path> <branch-name>` (derive `<plan-name>` from the plan file stem, e.g., `fix-issues.md` → `progress-fix-issues`). The script creates the file with a header. Report the full progress file path to the user.

IMPORTANT: Always use `${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/append-progress.py` to write to the progress file after initialization. Never write directly.

### Step 6. Task loop

Repeat until no `[ ]` checkboxes remain in any Task section:

1. **Re-read the plan file** (subagent modifies it each iteration)
2. **Find the first Task section** (`### Task N:` or `### Iteration N:`) that still has `[ ]` checkboxes
3. **If none found** — all tasks complete, go to step 7
4. **Announce the task to the user** — before spawning the subagent, output a visible summary:
   - Task number and title (from the `### Task N:` header)
   - List all `[ ]` checkbox items in that task section
   - Example output:
     ```
     --- Task 1: Fix error handling ---
     - [ ] Handle the error from os.ReadFile
     - [ ] Either log and exit or handle gracefully
     ```
5. **Spawn a subagent** — autonomous permissions (no approval prompts), general-purpose persona, given the task prompt from `prompts/task.md` with all placeholders substituted as described in the Placeholder Substitution section above (including `USER_RULES`)
6. **After subagent returns**, re-read the plan file and check if that task's checkboxes are now `[x]`
   - If yes — task succeeded, continue loop
   - If no — **retry** with a fresh subagent for the same task up to `task_retries` times (userConfig, default: 1). If all retries fail, stop and report failure to user
7. **Report to user**: "Task N completed" (one line). The task subagent logs details to the progress file.

CRITICAL: Spawn exactly ONE task subagent per iteration and WAIT for it to return before starting the next. NEVER batch-spawn multiple task subagents in a single message. Plan tasks are ordered and interdependent — later tasks build on the files earlier tasks create, and every task subagent edits the same plan-file checkboxes and overlapping source files, so running them in parallel corrupts the plan and the working tree. The "launch in a single message for parallel execution" instruction applies ONLY to the review phases (steps 7 and 10), never to this task loop.

CRITICAL: Do NOT stop the loop based on subagent return text. The ONLY condition to stop is: no `[ ]` checkboxes remain in any Task section (`### Task N:` or `### Iteration N:`). Always re-read the plan file to check.

CRITICAL: You are the ORCHESTRATOR. Never read code, debug errors, investigate diagnostics, or fix issues yourself. If a subagent leaves problems (compiler errors, test failures, lint issues), retry with a fresh subagent — pass the error details in the prompt so it can fix them. All code work happens inside subagents, not in the orchestrator.

Maximum iterations safety limit: 50. If reached, stop and report to user.

### Step 6.5. Choose the review route

Before running any review phase, use the task count from Step 1 (or recount `### Task N:` sections) to form a recommendation, but always ask — don't switch silently:

- **≤ `plan_size_threshold` tasks** (userConfig, default 4): recommend the **simplified** route — one sequential review pass combining the quality/testing/simplification checklists into a single subagent prompt, skipping the separate smells/documentation passes and the critical-recheck loop (Steps 7–8 and 10 collapse into one pass; step 9's external review is unaffected by this choice, it's gated separately).
- **> `plan_size_threshold` tasks**: recommend the **full** route — today's cascade (Steps 7, 8, 10 as written: 5 parallel specialist subagents, critical re-check loop, smells pass).

Ask once: "This plan has N tasks — I'd recommend the [simplified/full] review route. Use that, or the other one instead?" Proceed with whichever the user picks. Log the choice to the progress file as `[decision] review route: <simplified/full> — <N tasks, threshold T>` so it isn't re-asked mid-run.

**If simplified was chosen**: replace Steps 7, 8, and 10 with a single pass — resolve `agents/quality.txt`, `agents/testing.txt`, and `agents/simplification.txt`, concatenate them into one subagent prompt (same READ-ONLY preamble and severity-tagging rules as the comprehensive playbook in `prompts/review.md`), spawn one subagent, collect findings, spawn one fixer with the full findings, then proceed straight to Step 9. Skip the code-smells pass and the critical-recheck loop entirely.

**If full was chosen**: run Steps 7, 8, 9, 10 exactly as written below.

### Step 7. Review phase 1 — comprehensive then critical re-check

After all tasks complete, run a comprehensive code review on iteration 1, then narrow to critical-only re-checks on subsequent iterations to verify the fixer's work without re-running the full heavy sweep.

Report to user: "--- Review phase 1: comprehensive ---"

Loop up to `review_iterations` times (userConfig, default: 5). Track the current iteration number:

1. **Read review.md as a playbook (NOT as a subagent prompt)** — resolve `prompts/review.md` through the override chain and read it from this main session. It tells YOU (the orchestrator) which specialist agents to fan out for the current `REVIEW_PHASE`. Substitute `DEFAULT_BRANCH`, `PLAN_FILE_PATH`, `PROGRESS_FILE_PATH`, `${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}`, and `REVIEW_PHASE` in the resolved content. Then follow the playbook FROM THIS SESSION: spawn the specified subagents to run their reviews concurrently, not one after another. Subagents cannot spawn further subagents, so the fanout MUST be initiated from the main orchestrator.
   - **Iteration 1**: set `REVIEW_PHASE` to `comprehensive`. Per the playbook, launch 5 parallel review agents (quality, implementation, testing, simplification, documentation).
   - **Iteration 2 and later**: set `REVIEW_PHASE` to `critical`. Per the playbook, launch 2 parallel review agents (quality, implementation) focused on critical/major issues only. Before this iteration, report to user: "--- Review phase 1: critical re-check (iteration N) ---"

2. **Collect findings** — collect findings from ALL launched review agents. Pass the COMPLETE output (not a summary) to the fixer. Do NOT summarize, filter, or dismiss any findings. ALL findings are actionable. Report to user with a short list of findings. Log to progress file:
   `python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/append-progress.py <progress-file> "review phase 1: findings"`
   Then pipe: `echo "<findings>" | python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/append-progress.py <progress-file>`

3. **If ALL agents reported zero issues** → report "Review phase 1: clean" and proceed to the next phase.

4. **Spawn a fixer agent** — resolve `prompts/fixer.md` through the override chain, autonomous permissions, general-purpose persona. Pass the FULL unedited review output as FINDINGS_LIST — the fixer decides what's real, not you.

5. **After fixer returns** → show the "FIXES:" section to the user. Report "Review phase 1: iteration N fixes applied". Check for uncommitted changes: run `git status --porcelain`. If output is non-empty, show every reported path and warn that these uncommitted changes are absent from the committed branch diff used by the next review. This is report-only: do not retry, abort, or commit leftovers because of this check. Loop back to step 1.

If `review_iterations` reached with issues still found, report "Review phase 1: max iterations reached, moving on" and continue.

### Step 8. Review phase 2 — code smells

Report to user: "--- Review phase 2: code smells analysis ---"

Run once (no loop):

1. **Spawn a smells agent** — resolve `agents/smells.txt` through the override chain, autonomous permissions, general-purpose persona, given the resolved agent prompt.

2. **Collect findings** — after the agent returns, report to user with a compact list of findings (one line per finding). Log findings to progress file:
   `python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/append-progress.py <progress-file> "review phase 2: findings"`
   Then pipe the findings: `echo "<findings>" | python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/append-progress.py <progress-file>`

3. **If no issues found** → report "Smells analysis: clean" and proceed to the next phase.

4. **Spawn a fixer agent** — resolve `prompts/fixer.md` through the override chain, autonomous permissions, general-purpose persona. Pass the FULL smells output as FINDINGS_LIST.

5. **After fixer returns** → report fixes to user. Check for uncommitted changes: run `git status --porcelain`. If output is non-empty, show every reported path and warn that these uncommitted changes are absent from the committed branch diff used by the next review. This is report-only: do not retry, abort, or commit leftovers because of this check. Proceed to the next phase.

### Step 9. Review phase 3 — external review

**Ask first — never automatic**: before doing anything else in this step, ask the user: "Run external review via Codex (or your configured `external_review_cmd`) before finishing? [y/N]" — default to no if they don't answer clearly. If declined, report "External review: skipped by user" and proceed directly to step 10. This step must never run as a fixed pipeline phase without this explicit opt-in, regardless of route chosen in Step 6.5.

Report to user: "--- Review phase 3: external review ---"

Adversarial loop: the external reviewer reviews the code, fixer evaluates and fixes, the reviewer re-reviews. The loop exits early once an iteration produces no `CRITICAL` or `MAJOR` findings — minor-only iterations still get fixed by the fixer, but no further round-trip happens. Subsequent phases (smells, critical-only) act as the final safety net.

All invocations go through `run-external-review.py`, which takes the `external_review_cmd` userConfig value as its first argument and the prompt as its second. An empty first argument makes it fall back to codex. Do NOT call `run-codex.py` directly — it cannot honor `external_review_cmd`. Older `codex-review.md` overrides may carry launcher or availability instructions before `## Prompt`; ignore those operational lines. Step 9 alone controls reviewer invocation and skip/failure handling.

If the script exits 127 AND its stderr carries the `run-external-review:` marker, no external tool is available: report `External review: skipped — <stderr line>`, quoting the reason verbatim (it distinguishes a configured command missing from `PATH` from codex missing with no command set), and proceed to step 10. A 127 without that marker came from the reviewer itself — typically a wrapper script whose own inner tool is missing — and is a reviewer failure, not a skip.

Any other non-zero exit is a reviewer failure too, not a clean review: report `External review: reviewer failed (exit <code>) — <stderr line>` and proceed to step 10. So is an exit 0 that produced no output: report `External review: reviewer failed (no output)`, adding any stderr line the reviewer printed. Never treat empty output as "no findings" — the severity scan in item 4 would find nothing and the phase would report success without a review having run. The tool result merges the reviewer's stdout and stderr, so judge this on the combined text; a reviewer whose only output is progress chatter on stderr, with no findings and no `NO ISSUES FOUND` marker, is a reviewer failure as well.

Loop up to `external_review_iterations` times (userConfig, default: 10):

1. **Resolve the review prompt** — read `prompts/codex-review.md` through the override chain. Replace `DIFF_COMMAND` with `git diff DEFAULT_BRANCH...HEAD` — every iteration uses this. Fixers commit their changes, so later reviews must include the committed branch diff. Also replace `PLAN_FILE_PATH` (so the reviewer can read the plan for intent) and `PROGRESS_FILE_PATH` (so the reviewer can read prior review iterations and fixer responses and avoid re-reporting fixed issues).

2. **Run the external reviewer** — first write the resolved prompt to `/tmp/external-review-<plan-name>.txt` with the Write tool (same `<plan-name>` as the progress file, overwrite it each iteration), then run `python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/run-external-review.py '<external_review_cmd>' "$(cat /tmp/external-review-<plan-name>.txt)"` in the background — do NOT poll or sleep, wait for it to finish. Do NOT paste the prompt text inline: it contains backticks and may contain `$` (the bundled prompt asks for findings formatted as `` `SEVERITY: file:line - description` ``), and the shell would run those as command substitutions before the reviewer saw the prompt. Write the file with the Write tool for that same reason — `echo "…" >` or a heredoc with an unquoted delimiter expands the backticks and `$` at write time, so the file the reviewer reads already has the format instruction blanked out.

   `<external_review_cmd>` is whatever value the host resolved for the `external_review_cmd` preference (on Claude Code, the `userConfig` value; on Codex/Copilot, whatever the user told you in chat, or empty if they never set one). Pass it through verbatim as a single-quoted argument — an empty value makes the script fall back to codex. If a value needs a literal `'`, wrap the command in a script and point the setting at that instead.

3. **Check the output** — the `NO ISSUES FOUND` marker counts as clean only when item 4's severity scan also comes back empty, so run that scan first. Marker present and no `CRITICAL` or `MAJOR` found → phase is done, proceed to step 10. That marker is the only clean result — the contract makes it mandatory — so never infer "clean" from output that lacks it. But the marker alone does not make a review clean either: a reviewer that echoes the phrase while still reporting a blocking finding is treated like any other finding output, and the findings win. Non-empty output without the marker must carry at least one `CRITICAL`, `MAJOR` or `MINOR` tag somewhere in the combined stdout/stderr text — a tag is what makes the output a review rather than a message. Output with neither the marker nor any tag is a reviewer failure: report `External review: reviewer failed (no findings and no clean marker)`, quoting the reviewer's first output line, and proceed to step 10. This is a whole-output check, not a per-line one — do not require every line to be tagged, or wrapped descriptions and blank separators would fail a real review. Output that clears this gate falls through to item 4 for severity classification.

4. **Classify severity** — scan the reviewer output for `CRITICAL` or `MAJOR` markers (case-insensitive whole-word match). Set `has_blocking = true` if either is present, otherwise `has_blocking = false`. Findings without an explicit severity tag are treated as MINOR — `has_blocking` stays false in that case. That default applies to untagged lines sitting alongside at least one tagged line; item 3 has already rejected output carrying no tag at all, so it can never make an untagged non-review read as minor findings.

5. **Report findings to user** — show a compact list (one line per finding).

6. **Spawn a fixer agent** — same as other review phases, with `description: "Fixer - external review"` so the stats phase can group this run under review phase 3. Resolve `prompts/fixer.md`, pass the reviewer output as FINDINGS_LIST. Fixer verifies, fixes, commits, reports FIXES.

7. **Report fixer results to user** - show FIXES section. Log to progress file. Check for uncommitted changes: run `git status --porcelain`. If output is non-empty, show every reported path and warn that these uncommitted changes are absent from the committed branch diff used by the next review. This is report-only: do not retry, abort, or commit leftovers because of this check.

8. **Decide whether to loop**:
   - If `has_blocking` is false → report "External review: only minor findings — fixes applied, stopping loop" and proceed to step 10.
   - Otherwise → loop back to step 1.

If `external_review_iterations` reached with critical/major issues still found, report "External review: max iterations reached, moving on" and continue.

### Step 10. Review phase 4 — critical only

Report to user: "--- Review phase 4: critical/major only (single pass) ---"

Same structure as step 7 but with `REVIEW_PHASE` set to `critical`. Resolve `prompts/review.md` and follow its playbook FROM THIS MAIN SESSION — spawn 2 subagents (quality, implementation) to run concurrently, focusing on critical/major issues only. Subagents cannot spawn further subagents, so the fanout MUST be initiated from the main orchestrator. Same fixer flow — pass findings to fixer, show FIXES to user.

If the simplified route was chosen in Step 6.5, this step was already folded into the single pass — skip it here.

### Step 11. Finalize

Check `finalize_enabled` userConfig (default: true). If false, skip this step.

After all reviews pass, rebase and clean up commits.

Report to user: "--- Finalize: rebase and clean up commits ---"

Spawn a subagent — autonomous permissions, general-purpose persona, given the prompt from `prompts/finalizer.md`. Replace `DEFAULT_BRANCH`, `PLAN_FILE_PATH`, and `PROGRESS_FILE_PATH`.

This is best-effort — if rebase fails, report the issue but don't block completion.

### Step 12. Stats summary

After finalize (or after step 11 was skipped because it's disabled), spawn a subagent — autonomous permissions, general-purpose persona, given the prompt from `prompts/stats.md`. Replace `DEFAULT_BRANCH` and `PROGRESS_FILE_PATH` in the resolved content.

The stats agent reads this session's main log + subagent logs (Claude Code: `~/.claude/projects/<cwd-encoded>/`; other hosts: whatever equivalent session-log location, if any, that host exposes), aggregates per-phase token/duration/tool-use counts, runs `git diff --shortstat DEFAULT_BRANCH...HEAD` for branch churn, and returns a compact markdown report.

Show the stats agent's full markdown output to the user verbatim. Do NOT summarize it further — the agent already produces a tight summary.

This step is best-effort and host-dependent — if the current host has no known session-log format, or the stats agent can't find/parse it, skip the step and note in the completion report that stats weren't available for this host. Never treat this as a failure that blocks completion.

### Step 13. Completion

When stats summary is done (or skipped on failure):
- **Report autonomous decisions and deviations to the user.** The run had no human to answer questions, so subagents decided judgment calls themselves and logged them. Collect every such entry from the progress file — `grep -E '^(\[[^]]*\] )?\[(decision|deviation)\]' <progress-file>` — and present them in a dedicated section titled **"Decisions made autonomously / Deviations from the plan"**, one bullet per entry with its stated reason, so the user learns every question the run answered on its own and why. If there are none, state "no autonomous decisions or deviations were logged." Do this regardless of whether finalize ran — finalize is skipped when disabled, so this is the guaranteed place the user always gets the report.
- Log completion to progress file: `python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/append-progress.py <progress-file> "completed"`
- Move the finished plan into its `completed/` subdirectory and commit it (best-effort): `python3 ${CODEX_PLUGIN_ROOT:-${COPILOT_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-$PLUGIN_ROOT}}}/skills/exec/scripts/move-plan.py <plan-file-path>`. The script is a no-op when the plan is already under `completed/` or missing, derives the target as a `completed/` sibling of the plan's directory (so it respects a custom `plans_dir` and worktrees), and commits the move. Do NOT push. If the script exits non-zero, report the failure but do not block completion.
- Report the final line "All N tasks completed, reviews passed, branch finalized". Append ", plan moved to completed/" ONLY when move-plan.py actually moved the file (it printed `moved plan to ...`); omit the suffix when the move was a no-op (already under `completed/` or missing) or exited non-zero

## Key rules

- Each subagent gets a fresh context — no accumulated state from previous tasks
- Parent session only tracks: task number, success/failure, retry count
- Plan file is the single source of truth for progress — always re-read it
- No signals — just checkboxes in the plan for task progress
- Maintain progress file (`/tmp/progress-<plan-name>.txt`) — see `prompts/progress-file.md` for format and when to write
- Do not modify the plan file yourself during the task, review, and finalize phases — only subagents modify it. The sole exception is the terminal move in step 13 (after all phases finish), which the orchestrator performs via `move-plan.py`
- Do not implement or fix code yourself — only subagents implement and fix
- If a subagent fails or leaves broken code, re-run the loop — do NOT investigate or fix it yourself
- NEVER dismiss findings as "pre-existing", "not from changes", or "architectural" — ALL findings are actionable
- NEVER summarize or filter agent findings — pass the full output to the fixer agent verbatim
- All prompt and agent files MUST be resolved through the three-layer override chain before use
- All `subagent_type` values must be `general-purpose` — agent files provide the specialized prompt
- After reading a prompt file, substitute all placeholders before passing to subagent (see Placeholder Substitution)
- Subagents run with NO human available — they must NEVER ask the user a question or pause for input. They decide judgment calls the plan does not settle from the project's lint rules, CLAUDE.md, and code conventions, and log each as a `[decision]`/`[deviation]` line for the completion report
- In worktree mode (`worktree_mode = true`) the main working directory is never touched — no branch is created or checked out there and no changes land there; all git operations run inside the worktree, and Step 4's create-branch.py is skipped
