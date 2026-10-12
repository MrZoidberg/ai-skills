#!/usr/bin/env python3
"""plan-review-hook.py - PreToolUse hook for ExitPlanMode.

intercepts ExitPlanMode so the plan gets reviewed before the agent proceeds.
if Plannotator (https://github.com/backnotprop/plannotator) is installed, it
registers its own ExitPlanMode/equivalent hook per its installer and owns the
interactive review UI directly -- this hook steps aside (allows the call) so
the two don't double-prompt. Otherwise falls back to plan-annotate.py
($EDITOR with unified diff).

hook receives JSON on stdin with the plan content in tool_input.plan field.
returns PreToolUse hook JSON response with permissionDecision:
  - "ask"  → no changes/annotations (or Plannotator is handling it), proceed
  - "deny" → feedback found, sent as denial reason

requirements:
  - plannotator (preferred, https://github.com/backnotprop/plannotator) or
    $EDITOR (fallback via plan-annotate.py: agterm, tmux, kitty, or wezterm)
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT_VARS = (
    "CODEX_PLUGIN_ROOT",
    "COPILOT_PLUGIN_ROOT",
    "CLAUDE_PLUGIN_ROOT",
    "PLUGIN_ROOT",
)


def first_env(names):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def read_plan_from_stdin() -> str:
    """read plan content from hook event JSON on stdin."""
    raw = sys.stdin.read()
    if not raw.strip():
        return ""
    try:
        event = json.loads(raw)
        return event.get("tool_input", {}).get("plan", "")
    except json.JSONDecodeError:
        return ""


def make_response(decision: str, reason: str = "") -> None:
    """output PreToolUse hook response and exit with appropriate code.
    deny: plain text to stderr + exit 2 (blocks the tool and shows the text).
    ask/allow: JSON to stdout + exit 0."""
    if decision == "deny":
        print(reason, file=sys.stderr)
        sys.exit(2)
    resp: dict = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
        }
    }
    if reason:
        resp["hookSpecificOutput"]["permissionDecisionReason"] = reason
    print(json.dumps(resp, indent=2))


def main() -> None:
    plan_content = read_plan_from_stdin()
    if not plan_content:
        make_response("ask", "no plan content in hook event")
        return

    # skip interactive review entirely when disabled (e.g. claude /remote-control, where
    # a host terminal overlay would be invisible to the remote client and block the
    # session). falls through to the normal ExitPlanMode confirmation, which the remote
    # client can see and act on. covers both Plannotator and the plan-annotate.py fallback.
    if os.environ.get("PLANNING_DISABLE_PLANNOTATOR"):
        make_response("ask", "plan review disabled via PLANNING_DISABLE_PLANNOTATOR")
        return

    # Plannotator, if installed, registers its own hook and owns the review UI --
    # step aside rather than also launching the plan-annotate.py fallback.
    if shutil.which("plannotator"):
        make_response("ask", "plannotator installed; it handles plan review directly")
        return

    plugin_root = first_env(PLUGIN_ROOT_VARS)
    if not plugin_root:
        make_response("ask", "plugin root not set (no CODEX/COPILOT/CLAUDE_PLUGIN_ROOT or PLUGIN_ROOT)")
        return

    # fall back to plan-annotate.py — it handles its own editor overlay and diffing.
    # since we already consumed stdin, we need to re-feed the JSON to it.
    annotate_script = Path(plugin_root) / "scripts" / "plan-annotate.py"
    if not annotate_script.exists():
        make_response("ask", "no review tool available (plannotator not installed, plan-annotate.py not found)")
        return

    stdin_data = json.dumps({"tool_input": {"plan": plan_content}})
    fallback = subprocess.run(
        [sys.executable, str(annotate_script)],
        input=stdin_data, capture_output=True, text=True, timeout=345600,
        env={**os.environ},
    )

    # plan-annotate.py outputs the hook JSON response directly
    output = fallback.stdout.strip()
    if output:
        print(output)
    else:
        make_response("ask", "plan reviewed, no changes")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\r\033[K", end="")
        sys.exit(130)
