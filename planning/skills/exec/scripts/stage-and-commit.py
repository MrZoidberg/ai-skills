#!/usr/bin/env python3
"""stage files and commit with a message.

usage: stage-and-commit.py <message> <file1> [file2 ...]
"""

import subprocess
import sys


def do_git(msg: str, paths: list[str]) -> None:
    # every name is passed as a :(literal) pathspec, so one holding '*', '?' or
    # '[...]' matches itself rather than something else. the magic prefix is used
    # rather than GIT_LITERAL_PATHSPECS because hooks inherit that variable and it
    # would silently change how their own pathspecs resolve.
    listed = [f":(literal){path}" for path in paths]
    subprocess.run(["git", "add", "--"] + listed, check=True)
    subprocess.run(["git", "commit", "-m", msg, "--"] + listed, check=True)

    # a path-scoped commit runs hooks against a temporary index, so nothing a
    # pre-commit hook stages reaches the real index — neither a reformatted copy
    # of a listed path nor an unlisted one the hook adds itself, such as a
    # regenerated lockfile. reconcile every path the commit actually recorded,
    # not just the listed ones: an unlisted path would otherwise sit in the index
    # as a staged deletion of a file present in both HEAD and the worktree.
    # anything staged but not committed is left alone.
    # diff-tree reports paths from the repository root while a pathspec resolves
    # against the current directory, so :(top) anchors them; without it the reset
    # silently matches nothing whenever the caller sits in a subdirectory.
    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "-z", "HEAD"],
        stdout=subprocess.PIPE, check=True, text=True,
    )
    committed_paths = [p for p in result.stdout.split("\0") if p]
    if committed_paths:
        committed = [f":(top,literal){path}" for path in committed_paths]
        subprocess.run(["git", "reset", "-q", "--"] + committed, check=True)


def main() -> int:
    if len(sys.argv) < 3:
        print("error: usage: stage-and-commit.py <message> <file1> [file2 ...]", file=sys.stderr)
        return 1

    message = sys.argv[1]
    paths = sys.argv[2:]

    # an empty path must be rejected here: as a git pathspec it matches everything under
    # the current directory, so it would silently commit the whole tree instead of failing
    for path in paths:
        if not path:
            print("error: empty file argument", file=sys.stderr)
            return 1

    try:
        do_git(message, paths)
    except subprocess.CalledProcessError as exc:
        return exc.returncode or 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
