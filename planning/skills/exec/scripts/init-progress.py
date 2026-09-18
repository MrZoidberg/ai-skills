#!/usr/bin/env python3
"""initialize the progress file with a header.

usage: init-progress.py <progress-file> <plan-path> <branch-name>
"""

import sys
from datetime import datetime


def main() -> int:
    if len(sys.argv) < 4 or not all(sys.argv[1:4]):
        print("error: usage: init-progress.py <progress-file> <plan-path> <branch-name>", file=sys.stderr)
        return 1

    file_path, plan, branch = sys.argv[1], sys.argv[2], sys.argv[3]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, "w") as f:
        f.write(f"# progress\nPlan: {plan}\nBranch: {branch}\nStarted: {timestamp}\n---\n")

    print(file_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
