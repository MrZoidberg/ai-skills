#!/usr/bin/env python3
"""run external code review and return findings on stdout.

usage: run-external-review.py "<external_review_cmd>" "<prompt>"

with an empty <external_review_cmd>, delegates to run-codex.py (codex-specific
sandbox/model flags). with a command set, that command is run
instead, with the prompt appended as the final argv element. the "External
review contract" section of README.md is authoritative for what the tool must
be able to do, emit, and leave untouched -- do not restate it here.

exits 127 when the tool is not on PATH so the caller can skip the phase rather
than treat it as a review failure. those two messages, and only those two, carry
the marker "run-external-review:" on stderr, so a 127 raised by the reviewer
itself (a wrapper whose inner tool is missing) stays distinguishable from this
one. nothing else written here may carry the marker -- an informational note
that did would make a reviewer's own 127 read as "no tool installed" and
silently skip the phase.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# the plugin-config framework's own placeholder for an unset option -- unlike
# the hook/MCP substitution path, Claude Code's skill-content substitution
# leaves this literal token untouched (no schema default merged in) when the
# user never configured the option. treat it as unset and take the codex
# fallback: the alternative is a 127 that reads as "no review tool installed"
# and silently skips the phase.
USER_CONFIG_PLACEHOLDER = re.compile(r"^\$\{user_config\.[^}]*\}$")


def main() -> int:
    if len(sys.argv) < 3 or not sys.argv[2]:
        print("error: usage: run-external-review.py '<external_review_cmd>' '<prompt>'", file=sys.stderr)
        return 1

    cmd = sys.argv[1] or ""
    prompt = sys.argv[2]
    script_dir = Path(__file__).resolve().parent

    if USER_CONFIG_PLACEHOLDER.match(cmd):
        print("note: external_review_cmd is not configured, using codex", file=sys.stderr)
        cmd = ""

    # a newline would be swallowed by the whitespace split below, running a
    # truncated command instead of the configured one -- report it rather
    # than truncate silently
    if "\n" in cmd:
        print("error: external_review_cmd must be a single line", file=sys.stderr)
        return 1

    # split on whitespace so a command carrying flags works, e.g.
    # "mytool review --strict". arguments containing spaces are not
    # supported -- wrap anything that needs quoting in a script and point
    # the config at it. an unset or whitespace-only config yields a
    # zero-length list, which must take the codex fallback rather than exit
    # 127 and silently skip the whole phase
    cmd_args = cmd.split()

    if not cmd_args:
        if not shutil.which("codex"):
            print("error: run-external-review: codex not on PATH and external_review_cmd is not set", file=sys.stderr)
            return 127
        result = subprocess.run([sys.executable, str(script_dir / "run-codex.py"), prompt])
        return result.returncode

    if not shutil.which(cmd_args[0]):
        print(f"error: run-external-review: external_review_cmd not on PATH: {cmd_args[0]}", file=sys.stderr)
        return 127

    # stdin from os.devnull: an inherited open pipe (background launch) would
    # let a tool that reads stdin block forever, the same failure run-codex.py
    # guards against
    with open(os.devnull) as devnull:
        result = subprocess.run(cmd_args + [prompt], stdin=devnull)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
