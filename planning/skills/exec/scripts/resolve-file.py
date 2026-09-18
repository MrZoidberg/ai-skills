#!/usr/bin/env python3
"""resolve a file through the three-layer override chain.

usage: resolve-file.py <relative-path> [data-dir]
e.g.: resolve-file.py prompts/task.md /path/to/plugin/data
e.g.: resolve-file.py agents/quality.txt /path/to/plugin/data

data-dir: plugin data directory path, passed from SKILL.md where
${CLAUDE_PLUGIN_DATA} (or the Codex/Copilot equivalent) is text-substituted
by the plugin framework. falls back to the *_PLUGIN_DATA env var chain if
not provided as argument.

checks in order:
  1. .agents/exec-plan/<path> (project override)
  2. <data-dir>/<path> (user override)
  3. bundled default (derived from script location)

outputs the file content to stdout
"""

import os
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1]:
        print("error: usage: resolve-file.py <relative-path> [data-dir]", file=sys.stderr)
        return 1

    path = sys.argv[1]

    # use argument if provided, fall back to the env-var chain
    if len(sys.argv) >= 3:
        data_dir = sys.argv[2]
    else:
        data_dir = (
            os.environ.get("CODEX_PLUGIN_DATA")
            or os.environ.get("COPILOT_PLUGIN_DATA")
            or os.environ.get("CLAUDE_PLUGIN_DATA")
            or os.environ.get("PLUGIN_DATA")
            or ""
        )

    # derive skill root from script location: <skill-root>/scripts/resolve-file.py
    skill_root = Path(__file__).resolve().parent.parent

    candidates = [Path(".agents/exec-plan") / path]
    if data_dir:
        candidates.append(Path(data_dir) / path)
    candidates.append(skill_root / "references" / path)

    for candidate in candidates:
        if candidate.is_file():
            sys.stdout.write(candidate.read_text())
            return 0

    print(f"error: file not found in override chain: {path}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
