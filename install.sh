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
  --plugin NAME           Plugin name (e.g. coding-python). Installs all skills under <plugin>/skills if present.
  --system NAME           Agentic system: codex | copilot | claude | antigravity
  --scope NAME            Install scope: user | project (aliases: system | repo)
  --repo-root PATH        Repo root for project installs (auto-detected if omitted)
  --source-repo URL       Git repo URL (default: MrZoidberg/ai-skills)
  --branch NAME           Git branch (default: master)
  -y, --yes               Non-interactive (fail if required args missing)
  -h, --help              Show this help

Notes:
- This installer clones/pulls the full repo via git, then installs via symlink.
EOF
}

die() {
  printf '%s\n' "$*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

install_skill_dir() {
  skill_dir="$1"
  skill_name=$(basename "$skill_dir")
  [ -f "$skill_dir/SKILL.md" ] || die "Invalid skill directory (missing SKILL.md): $skill_dir"

  dest="$DEST_ROOT/$skill_name"
  rm -rf "$dest"
  ln -s "$skill_dir" "$dest"

  rel_path=${skill_dir#"$SRC_DIR/"}
  printf '%s\n' "Installed '$skill_name' for $SYSTEM ($SCOPE) -> $dest" >&2
  printf '%s\n' "Source: https://github.com/MrZoidberg/ai-skills/tree/$BRANCH/$rel_path" >&2
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

PLUGIN=""
SYSTEM=""
SCOPE=""
REPO_ROOT=""
SOURCE_REPO="$REPO_URL_DEFAULT"
BRANCH="$BRANCH_DEFAULT"
YES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --plugin)
      PLUGIN="$2"; shift 2 ;;
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

prompt PLUGIN "Plugin (e.g. coding-python): "
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

mkdir -p "$DEST_ROOT"

# Layout resolution for a plugin name (also supports legacy single-skill layout):
# 1) Legacy: <name>/SKILL.md
# 2) Plugin: <plugin>/skills/<skill>/SKILL.md (install all skills under <plugin>/skills)
# 3) Fallback: search for a matching directory name containing SKILL.md
SKILL_SRC_LEGACY="$SRC_DIR/$PLUGIN"
PLUGIN_SKILLS_DIR="$SRC_DIR/$PLUGIN/skills"

if [ -f "$SKILL_SRC_LEGACY/SKILL.md" ]; then
  install_skill_dir "$SKILL_SRC_LEGACY"
elif [ -d "$PLUGIN_SKILLS_DIR" ]; then
  found_any=0
  for d in "$PLUGIN_SKILLS_DIR"/*; do
    [ -d "$d" ] || continue
    [ -f "$d/SKILL.md" ] || continue
    found_any=1
    install_skill_dir "$d"
  done
  [ "$found_any" = "1" ] || die "No skills found in plugin: $PLUGIN_SKILLS_DIR"
else
  need_cmd find
  # Try to find a skill directory whose basename matches $PLUGIN.
  match_file=$(find "$SRC_DIR" -type f -name SKILL.md -path "*/$PLUGIN/SKILL.md" -print -quit 2>/dev/null || true)
  [ -n "$match_file" ] || die "Plugin/skill not found: $PLUGIN (expected either $SKILL_SRC_LEGACY/SKILL.md or $PLUGIN_SKILLS_DIR/*/SKILL.md)"
  install_skill_dir "$(dirname "$match_file")"
fi
