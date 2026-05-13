#!/usr/bin/env bats

SETUP_SCRIPT="${BATS_TEST_DIRNAME}/setup-shims.sh"

setup() {
  export CODEX_ENV_FILE
  CODEX_ENV_FILE="$(mktemp)"
  FAKE_BIN="$(mktemp -d)"
  echo '#!/usr/bin/env bash' >"$FAKE_BIN/uv"
  chmod +x "$FAKE_BIN/uv"
  export FAKE_BIN
  export ORIG_PATH="$PATH"
}

teardown() {
  rm -f "$CODEX_ENV_FILE"
  rm -rf "$FAKE_BIN"
}

@test "exits silently when no env file is set" {
  run env -u CODEX_ENV_FILE -u CLAUDE_ENV_FILE PATH="${FAKE_BIN}:${ORIG_PATH}" bash "$SETUP_SCRIPT"
  [[ $status -eq 0 ]]
}

@test "exits silently when uv is not available" {
  local path_without_uv=""
  local IFS=:
  for dir in $ORIG_PATH; do
    [[ "$dir" == "$FAKE_BIN" ]] && continue
    [[ -x "$dir/uv" ]] && continue
    path_without_uv="${path_without_uv:+${path_without_uv}:}$dir"
  done

  run env PATH="$path_without_uv" CODEX_ENV_FILE="$CODEX_ENV_FILE" bash "$SETUP_SCRIPT"
  [[ $status -eq 0 ]]
  [[ ! -s "$CODEX_ENV_FILE" ]]
}

@test "writes PATH export to CODEX_ENV_FILE" {
  run env PATH="${FAKE_BIN}:${ORIG_PATH}" bash "$SETUP_SCRIPT"
  [[ $status -eq 0 ]]
  grep -q 'export PATH=' "$CODEX_ENV_FILE"
}

@test "supports CLAUDE_ENV_FILE fallback" {
  local claude_env_file
  claude_env_file="$(mktemp)"
  run env -u CODEX_ENV_FILE CLAUDE_ENV_FILE="$claude_env_file" PATH="${FAKE_BIN}:${ORIG_PATH}" bash "$SETUP_SCRIPT"
  [[ $status -eq 0 ]]
  grep -q 'export PATH=' "$claude_env_file"
  rm -f "$claude_env_file"
}
