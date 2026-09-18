# TODO

## Re-point the "write a plan" handoff to the planning skill

**Status:** open — blocked on the planning skill existing in this repo.

### Origin

The upstream `brainstorming` skill (forked from
[umputun/cc-thingz](https://github.com/umputun/cc-thingz) in commit `1ae3878`, itself derived from
[obra/superpowers](https://github.com/obra/superpowers)) ended its Phase 4 handoff by invoking a
slash command from a sibling plugin:

```
/planning:make
```

That `planning:` namespace does not exist in this repo — it belongs to Umputun's plugin set, not
ours. It was a dangling reference: the command would simply fail to resolve.

### What was done as a stopgap

In `brainstorming` v0.2.0 every `/planning:make` reference was re-pointed at this repo's existing
[`writing-plans`](writing-plans/README.md) skill, which covers the same ground (turn an approved
design into a task-by-task implementation plan). Locations:

| File | Line(s) |
|------|---------|
| `brainstorming/skills/brainstorming/SKILL.md` | Phase 4 `AskUserQuestion` option, and the bullet below it |
| `brainstorming/skills/brainstorming/SKILL.md` | the CRITICAL self-modification paragraph |
| `brainstorming/skills/brainstorming/references/usage.md` | Phase 4 bullet, and the worked example |
| `brainstorming/README.md` | "Use it for" bullet, and step 4 of "How to use it" |
| `brainstorming/hooks/guard-self-edit.py` | the deny message shown to the agent |

### What to do

A dedicated planning skill/script is planned. Once it lands, decide whether it supersedes
`writing-plans` for this handoff and update the references above accordingly — including the deny
message in `guard-self-edit.py`, which is easy to miss because it is a Python string rather than
markdown.

To find them all:

```bash
grep -rn "writing-plans" brainstorming/
```

Keep the invocation syntax agent-neutral in prose (`$skill-name` for Codex, `/skill-name` for
Copilot), since this repo targets both.
