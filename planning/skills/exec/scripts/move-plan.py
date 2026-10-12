#!/usr/bin/env python3
"""move a finished plan file into the archive directory beside its stage directory and commit it.

usage: move-plan.py <plan-file-path> [--dir <name>]

The archive directory is discovered rather than assumed, because repositories name it
differently: one keeps `future/`, `in-progress/` and `finished/` side by side, another uses
`completed/`. Discovery walks from the plan's own directory towards the repository root and
takes the nearest directory already carrying a known archive name; `finished` is preferred
over `completed` at the same level. When the plan sits in a stage directory (`future/`,
`in-progress/`, ...) the archive beside that directory wins over one inside it, so a plan in
`docs/plans/future/` lands in the sibling `docs/plans/finished/` when that exists, and in
`docs/plans/completed/` otherwise.

When no archive directory exists anywhere, one is created next to the plan's directory — or
next to its stage directory when the plan sits in one (`future/`, `in-progress/`, ...), since
the archive is a sibling of the stage directory rather than a child of it. `--dir <name>`
forces a specific name at the discovered level, or creates it when absent.

no-op if the plan already sits under a known archive directory or the file is missing.
commits via stage-and-commit.py; does NOT push.
"""

import subprocess
import sys
from pathlib import Path

# archive directory names to look for, in preference order
ARCHIVE_NAMES = ("finished", "completed")
# created when no archive directory exists yet
DEFAULT_ARCHIVE = "completed"
# directories plans are held in before completion; the archive is their sibling, not their child
STAGE_NAMES = ("future", "in-progress", "in_progress", "planned", "active", "wip")
# levels above the plan's own directory to search when git supplies no bound
MAX_CLIMB = 4


def repo_root(start: Path) -> Path | None:
    """the repository containing start, or None when git cannot answer."""
    result = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    if result.returncode != 0:
        return None
    top = result.stdout.strip()
    return Path(top) if top else None


def levels(plan_dir: Path) -> list[Path]:
    """plan_dir and its ancestors, nearest first, bounded by the repository root."""
    bound = repo_root(plan_dir)
    found: list[Path] = []
    level = plan_dir
    for _ in range(MAX_CLIMB + 1):
        found.append(level)
        # stop at the repository root; a plans directory can sit outside any repository,
        # in which case the climb is bounded by MAX_CLIMB alone
        if bound is not None and level == bound:
            break
        if level.parent == level:
            break
        level = level.parent
    return found


def resolve_archive(plan_dir: Path, name: str | None) -> Path:
    """the archive directory to move into, existing or not."""
    wanted = (name,) if name else ARCHIVE_NAMES
    levels_to_check = levels(plan_dir)
    if plan_dir.name in STAGE_NAMES and len(levels_to_check) > 1:
        # the archive belongs beside the stage directory, not inside it: a plan in
        # docs/plans/future/ belongs in docs/plans/finished/, and a stray
        # docs/plans/future/completed/ left by an older convention never wins over it
        levels_to_check = levels_to_check[1:] + levels_to_check[:1]
    for level in levels_to_check:
        for candidate in wanted:
            directory = level / candidate
            if directory.is_dir():
                return directory
    # nothing to join: create it beside the plan, or beside its stage directory
    parent = plan_dir.parent if plan_dir.name in STAGE_NAMES else plan_dir
    return parent / (name or DEFAULT_ARCHIVE)


def archive_names(name: str | None) -> set[str]:
    return set(ARCHIVE_NAMES) | ({name} if name else set())


def is_tracked(plan: str) -> bool:
    """whether the pre-move path is in the index.

    git add stages a deletion only for a path git already knows; for a plan that was never
    committed it aborts with "pathspec did not match any files". the move has happened by
    then, so passing that path would report a failure for a move that in fact succeeded.
    the check runs against the index, so it still answers after the file is gone, and the
    path is interpreted from the current directory exactly as the later git add will be.
    """
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", f":(literal){plan}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def parse_args(argv: list[str]) -> tuple[str, str | None] | None:
    args = list(argv)
    name = None
    if "--dir" in args:
        index = args.index("--dir")
        if index + 1 >= len(args):
            print("error: --dir needs a directory name", file=sys.stderr)
            return None
        name = args[index + 1]
        del args[index:index + 2]
        # a bare name keeps the destination inside the plans tree; a path would let the
        # move escape it, which is what --dir is not for
        if not name or name in (".", "..") or "/" in name or "\\" in name:
            print(f"error: --dir must be a bare directory name, got: {name!r}", file=sys.stderr)
            return None
    if len(args) != 1:
        print("error: usage: move-plan.py <plan-file-path> [--dir <name>]", file=sys.stderr)
        return None
    return args[0], name


def main() -> int:
    parsed = parse_args(sys.argv[1:])
    if parsed is None:
        return 1
    plan, name = parsed

    script_dir = Path(__file__).resolve().parent

    plan_path = Path(plan)
    # file missing (already moved, or never existed) — nothing to do
    if not plan_path.is_file():
        print(f"plan file not found, skipping move: {plan}", file=sys.stderr)
        return 0

    # already archived — nothing to do. this is checked against every directory the plan
    # sits under, not just a literal "completed", so rerunning is safe in either convention
    known = archive_names(name)
    if known & {parent.name for parent in plan_path.resolve().parents}:
        print(f"plan already archived: {plan}")
        return 0

    base = plan_path.name
    dest_dir = resolve_archive(plan_path.resolve().parent, name)
    dest = dest_dir / base
    tracked_before_move = is_tracked(plan)

    # refuse to clobber an existing plan with the same name
    if dest.exists() or dest.is_symlink():
        print(f"error: destination already exists, refusing to overwrite: {dest}", file=sys.stderr)
        return 1

    dest_dir.mkdir(parents=True, exist_ok=True)
    plan_path.rename(dest)

    # stage-and-commit.py stages both the old path (now removed) and the new one; git
    # records that as the rename plus commit. the old path is listed only when it is
    # tracked, since git cannot stage a deletion for a path it never knew.
    paths = [plan, str(dest)] if tracked_before_move else [str(dest)]
    result = subprocess.run(
        [sys.executable, str(script_dir / "stage-and-commit.py"),
         f"docs: move completed plan {base} to {dest_dir.name}/"] + paths
    )
    if result.returncode != 0:
        return result.returncode

    print(f"moved plan to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
