#!/usr/bin/env bash
set -euo pipefail

# SessionStart hook: prepend shims directory to PATH so bare python/pip/pipx
# and legacy uv-pip invocations are intercepted with uv suggestions.
#
# uv run is unaffected because it prepends its managed virtualenv bin/ to PATH,
# shadowing these shims.

command -v uv &>/dev/null || exit 0

env_file="${CODEX_ENV_FILE:-${CLAUDE_ENV_FILE:-}}"
if [[ -z "$env_file" ]]; then
  echo "coding-python: no hook environment file set; shims will not be installed" >&2
  exit 0
fi

shims_dir="$(cd "$(dirname "$0")/shims" && pwd)" || {
  echo "coding-python: shims directory not found" >&2
  exit 1
}

echo "export PATH=\"${shims_dir}:\${PATH}\"" >>"$env_file"
