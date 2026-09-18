#!/usr/bin/env python3
"""move a completed plan file into its sibling completed/ directory and commit it.

usage: move-plan.py <plan-file-path>
no-op if the plan is already under completed/ or the file is missing
commits via stage-and-commit.py; does NOT push
"""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print("error: usage: move-plan.py <plan-file-path>", file=sys.stderr)
        return 1

    plan = sys.argv[1]
    script_dir = Path(__file__).resolve().parent

    # already under completed/ — nothing to do
    if "/completed/" in plan.replace("\\", "/"):
        print(f"plan already under completed/: {plan}")
        return 0

    plan_path = Path(plan)
    # file missing (already moved, or never existed) — nothing to do
    if not plan_path.is_file():
        print(f"plan file not found, skipping move: {plan}", file=sys.stderr)
        return 0

    base = plan_path.name
    dest_dir = plan_path.parent / "completed"
    dest = dest_dir / base

    # refuse to clobber an existing completed plan with the same name
    if dest.exists() or dest.is_symlink():
        print(f"error: destination already exists, refusing to overwrite: {dest}", file=sys.stderr)
        return 1

    dest_dir.mkdir(parents=True, exist_ok=True)
    plan_path.rename(dest)

    # stage-and-commit.py stages both the (now-removed) old path and the new path;
    # git records this as the rename plus commit
    result = subprocess.run(
        [sys.executable, str(script_dir / "stage-and-commit.py"),
         f"docs: move completed plan {base} to completed/", plan, str(dest)]
    )
    if result.returncode != 0:
        return result.returncode

    print(f"moved plan to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
