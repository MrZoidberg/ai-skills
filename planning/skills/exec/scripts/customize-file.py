#!/usr/bin/env python3
"""copy a bundled prompt or agent file to an override location for editing.

usage: customize-file.py <relative-path> [data-dir]
e.g.: customize-file.py prompts/review.md
e.g.: customize-file.py agents/quality.txt /path/to/plugin/data

with a data-dir, copies to <data-dir>/<path> (user level, all projects).
without one, copies to .agents/exec-plan/<path> (project level).

an override shadows the bundled default permanently -- see the "Customization"
paragraph of README.md, which is authoritative for the consequences

refuses to overwrite an existing override; prints the destination path
"""

import os
import shutil
import sys
from pathlib import Path, PurePosixPath


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1]:
        print("error: usage: customize-file.py <relative-path> [data-dir]", file=sys.stderr)
        return 1

    path = sys.argv[1]

    # path must be relative and stay inside the override dir
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts:
        print(f"error: path must be relative and stay inside the override dir: {path}", file=sys.stderr)
        return 1

    # a passed-but-empty data dir means ${CLAUDE_PLUGIN_DATA} substituted to nothing,
    # so user-level overrides are unavailable. report it instead of silently writing a
    # project-level copy the caller did not ask for -- same handling as commands/make.md.
    data_dir = sys.argv[2].rstrip("/") if len(sys.argv) >= 3 else None
    if len(sys.argv) >= 3 and not data_dir:
        print(
            "error: data-dir argument is empty or the filesystem root -- user-level overrides "
            "require the plugin to be installed from the marketplace; omit the argument for a "
            "project-level copy",
            file=sys.stderr,
        )
        return 1

    # derive skill root from script location: <skill-root>/scripts/customize-file.py
    skill_root = Path(__file__).resolve().parent.parent

    src = skill_root / "references" / path
    if not src.is_file():
        print(f"error: no bundled file at {path}", file=sys.stderr)
        return 1

    if data_dir:
        dest = Path(data_dir) / path
        stop = data_dir
    else:
        dest = Path(".agents/exec-plan") / path
        stop = "."

    # a dangling symlink is invisible to is_file()/exists() through it, so check
    # is_symlink() too: cp would follow it and write outside the override directory,
    # defeating the path guard above
    if dest.exists() or dest.is_symlink():
        print(f"error: override already exists, edit it in place: {dest}", file=sys.stderr)
        return 1

    # the exists()/is_symlink() check above only covers the destination file. any
    # ancestor directory can be a symlink too: mkdir(parents=True) accepts it and cp
    # follows it, so the copy lands outside the override dir. walk the components at
    # or below the override root and refuse any symlink among them. components above
    # the root are not checked -- the data dir comes from the caller, and a symlinked
    # $HOME or ~/.claude is a legitimate setup.
    #
    # the two branches are deliberately asymmetric: at project level the walk stops at
    # the working directory, so `.claude` itself is checked too. that is stricter than
    # the user-level exemption on purpose -- `.claude` comes out of the checked-out
    # repository, not the caller, so a repo shipping `.claude` as a symlink could
    # otherwise redirect the copy anywhere. someone whose `.claude` is symlinked into a
    # dotfiles repo gets a clear error and can use the user-level data dir instead
    # "." terminates the walk as well as "/": dirname(".") is ".", so a stop that is
    # somehow absent from the chain would otherwise spin here forever rather than fail
    directory = os.path.dirname(str(dest)) or "."
    while directory not in (stop, "/", "."):
        if os.path.islink(directory):
            print(f"error: refusing to write through a symlinked directory component: {directory}", file=sys.stderr)
            return 1
        directory = os.path.dirname(directory) or "."

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
