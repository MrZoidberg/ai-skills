#requires -Version 5.1

<##
AI Skills installer (Windows / PowerShell)

Usage:
  powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $s = irm https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.ps1; iex $s; Install-AiSkill -Skill coding-python -System copilot -Scope user -Yes }"

Or download + run:
  irm https://raw.githubusercontent.com/MrZoidberg/ai-skills/master/install.ps1 -OutFile install.ps1
  .\install.ps1 -Skill coding-python -System copilot -Scope user -Yes

This script clones/pulls the repo via git, then installs the chosen skill as a Junction.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory = $false)]
  [string]$Skill,

  [Parameter(Mandatory = $false)]
  [ValidateSet('codex', 'copilot', 'claude', 'claude-code', 'antigravity')]
  [string]$System,

  [Parameter(Mandatory = $false)]
  [ValidateSet('user', 'project', 'system', 'repo')]
  [string]$Scope,

  [Parameter(Mandatory = $false)]
  [string]$RepoRoot,

  [Parameter(Mandatory = $false)]
  [string]$SourceRepo = 'https://github.com/MrZoidberg/ai-skills.git',

  [Parameter(Mandatory = $false)]
  [string]$Branch = 'master',

  [Parameter(Mandatory = $false)]
  [switch]$Yes
)

function Assert-Command([string]$Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Missing required command: $Name"
  }
}

function Prompt-IfMissing([string]$Name, [string]$Prompt, [switch]$NonInteractive) {
  $value = Get-Variable -Name $Name -ValueOnly -ErrorAction SilentlyContinue
  if ($value) { return }
  if ($NonInteractive) { throw "Missing required option: $Name" }
  $input = Read-Host $Prompt
  if (-not $input) { throw "Empty input for $Name" }
  Set-Variable -Name $Name -Value $input -Scope Script
}

function Get-RepoRootOrPwd() {
  try {
    $root = git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -eq 0 -and $root) { return $root.Trim() }
  } catch {}
  return (Get-Location).Path
}

function Install-AiSkill {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $false)]
    [string]$Skill,

    [Parameter(Mandatory = $false)]
    [ValidateSet('codex', 'copilot', 'claude', 'claude-code', 'antigravity')]
    [string]$System,

    [Parameter(Mandatory = $false)]
    [ValidateSet('user', 'project', 'system', 'repo')]
    [string]$Scope,

    [Parameter(Mandatory = $false)]
    [string]$RepoRoot,

    [Parameter(Mandatory = $false)]
    [string]$SourceRepo = 'https://github.com/MrZoidberg/ai-skills.git',

    [Parameter(Mandatory = $false)]
    [string]$Branch = 'master',

    [Parameter(Mandatory = $false)]
    [switch]$Yes
  )

  Set-StrictMode -Version Latest
  $ErrorActionPreference = 'Stop'

  Prompt-IfMissing -Name Skill -Prompt 'Skill (e.g. coding-python)' -NonInteractive:$Yes
  Prompt-IfMissing -Name System -Prompt 'System (codex/copilot/claude/antigravity)' -NonInteractive:$Yes
  Prompt-IfMissing -Name Scope -Prompt 'Scope (system/repo) or (user/project)' -NonInteractive:$Yes

  if ($System -eq 'claude-code') { $System = 'claude' }
  if ($Scope -eq 'system') { $Scope = 'user' }
  if ($Scope -eq 'repo') { $Scope = 'project' }

  Assert-Command git

  if (-not $RepoRoot -and $Scope -eq 'project') {
    $RepoRoot = Get-RepoRootOrPwd
  }

  $dataHome = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } elseif ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { Join-Path $env:USERPROFILE '.local\share' }
  $srcDir = Join-Path $dataHome 'agent-skills\ai-skills'

  New-Item -ItemType Directory -Force (Split-Path $srcDir) | Out-Null

  if (-not (Test-Path (Join-Path $srcDir '.git'))) {
    git clone --depth 1 --branch $Branch $SourceRepo $srcDir | Out-Null
  } else {
    git -C $srcDir pull --ff-only | Out-Null
  }

  $skillSrc = Join-Path $srcDir $Skill
  if (-not (Test-Path (Join-Path $skillSrc 'SKILL.md'))) {
    throw "Skill not found in source repo: $skillSrc (expected SKILL.md)"
  }

  $destRoot = switch ("$System:$Scope") {
    'codex:user' { Join-Path $env:USERPROFILE '.agents\skills' }
    'codex:project' { Join-Path $RepoRoot '.agents\skills' }
    'copilot:user' { Join-Path $env:USERPROFILE '.copilot\skills' }
    'copilot:project' { Join-Path $RepoRoot '.github\skills' }
    'claude:user' { Join-Path $env:USERPROFILE '.claude\skills' }
    'claude:project' { Join-Path $RepoRoot '.claude\skills' }
    'antigravity:user' { Join-Path $env:USERPROFILE '.agents\skills' }
    'antigravity:project' { Join-Path $RepoRoot '.agents\skills' }
    default { throw "Unsupported combination: $System / $Scope" }
  }

  New-Item -ItemType Directory -Force $destRoot | Out-Null

  $dest = Join-Path $destRoot $Skill
  if (Test-Path $dest) {
    Remove-Item $dest -Recurse -Force
  }

  New-Item -ItemType Junction -Path $dest -Target $skillSrc | Out-Null

  Write-Host "Installed '$Skill' for $System ($Scope) -> $dest"
  Write-Host "Source: https://github.com/MrZoidberg/ai-skills/tree/master/$Skill"
}

# If invoked as a script (not dot-sourced), run once using passed parameters.
if ($MyInvocation.InvocationName -ne '.') {
  try {
    Install-AiSkill @PSBoundParameters
  } catch {
    Write-Error $_
    exit 1
  }
}
