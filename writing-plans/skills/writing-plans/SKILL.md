---
name: writing-plans
description: Use when you have an approved spec, design doc, or concrete requirements for a multi-step implementation task, before touching code. Do not use for initial ideation; use brainstorming first when requirements still need to be discovered or approved.
---

# Writing Plans

Create detailed implementation plans from approved specs or concrete requirements before code changes begin.

Announce at start: "I'm using the writing-plans skill to create the implementation plan."

## Relationship To Brainstorming

This skill is the implementation-planning handoff from `brainstorming`.

- Use `brainstorming` first when the user is still exploring goals, alternatives, design, UX, architecture, or acceptance criteria.
- Use `writing-plans` after there is an approved design doc, spec, issue, PRD, or sufficiently concrete requirement set.
- If the request still requires product/design decisions, pause planning and route back to `brainstorming`.
- Do not touch code, scaffold files, or start implementation while writing the plan.

## Scope Check

Before defining tasks, verify that the spec is appropriate for one implementation plan.

- If it spans multiple independent subsystems, suggest splitting it into separate specs or plans.
- Each plan should produce working, testable software on its own.
- Preserve explicit user preferences for plan location, sequencing, technologies, and non-goals.

## File Structure

Map the files before decomposing tasks:

- List every file to create, modify, or test.
- State what each file is responsible for.
- Follow existing codebase patterns and local helper APIs.
- Keep boundaries clear and avoid unrelated refactors.
- If a touched file is doing too much, include only the targeted split needed for this work.

This file map locks in the decomposition. Each task should be independently understandable and testable.

## Plan Location

Save plans to:

`docs/plans/YYYY-MM-DD-<feature-name>-implementation.md`

User preferences override this default.

## Task Granularity

Break work into bite-sized steps. Each step should be one action that takes a few minutes:

- Write the failing test.
- Run it and verify the expected failure.
- Implement the smallest code change that should pass.
- Run the focused test and verify it passes.
- Run the relevant broader checks.
- Commit the task when the user asked for commit-ready work or the workflow requires commits.

## Plan Header

Every plan must start with this structure:

```markdown
# [Feature Name] Implementation Plan

**Goal:** [One sentence describing what this builds]

**Spec Source:** [Path or description of the approved spec/requirements]

**Architecture:** [2-3 sentences about the implementation approach]

**Tech Stack:** [Key technologies, libraries, commands, and test tools]

---
```

## Task Structure

Use checkbox syntax so the plan can be executed step by step:

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/new-file.ext`
- Modify: `exact/path/to/existing-file.ext`
- Test: `exact/path/to/test-file.ext`

- [ ] **Step 1: Write the failing test**

```language
[complete test code or exact test edit]
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `exact command`

Expected: fails for the specific missing behavior.

- [ ] **Step 3: Implement the behavior**

```language
[complete implementation code or exact edit]
```

- [ ] **Step 4: Run the focused test and verify it passes**

Run: `exact command`

Expected: passes.

- [ ] **Step 5: Run broader validation**

Run: `exact command`

Expected: passes.
````

Adapt the code block language and commands to the project.

## No Placeholders

Every step must contain the actual detail an engineer needs. These are plan failures:

- `TBD`, `TODO`, `later`, or `fill in`.
- "Add appropriate error handling" without the exact expected behavior.
- "Write tests for the above" without concrete test cases.
- "Similar to Task N" instead of repeating the needed details.
- Steps that describe code changes without showing enough code, signatures, or exact edit instructions.
- References to functions, types, commands, or paths not defined earlier in the plan.

## Subagent Plan Review

After writing the complete plan, dispatch a reviewer subagent before handing the plan back.

Use `references/plan-document-reviewer-prompt.md` as the reviewer prompt template. Fill in:

- `PLAN_FILE_PATH`: the implementation plan you just wrote.
- `SPEC_FILE_PATH`: the source spec or requirement file, when one exists. If there is no file-backed spec, include the concrete requirements summary used to write the plan.

The reviewer must check:

1. Spec coverage: every approved requirement maps to at least one task.
2. Placeholder scan: no vague or deferred instructions remain.
3. Type and naming consistency: names introduced in early tasks match later tasks.
4. Test coverage: each behavior change has focused verification and an appropriate broader check.
5. Execution order: each task can be completed using only prior tasks and current repo context.

Only blocking issues should require plan changes. Minor style preferences or nice-to-have improvements should be captured as advisory recommendations.

If the reviewer returns `Issues Found`, fix the plan inline and run the reviewer subagent again. Repeat until the reviewer returns `Approved` or there is a concrete disagreement to surface to the user.

If subagents are not available in the current runtime, perform the same review yourself and explicitly note that the subagent review was unavailable.

## Handoff

After saving the plan, summarize:

- Plan path.
- Number of tasks.
- Reviewer status.
- Any assumptions made.
- Any risks or prerequisites.

Then ask whether to proceed with implementation or revise the plan.
