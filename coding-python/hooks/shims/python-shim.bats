#!/usr/bin/env bats

SHIM="${BATS_TEST_DIRNAME}/python"

@test "blocks bare python" {
  run "$SHIM" script.py
  [[ $status -ne 0 ]]
  [[ "$output" == *"uv run python"* ]]
}

@test "blocks python -m pip" {
  run "$SHIM" -m pip install requests
  [[ $status -ne 0 ]]
  [[ "$output" == *"uv add"* ]]
}

@test "suggests uv run for modules" {
  run "$SHIM" -m pytest
  [[ $status -ne 0 ]]
  [[ "$output" == *"uv run python -m pytest"* ]]
}
