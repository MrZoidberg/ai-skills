#!/usr/bin/env python3
"""create a feature branch from plan file name if on the default branch.

usage: create-branch.py <plan-file-path>
exits 0 if branch created or already on feature branch
outputs branch name to stdout

strips leading YYYYMMDD- date prefix from branch name since plan files
use date prefixes (e.g., 20260329-feature-name.md) but branch names should not
"""

import re
import subprocess
import sys
from pathlib import Path


def run(args: list[str]) -> str:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return result.stdout.strip()


def derive_branch_name(plan_file: str) -> str:
    # e.g., docs/plans/20260329-feature-name.md -> feature-name
    name = Path(plan_file).stem
    # strip leading date prefix if present (YYYYMMDD- or YYYY-MM-DD-)
    return re.sub(r"^\d{4}-?\d{2}-?\d{2}-", "", name)


def detect_default_branch_git() -> str:
    ref = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"])
    default_branch = re.sub(r"^refs/remotes/origin/", "", ref)
    if not default_branch:
        for candidate in ("main", "master", "trunk", "develop"):
            result = subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{candidate}"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                default_branch = candidate
                break
    if not default_branch:
        show = run(["git", "remote", "show", "origin"])
        for line in show.splitlines():
            if "HEAD branch" in line:
                default_branch = line.split(":", 1)[-1].strip()
                break
    return default_branch


def do_git(plan_file: str) -> str:
    current_branch = run(["git", "branch", "--show-current"])
    default_branch = detect_default_branch_git()

    # if already on a feature branch (not the default and not detached), just report it
    if current_branch and default_branch and current_branch != default_branch:
        return current_branch
    if current_branch and not default_branch and current_branch not in ("main", "master"):
        return current_branch

    branch_name = derive_branch_name(plan_file)

    exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0
    if exists:
        subprocess.run(["git", "checkout", branch_name], check=True)
    else:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)

    return branch_name


def main() -> int:
    args = sys.argv[1:]

    # --print-name mode: derive and print the branch name only, with NO VCS side effects.
    # the exec SKILL uses this in worktree mode to name the worktree/branch without ever
    # running `git checkout -b` in the main working tree (which would break isolation).
    if args and args[0] == "--print-name":
        if len(args) < 2 or not args[1]:
            print("error: plan file path required", file=sys.stderr)
            return 1
        print(derive_branch_name(args[1]))
        return 0

    if not args or not args[0]:
        print("error: plan file path required", file=sys.stderr)
        return 1

    plan_file = args[0]
    try:
        print(do_git(plan_file))
    except subprocess.CalledProcessError as exc:
        return exc.returncode or 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
