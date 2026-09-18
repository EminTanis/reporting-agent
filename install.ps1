# Installs the reporting-agent skill and its subagents into a target
# project. Only ever touches the reporting-agent files themselves -- it
# never deletes or overwrites anything else already in the target.
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
Copy-Item -Path (Join-Path $ScriptDir ".opencode\skills\reporting-agent") -Destination $SkillDest -Recurse -Force

Copy-Item -Path (Join-Path $ScriptDir ".opencode\agents\reporting-writer.md") -Destination (Join-Path $Target ".opencode\agents\reporting-writer.md") -Force
Copy-Item -Path (Join-Path $ScriptDir ".opencode\agents\reporting-editor.md") -Destination (Join-Path $Target ".opencode\agents\reporting-editor.md") -Force
Copy-Item -Path (Join-Path $ScriptDir ".omp\agents\reporting-writer.md") -Destination (Join-Path $Target ".omp\agents\reporting-writer.md") -Force
Copy-Item -Path (Join-Path $ScriptDir ".omp\agents\reporting-editor.md") -Destination (Join-Path $Target ".omp\agents\reporting-editor.md") -Force

$Resolved = (Resolve-Path $Target).Path
Write-Host "Installed reporting-agent into: $Resolved"
Write-Host "  .opencode\skills\reporting-agent\"
Write-Host "  .opencode\agents\reporting-writer.md, reporting-editor.md"
Write-Host "  .omp\agents\reporting-writer.md, reporting-editor.md"
