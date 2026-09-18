# TODO

## Re-point the "write a plan" handoff to the planning skill

**Status:** done — the `planning` plugin was adopted for Codex CLI (see `adopt.md` for the
brainstorming precedent this followed).

### Origin

The upstream `brainstorming` skill (forked from
[umputun/cc-thingz](https://github.com/umputun/cc-thingz) in commit `1ae3878`, itself derived from
[obra/superpowers](https://github.com/obra/superpowers)) ended its Phase 4 handoff by invoking a
slash command from a sibling plugin:

```
/planning:make
```

That `planning:` namespace did not exist in this repo at the time — it belonged to Umputun's
plugin set, not ours. It was a dangling reference: the command would simply fail to resolve.

### What was done as a stopgap, then resolved

In `brainstorming` v0.2.0 every `/planning:make` reference was temporarily re-pointed at this
repo's `writing-plans` skill. `writing-plans` has since been removed and superseded by the adopted
`planning` plugin (`planning/commands/make.md`), so all 5 locations were updated to point at
`planning`'s `make` command instead:

| File | What changed |
|------|--------------|
| `brainstorming/skills/brainstorming/SKILL.md` | Phase 4 `AskUserQuestion` option, the bullet below it, and the CRITICAL self-modification paragraph |
| `brainstorming/skills/brainstorming/references/usage.md` | Phase 4 bullet, and the worked example |
| `brainstorming/README.md` | "Use it for" bullet, and step 4 of "How to use it" |
| `brainstorming/hooks/guard-self-edit.py` | the deny message shown to the agent |

Invocation is documented agent-neutrally: `$planning make` for Codex, `/planning:make` for
Copilot/Claude Code.
