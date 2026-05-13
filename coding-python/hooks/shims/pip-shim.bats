#!/usr/bin/env bats

SHIM="${BATS_TEST_DIRNAME}/pip"

@test "suggests uv add for pip install" {
  run "$SHIM" install requests
  [[ $status -ne 0 ]]
  [[ "$output" == *"uv add"* ]]
}

@test "suggests uv remove for pip uninstall" {
  run "$SHIM" uninstall requests
  [[ $status -ne 0 ]]
  [[ "$output" == *"uv remove"* ]]
}

@test "suggests uv export for pip freeze" {
  run "$SHIM" freeze
  [[ $status -ne 0 ]]
  [[ "$output" == *"uv export"* ]]
}
