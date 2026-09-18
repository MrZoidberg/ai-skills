#!/usr/bin/env python3
"""append to the progress file with timestamp.

usage: append-progress.py <progress-file> [message]
if message is provided, appends single timestamped line
if no message, reads stdin and appends all lines (for multi-line content)
"""

import sys
from datetime import datetime


def main() -> int:
    if len(sys.argv) < 2:
        print("error: usage: append-progress.py <file> [message]", file=sys.stderr)
        return 1

    file_path = sys.argv[1]
    message_args = sys.argv[2:]

    with open(file_path, "a") as f:
        if message_args:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {' '.join(message_args)}\n")
        else:
            f.write(sys.stdin.read())

    return 0


if __name__ == "__main__":
    sys.exit(main())
