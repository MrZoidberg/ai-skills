#!/usr/bin/env bats

SHIM="${BATS_TEST_DIRNAME}/uv"

setup() {
  command -v uv &>/dev/null || skip "uv not available"
}

@test "exits non-zero for uv pip install" {
  run "$SHIM" pip install requests
  [[ $status -ne 0 ]]
  [[ "$output" == *"uv add"* ]]
}

@test "exits non-zero for uv pip sync" {
  run "$SHIM" pip sync
  [[ $status -ne 0 ]]
  [[ "$output" == *"uv sync"* ]]
}

@test "passes through to real uv for non-pip subcommands" {
  run "$SHIM" --version
  [[ $status -eq 0 ]]
  [[ "$output" == *"uv"* ]]
}
