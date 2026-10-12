#!/usr/bin/env python3
"""run codex review and return output.

usage: run-codex.py "<prompt>"
outputs codex response to stdout

stdout/stderr are inherited so codex's output streams straight through; stdin
is redirected from os.devnull because `codex exec` reads stdin to append a
<stdin> block even when a prompt arg is given, and an inherited open pipe
(e.g. a background launch) would block it forever waiting for EOF.
"""

import os
import subprocess
import sys


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1]:
        print("error: usage: run-codex.py '<prompt>'", file=sys.stderr)
        return 1
    prompt = sys.argv[1]

    args = ["codex", "exec", "--sandbox", "read-only"]

    # -c overrides switch provider routing in a way some corporate codex
    # proxies / wrappers reject (e.g. "Error: Model provider 'responses' not
    # found"). Set CODEX_NO_OVERRIDES=1 to skip the overrides and fall
    # through to the proxy's defaults. Only the literal value `1` activates
    # suppression -- any other value (including `0`, `false`, empty) keeps
    # the overrides on, matching the documented "set to 1 to enable" semantic.
    if os.environ.get("CODEX_NO_OVERRIDES", "") != "1":
        model = os.environ.get("CODEX_MODEL", "gpt-5.5")
        args += [
            "-c", f"model={model}",
            "-c", "model_reasoning_effort=xhigh",
            "-c", "stream_idle_timeout_ms=3600000",
        ]

    args.append(prompt)

    with open(os.devnull) as devnull:
        result = subprocess.run(args, stdin=devnull)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
