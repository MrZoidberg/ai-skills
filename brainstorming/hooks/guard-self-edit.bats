#!/usr/bin/env bats

setup() {
  GUARD="$BATS_TEST_DIRNAME/guard-self-edit.py"
  PY="$(command -v python3 || command -v python)"
  TMP="$(mktemp -d)"
  ROOT="$TMP/installed/brainstorming"
  DATA="$TMP/plugin-data"
  WORK="$TMP/workspace"
  mkdir -p "$ROOT/skills/brainstorming" "$ROOT/hooks" "$DATA" "$WORK/.agents"
  unset BRAINSTORM_ALLOW_SELF_EDIT
  unset CODEX_PLUGIN_ROOT COPILOT_PLUGIN_ROOT CLAUDE_PLUGIN_ROOT PLUGIN_ROOT
  unset CODEX_PLUGIN_DATA COPILOT_PLUGIN_DATA CLAUDE_PLUGIN_DATA PLUGIN_DATA
  export CODEX_PLUGIN_ROOT="$ROOT"
  export CODEX_PLUGIN_DATA="$DATA"
}

teardown() {
  rm -rf "$TMP"
}

# guard <json-payload>
guard() {
  run bash -c "printf '%s' \"\$1\" | '$PY' '$GUARD'" _ "$1"
}

payload() {
  local tool="$1" input="$2" cwd="${3:-$WORK}"
  printf '{"hook_event_name":"PreToolUse","tool_name":"%s","cwd":"%s","tool_input":%s}' \
    "$tool" "$cwd" "$input"
}

@test "denies Write to the skill's own SKILL.md" {
  guard "$(payload Write "{\"file_path\":\"$ROOT/skills/brainstorming/SKILL.md\"}")"
  [ "$status" -eq 2 ]
  [[ "$output" == *"self-modification guard"* ]]
}

@test "denies Edit to the plugin manifest" {
  guard "$(payload Edit "{\"file_path\":\"$ROOT/plugin.json\"}")"
  [ "$status" -eq 2 ]
}

@test "denies Write to the guard hook itself" {
  guard "$(payload Write "{\"file_path\":\"$ROOT/hooks/guard-self-edit.py\"}")"
  [ "$status" -eq 2 ]
}

@test "denies a relative path that resolves into the plugin root" {
  guard "$(payload Write '{"file_path":"skills/brainstorming/SKILL.md"}' "$ROOT")"
  [ "$status" -eq 2 ]
}

@test "allows writing project rules in .agents" {
  guard "$(payload Write "{\"file_path\":\"$WORK/.agents/brainstorm-rules.md\"}")"
  [ "$status" -eq 0 ]
}

@test "allows writing user rules in the plugin data dir" {
  guard "$(payload Write "{\"file_path\":\"$DATA/brainstorm-rules.md\"}")"
  [ "$status" -eq 0 ]
}

@test "allows an unrelated file in the workspace" {
  guard "$(payload Write "{\"file_path\":\"$WORK/src/main.go\"}")"
  [ "$status" -eq 0 ]
}

@test "allows a Read of the skill's own files" {
  guard "$(payload Read "{\"file_path\":\"$ROOT/skills/brainstorming/SKILL.md\"}")"
  [ "$status" -eq 0 ]
}

@test "allows a Grep over the skill's own directory" {
  guard "$(payload Grep "{\"path\":\"$ROOT\"}")"
  [ "$status" -eq 0 ]
}

@test "denies a mutating shell command run from inside the plugin root" {
  guard "$(payload Bash '{"command":"echo x > SKILL.md"}' "$ROOT")"
  [ "$status" -eq 2 ]
}

@test "denies a mutating shell command naming the plugin root" {
  guard "$(payload Bash "{\"command\":\"rm -rf $ROOT/skills\"}")"
  [ "$status" -eq 2 ]
}

@test "denies a shell redirect into the plugin root" {
  guard "$(payload Bash "{\"command\":\"echo hi > $ROOT/skills/brainstorming/SKILL.md\"}")"
  [ "$status" -eq 2 ]
}

@test "denies sed -i against the plugin root" {
  guard "$(payload Bash "{\"command\":\"sed -i '' s/a/b/ $ROOT/plugin.json\"}")"
  [ "$status" -eq 2 ]
}

@test "allows a read-only shell command naming the plugin root" {
  guard "$(payload Bash "{\"command\":\"cat $ROOT/plugin.json\"}")"
  [ "$status" -eq 0 ]
}

@test "allows a mutating shell command elsewhere" {
  guard "$(payload Bash "{\"command\":\"rm -rf $WORK/build\"}")"
  [ "$status" -eq 0 ]
}

@test "denies apply_patch touching the plugin root" {
  local patch="*** Begin Patch\n*** Update File: $ROOT/skills/brainstorming/SKILL.md\n*** End Patch"
  guard "$(payload apply_patch "{\"patch\":\"$patch\"}")"
  [ "$status" -eq 2 ]
}

@test "allows apply_patch elsewhere" {
  local patch="*** Begin Patch\n*** Update File: $WORK/src/main.go\n*** End Patch"
  guard "$(payload apply_patch "{\"patch\":\"$patch\"}")"
  [ "$status" -eq 0 ]
}

@test "BRAINSTORM_ALLOW_SELF_EDIT=1 bypasses the guard" {
  export BRAINSTORM_ALLOW_SELF_EDIT=1
  guard "$(payload Write "{\"file_path\":\"$ROOT/skills/brainstorming/SKILL.md\"}")"
  [ "$status" -eq 0 ]
}

@test "BRAINSTORM_ALLOW_SELF_EDIT=0 does not bypass the guard" {
  export BRAINSTORM_ALLOW_SELF_EDIT=0
  guard "$(payload Write "{\"file_path\":\"$ROOT/skills/brainstorming/SKILL.md\"}")"
  [ "$status" -eq 2 ]
}

@test "malformed stdin exits 0 (never fail-closed)" {
  guard "not json at all"
  [ "$status" -eq 0 ]
}

@test "empty stdin exits 0" {
  guard ""
  [ "$status" -eq 0 ]
}

@test "payload without tool_input exits 0" {
  guard '{"hook_event_name":"PreToolUse","tool_name":"Write"}'
  [ "$status" -eq 0 ]
}

@test "camelCase payload keys are understood" {
  guard "{\"toolName\":\"Write\",\"cwd\":\"$WORK\",\"toolArgs\":{\"filePath\":\"$ROOT/plugin.json\"}}"
  [ "$status" -eq 2 ]
}

@test "falls back to COPILOT_PLUGIN_ROOT" {
  unset CODEX_PLUGIN_ROOT
  export COPILOT_PLUGIN_ROOT="$ROOT"
  guard "$(payload Write "{\"file_path\":\"$ROOT/plugin.json\"}")"
  [ "$status" -eq 2 ]
}

@test "falls back to PLUGIN_ROOT" {
  unset CODEX_PLUGIN_ROOT
  export PLUGIN_ROOT="$ROOT"
  guard "$(payload Write "{\"file_path\":\"$ROOT/plugin.json\"}")"
  [ "$status" -eq 2 ]
}

@test "never exits with a code other than 0 or 2" {
  for p in "" "null" "[]" '{"tool_name":null}' '{"tool_input":42}' "not json"; do
    guard "$p"
    [ "$status" -eq 0 ] || [ "$status" -eq 2 ]
  done
}
