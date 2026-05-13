#!/usr/bin/env bats

SHIM="${BATS_TEST_DIRNAME}/pipx"

@test "suggests uv tool install" {
  run "$SHIM" install ruff
  [[ $status -ne 0 ]]
  [[ "$output" == *"uv tool install"* ]]
}

@test "suggests uvx" {
  run "$SHIM" run ruff
  [[ $status -ne 0 ]]
  [[ "$output" == *"uvx"* ]]
}

@test "suggests uv tool list" {
  run "$SHIM" list
  [[ $status -ne 0 ]]
  [[ "$output" == *"uv tool list"* ]]
}
