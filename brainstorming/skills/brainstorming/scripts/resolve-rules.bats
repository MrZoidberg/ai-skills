#!/usr/bin/env bats

setup() {
  SCRIPT="$BATS_TEST_DIRNAME/resolve-rules.py"
  PY="$(command -v python3 || command -v python)"
  TMP="$(mktemp -d)"
  PROJECT="$TMP/project"
  DATA="$TMP/data"
  mkdir -p "$PROJECT/.agents" "$DATA"
  unset CODEX_PLUGIN_DATA COPILOT_PLUGIN_DATA CLAUDE_PLUGIN_DATA PLUGIN_DATA
}

teardown() {
  rm -rf "$TMP"
}

run_resolve() {
  cd "$PROJECT" && run "$PY" "$SCRIPT" "$@"
}

@test "no rules files anywhere: empty output, exit 0" {
  run_resolve brainstorm-rules.md "$DATA"
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

@test "project rules only" {
  echo "project rules" >"$PROJECT/.agents/brainstorm-rules.md"
  run_resolve brainstorm-rules.md "$DATA"
  [ "$status" -eq 0 ]
  [ "$output" = "project rules" ]
}

@test "user rules only" {
  echo "user rules" >"$DATA/brainstorm-rules.md"
  run_resolve brainstorm-rules.md "$DATA"
  [ "$status" -eq 0 ]
  [ "$output" = "user rules" ]
}

@test "project wins over user, never merged" {
  echo "project rules" >"$PROJECT/.agents/brainstorm-rules.md"
  echo "user rules" >"$DATA/brainstorm-rules.md"
  run_resolve brainstorm-rules.md "$DATA"
  [ "$status" -eq 0 ]
  [ "$output" = "project rules" ]
}

@test "empty project file falls through to user" {
  : >"$PROJECT/.agents/brainstorm-rules.md"
  echo "user rules" >"$DATA/brainstorm-rules.md"
  run_resolve brainstorm-rules.md "$DATA"
  [ "$status" -eq 0 ]
  [ "$output" = "user rules" ]
}

@test "whitespace-only project file falls through to user" {
  printf '   \n\t\n' >"$PROJECT/.agents/brainstorm-rules.md"
  echo "user rules" >"$DATA/brainstorm-rules.md"
  run_resolve brainstorm-rules.md "$DATA"
  [ "$status" -eq 0 ]
  [ "$output" = "user rules" ]
}

@test "data dir falls back to CODEX_PLUGIN_DATA when no argument given" {
  echo "user rules" >"$DATA/brainstorm-rules.md"
  export CODEX_PLUGIN_DATA="$DATA"
  run_resolve brainstorm-rules.md
  [ "$status" -eq 0 ]
  [ "$output" = "user rules" ]
}

@test "data dir falls back to PLUGIN_DATA when no argument given" {
  echo "user rules" >"$DATA/brainstorm-rules.md"
  export PLUGIN_DATA="$DATA"
  run_resolve brainstorm-rules.md
  [ "$status" -eq 0 ]
  [ "$output" = "user rules" ]
}

@test "missing filename argument exits 0 with no output" {
  run_resolve
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

@test "nonexistent data dir is harmless" {
  run_resolve brainstorm-rules.md "$TMP/does-not-exist"
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

@test "--source reports project" {
  echo "project rules" >"$PROJECT/.agents/brainstorm-rules.md"
  run_resolve brainstorm-rules.md "$DATA" --source
  [ "$status" -eq 0 ]
  [ "$output" = "project" ]
}

@test "--source reports user" {
  echo "user rules" >"$DATA/brainstorm-rules.md"
  run_resolve brainstorm-rules.md "$DATA" --source
  [ "$status" -eq 0 ]
  [ "$output" = "user" ]
}

@test "--source reports none" {
  run_resolve brainstorm-rules.md "$DATA" --source
  [ "$status" -eq 0 ]
  [ "$output" = "none" ]
}

@test "multi-line content is passed through verbatim" {
  printf '## a\n- one\n- two\n' >"$PROJECT/.agents/brainstorm-rules.md"
  run_resolve brainstorm-rules.md "$DATA"
  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "## a" ]
  [ "${lines[1]}" = "- one" ]
  [ "${lines[2]}" = "- two" ]
}

@test "a directory in place of the rules file still exits 0" {
  mkdir -p "$PROJECT/.agents/brainstorm-rules.md"
  run_resolve brainstorm-rules.md "$DATA"
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}
