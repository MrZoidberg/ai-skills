"""PreToolUse guard: refuse any write that targets the planning plugin's own files.

Reads the PreToolUse hook payload as JSON on stdin.

Exit codes -- deliberately only ever 0 or 2:
  0  allow (also: parse failure, unknown payload, missing plugin root)
  2  deny; the reason is written to stderr

Exit code 2 is the one deny mechanism both Codex CLI and Copilot CLI honour, so
this hook uses it instead of the (incompatible) JSON decision payloads. Copilot
treats *any* other non-zero preToolUse exit as a deny, which would block every
tool call in the session -- hence the blanket try/except that exits 0.

Set PLANNING_ALLOW_SELF_EDIT=1 to bypass the guard for deliberate maintenance.
"""

import json
import os
import re
import sys
from pathlib import Path

PLUGIN_ROOT_VARS = (
    "CODEX_PLUGIN_ROOT",
    "COPILOT_PLUGIN_ROOT",
    "CLAUDE_PLUGIN_ROOT",
    "PLUGIN_ROOT",
)
PLUGIN_DATA_VARS = (
    "CODEX_PLUGIN_DATA",
    "COPILOT_PLUGIN_DATA",
    "CLAUDE_PLUGIN_DATA",
    "PLUGIN_DATA",
)

# tool_input keys that carry a single target path, across Codex/Copilot/Claude naming
PATH_KEYS = ("file_path", "filePath", "path", "notebook_path", "notebookPath", "target_file")

SHELL_TOOLS = {"bash", "shell", "powershell", "pwsh", "sh", "run_command", "local_shell"}

# only these tools can write; everything else (Read, Grep, Glob, ...) is always allowed.
# covers Codex, Copilot's Claude-compatible names, and Claude Code itself.
WRITE_TOOLS = SHELL_TOOLS | {
    "write",
    "edit",
    "multiedit",
    "notebookedit",
    "create",
    "apply_patch",
    "applypatch",
    "str_replace_editor",
    "str_replace_based_edit_tool",
}

# constructs that make a shell command a *write* rather than a read
MUTATING = re.compile(
    r"(>>?|\btee\b|\brm\b|\bmv\b|\bcp\b|\bln\b|\btruncate\b|\bdd\b|\bpatch\b|\bchmod\b|\bchown\b"
    r"|\bsed\b[^|;]*-i|\bperl\b[^|;]*-i|\bgit\s+(checkout|restore|apply|clean|rm|mv)\b"
    r"|Set-Content|Add-Content|Out-File|Remove-Item|New-Item|Move-Item|Copy-Item)",
    re.IGNORECASE,
)

ALLOWED_BASENAMES = {"planning-rules.md"}


def first_env(names):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def real(path):
    try:
        return Path(os.path.realpath(str(path)))
    except OSError:
        return Path(str(path))


def plugin_roots():
    """return (canonical_root, [all spellings of it to look for in shell commands]).

    The raw env value and its realpath can differ -- plugins are commonly installed
    as symlinks (see install.sh), and on macOS /tmp resolves to /private/tmp. A
    shell command will normally name the un-resolved path, so match against both.
    """
    value = first_env(PLUGIN_ROOT_VARS)
    if not value:
        # fall back to this script's own plugin dir: <root>/hooks/guard-self-edit.py
        value = str(Path(__file__).resolve().parent.parent)
    canonical = real(value)
    spellings = {str(canonical), value.rstrip("/\\")}
    return canonical, sorted(s for s in spellings if s)


def is_inside(child, parent):
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def apply_patch_paths(text):
    """pull file paths out of an apply_patch / unified-diff body."""
    found = []
    for line in text.splitlines():
        stripped = line.strip()
        for prefix in (
            "*** Add File:",
            "*** Update File:",
            "*** Delete File:",
            "*** Move to:",
            "+++ ",
            "--- ",
        ):
            if stripped.startswith(prefix):
                candidate = stripped[len(prefix) :].strip()
                if candidate and candidate != "/dev/null":
                    # strip a/ b/ diff prefixes
                    candidate = re.sub(r"^[ab]/", "", candidate)
                    found.append(candidate)
    return found


def candidate_paths(tool_name, tool_input):
    """return (paths, shell_command_text) implied by this tool call."""
    paths = []
    command_text = None

    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (ValueError, TypeError):
            tool_input = {"command": tool_input}

    if not isinstance(tool_input, dict):
        return paths, command_text

    for key in PATH_KEYS:
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            paths.append(value)

    for key in ("edits", "files"):
        value = tool_input.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for path_key in PATH_KEYS:
                        nested = item.get(path_key)
                        if isinstance(nested, str) and nested:
                            paths.append(nested)

    lowered = (tool_name or "").lower()

    for key in ("patch", "input", "diff"):
        value = tool_input.get(key)
        if isinstance(value, str) and ("*** " in value or value.startswith("---")):
            paths.extend(apply_patch_paths(value))
    if "apply_patch" in lowered and isinstance(tool_input.get("command"), str):
        paths.extend(apply_patch_paths(tool_input["command"]))

    if lowered in SHELL_TOOLS or "apply_patch" in lowered:
        for key in ("command", "cmd", "script"):
            value = tool_input.get(key)
            if isinstance(value, str) and value:
                command_text = value
                break
            if isinstance(value, list) and value:
                command_text = " ".join(str(part) for part in value)
                break

    return paths, command_text


def allowed(path, data_dir):
    if path.name in ALLOWED_BASENAMES:
        return True
    if data_dir and is_inside(path, data_dir):
        return True
    return False


def deny(target):
    sys.stderr.write(
        "Blocked by the planning plugin's self-modification guard: "
        f"{target}\n"
        "This skill must never modify its own files (SKILL.md, commands, scripts, "
        "references, hooks, plugin manifests). Custom behaviour belongs in a rules "
        "file at .agents/planning-rules.md instead. To change the skill itself, "
        "propose a plan with the planning skill's own make command, or re-run with "
        "PLANNING_ALLOW_SELF_EDIT=1 for deliberate maintenance.\n"
    )
    return 2


def main():
    if os.environ.get("PLANNING_ALLOW_SELF_EDIT", "").strip().lower() not in ("", "0", "false", "no"):
        return 0

    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except ValueError:
        return 0
    if not isinstance(payload, dict):
        return 0

    tool_name = payload.get("tool_name") or payload.get("toolName") or ""
    tool_input = payload.get("tool_input")
    if tool_input is None:
        tool_input = payload.get("toolArgs")
    if tool_input is None:
        tool_input = payload.get("tool_args") or {}

    if (tool_name or "").lower() not in WRITE_TOOLS:
        return 0

    root, root_spellings = plugin_roots()
    data_value = first_env(PLUGIN_DATA_VARS)
    data_dir = real(data_value) if data_value else None

    cwd = payload.get("cwd") or os.getcwd()

    paths, command_text = candidate_paths(tool_name, tool_input)

    for raw_path in paths:
        resolved = real(Path(cwd) / raw_path) if not os.path.isabs(raw_path) else real(raw_path)
        if is_inside(resolved, root) and not allowed(resolved, data_dir):
            return deny(str(resolved))

    if command_text and MUTATING.search(command_text):
        names_root = any(spelling in command_text for spelling in root_spellings)
        # a mutating shell command that names the plugin root, or runs from inside it
        if names_root or is_inside(real(cwd), root):
            if not any(name in command_text for name in ALLOWED_BASENAMES):
                return deny(f"shell command touching {root}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - never fail-close; Copilot denies on any other non-zero exit
        sys.exit(0)
