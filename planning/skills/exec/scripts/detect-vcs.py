#!/usr/bin/env python3
"""detect the VCS of the current working directory.

usage: detect-vcs.py
outputs "git" on stdout; exits 1 if not a git repository
"""

import subprocess
import sys


def detect_vcs() -> str:
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
        return "git"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("error: not a git repository", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    print(detect_vcs())
