"""resolve custom rules file through the two-layer override chain.

usage: resolve-rules.py <filename> [data-dir] [--source]

  <filename>   e.g. brainstorm-rules.md
  [data-dir]   plugin data directory. falls back to the *_PLUGIN_DATA env vars.
  --source     print "project" / "user" / "none" instead of the file content.

checks in order (first-found-wins, never merged):
  1. .agents/<filename>   relative to the current working directory (project)
  2. <data-dir>/<filename>                                          (user)

empty or whitespace-only files are treated as absent and fall through.
outputs the file content to stdout if found, nothing if not.
always exits 0 -- the caller treats empty output as "no custom rules".
"""

import os
import sys
from pathlib import Path

DATA_DIR_VARS = (
    "CODEX_PLUGIN_DATA",
    "COPILOT_PLUGIN_DATA",
    "CLAUDE_PLUGIN_DATA",
    "PLUGIN_DATA",
)


def read_if_present(path):
    """return the file's text, or None if it is missing, empty or unreadable."""
    try:
        if not path.is_file():
            return None
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return text if text.strip() else None


def resolve_data_dir(argv_value):
    if argv_value:
        return argv_value
    for var in DATA_DIR_VARS:
        value = os.environ.get(var)
        if value:
            return value
    return None


def main(argv):
    args = [a for a in argv[1:] if a != "--source"]
    want_source = "--source" in argv[1:]

    if not args or not args[0]:
        if want_source:
            print("none")
        return 0

    filename = args[0]
    data_dir = resolve_data_dir(args[1] if len(args) > 1 else None)

    candidates = [("project", Path.cwd() / ".agents" / filename)]
    if data_dir:
        candidates.append(("user", Path(data_dir) / filename))

    for level, path in candidates:
        content = read_if_present(path)
        if content is not None:
            if want_source:
                print(level)
            else:
                sys.stdout.write(content)
            return 0

    if want_source:
        print("none")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:  # noqa: BLE001 - never fail the caller over missing rules
        sys.exit(0)
