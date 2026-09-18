# Installs the reporting-agent skill and its subagents into a target
# project's .opencode/ and .omp/ directories (the paths opencode/omp
# actually discover skills and agents from). Only ever touches the
# reporting-agent files themselves -- it never deletes or overwrites
# anything else already in the target.
param(
    [string]$Target = "."
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

New-Item -ItemType Directory -Force -Path $Target | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Target ".opencode\skills") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Target ".opencode\agents") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Target ".omp\agents") | Out-Null

$SkillDest = Join-Path $Target ".opencode\skills\reporting-agent"
if (Test-Path $SkillDest) {
    Remove-Item -Recurse -Force $SkillDest
}
New-Item -ItemType Directory -Force -Path $SkillDest | Out-Null
Copy-Item -Path (Join-Path $ScriptDir "SKILL.md") -Destination (Join-Path $SkillDest "SKILL.md") -Force
Copy-Item -Path (Join-Path $ScriptDir "reference") -Destination (Join-Path $SkillDest "reference") -Recurse -Force
Copy-Item -Path (Join-Path $ScriptDir "templates") -Destination (Join-Path $SkillDest "templates") -Recurse -Force
Copy-Item -Path (Join-Path $ScriptDir "scripts") -Destination (Join-Path $SkillDest "scripts") -Recurse -Force

Copy-Item -Path (Join-Path $ScriptDir "agents\opencode\reporting-writer.md") -Destination (Join-Path $Target ".opencode\agents\reporting-writer.md") -Force
Copy-Item -Path (Join-Path $ScriptDir "agents\opencode\reporting-editor.md") -Destination (Join-Path $Target ".opencode\agents\reporting-editor.md") -Force
Copy-Item -Path (Join-Path $ScriptDir "agents\omp\reporting-writer.md") -Destination (Join-Path $Target ".omp\agents\reporting-writer.md") -Force
Copy-Item -Path (Join-Path $ScriptDir "agents\omp\reporting-editor.md") -Destination (Join-Path $Target ".omp\agents\reporting-editor.md") -Force

$Resolved = (Resolve-Path $Target).Path
Write-Host "Installed reporting-agent into: $Resolved"
Write-Host "  .opencode\skills\reporting-agent\"
Write-Host "  .opencode\agents\reporting-writer.md, reporting-editor.md"
Write-Host "  .omp\agents\reporting-writer.md, reporting-editor.md"
