#!/bin/sh
set -eu

REPO_URL_DEFAULT="https://github.com/MrZoidberg/ai-skills.git"
BRANCH_DEFAULT="master"

usage() {
  cat <<'EOF'
AI Skills installer (macOS/Linux)

Usage:
  curl -fsSL https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.sh | sh -s -- [OPTIONS]

Options:
  --skill NAME            Skill directory name (e.g. coding-python)
  --system NAME           Agentic system: codex | copilot | claude | antigravity
  --scope NAME            Install scope: user | project (aliases: system | repo)
  --repo-root PATH        Repo root for project installs (auto-detected if omitted)
  --source-repo URL       Git repo URL (default: MrZoidberg/ai-skills)
  --branch NAME           Git branch (default: master)
  -y, --yes               Non-interactive (fail if required args missing)
  -h, --help              Show this help

Notes:
- Source of truth for a skill is a GitHub directory like:
  https://github.com/MrZoidberg/ai-skills/tree/master/<skill>
- This installer clones/pulls the full repo via git, then installs the chosen skill via symlink.
EOF
}

die() {
  printf '%s\n' "$*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

prompt() {
  var_name="$1"
  prompt_text="$2"
  eval "current=\${$var_name-}"
  if [ -n "${current}" ]; then
    return 0
  fi
  if [ "${YES:-0}" = "1" ]; then
    die "Missing required option: $var_name"
  fi
  printf '%s' "$prompt_text" >&2
  IFS= read -r value
  [ -n "$value" ] || die "Empty input for $var_name"
  eval "$var_name=\"$value\""
}

SKILL=""
SYSTEM=""
SCOPE=""
REPO_ROOT=""
SOURCE_REPO="$REPO_URL_DEFAULT"
BRANCH="$BRANCH_DEFAULT"
YES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --skill)
      SKILL="$2"; shift 2 ;;
    --system|--agent)
      SYSTEM="$2"; shift 2 ;;
    --scope)
      SCOPE="$2"; shift 2 ;;
    --repo-root)
      REPO_ROOT="$2"; shift 2 ;;
    --source-repo)
      SOURCE_REPO="$2"; shift 2 ;;
    --branch)
      BRANCH="$2"; shift 2 ;;
    -y|--yes)
      YES=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      die "Unknown argument: $1 (use --help)" ;;
  esac
done

prompt SKILL "Skill (e.g. coding-python): "
prompt SYSTEM "System (codex/copilot/claude/antigravity): "
prompt SCOPE "Scope (system/repo) or (user/project): "

case "$SYSTEM" in
  codex|copilot|claude|claude-code|antigravity) ;;
  *) die "Invalid --system: $SYSTEM" ;;
esac

if [ "$SYSTEM" = "claude-code" ]; then
  SYSTEM="claude"
fi

case "$SCOPE" in
  user|project|system|repo) ;;
  *) die "Invalid --scope: $SCOPE" ;;
esac

if [ "$SCOPE" = "system" ]; then
  SCOPE="user"
fi
if [ "$SCOPE" = "repo" ]; then
  SCOPE="project"
fi

need_cmd git

if [ -z "$REPO_ROOT" ] && [ "$SCOPE" = "project" ]; then
  if REPO_ROOT_DETECTED=$(git rev-parse --show-toplevel 2>/dev/null); then
    REPO_ROOT="$REPO_ROOT_DETECTED"
  else
    REPO_ROOT="$PWD"
  fi
fi

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
SRC_DIR="$DATA_HOME/agent-skills/ai-skills"

mkdir -p "$(dirname "$SRC_DIR")"
if [ ! -d "$SRC_DIR/.git" ]; then
  git clone --depth 1 --branch "$BRANCH" "$SOURCE_REPO" "$SRC_DIR"
else
  git -C "$SRC_DIR" pull --ff-only
fi

SKILL_SRC="$SRC_DIR/$SKILL"
[ -f "$SKILL_SRC/SKILL.md" ] || die "Skill not found in source repo: $SKILL_SRC (expected SKILL.md)"

case "$SYSTEM:$SCOPE" in
  codex:user)
    DEST_ROOT="$HOME/.agents/skills" ;;
  codex:project)
    DEST_ROOT="$REPO_ROOT/.agents/skills" ;;
  copilot:user)
    DEST_ROOT="$HOME/.copilot/skills" ;;
  copilot:project)
    DEST_ROOT="$REPO_ROOT/.github/skills" ;;
  claude:user)
    DEST_ROOT="$HOME/.claude/skills" ;;
  claude:project)
    DEST_ROOT="$REPO_ROOT/.claude/skills" ;;
  antigravity:user)
    DEST_ROOT="$HOME/.agents/skills" ;;
  antigravity:project)
    DEST_ROOT="$REPO_ROOT/.agents/skills" ;;
  *)
    die "Unsupported combination: $SYSTEM / $SCOPE" ;;
esac

DEST="$DEST_ROOT/$SKILL"

mkdir -p "$DEST_ROOT"
rm -rf "$DEST"
ln -s "$SKILL_SRC" "$DEST"

printf '%s\n' "Installed '$SKILL' for $SYSTEM ($SCOPE) -> $DEST" >&2
printf '%s\n' "Source: https://github.com/MrZoidberg/ai-skills/tree/master/$SKILL" >&2
