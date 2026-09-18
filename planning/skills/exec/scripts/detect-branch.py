#!/usr/bin/env python3
"""detect the default branch name of the current repository.

usage: detect-branch.py
outputs the branch name to stdout
avoids network calls when possible
"""

import re
import subprocess
import sys


def run(args: list[str]) -> str:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return result.stdout.strip()


def do_git() -> str:
    # 1. check cached remote HEAD (local, fast)
    ref = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"])
    branch = re.sub(r"^refs/remotes/origin/", "", ref)

    # 2. check for common default branch names locally
    if not branch:
        for candidate in ("main", "master", "trunk", "develop"):
            result = subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{candidate}"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                branch = candidate
                break

    # 3. last resort: ask remote (may block if network is unreachable)
    if not branch:
        show = run(["git", "remote", "show", "origin"])
        for line in show.splitlines():
            if "HEAD branch" in line:
                branch = line.split(":", 1)[-1].strip()
                break

    # 4. fallback
    return branch or "main"


def main() -> int:
    print(do_git())
    return 0


if __name__ == "__main__":
    sys.exit(main())
