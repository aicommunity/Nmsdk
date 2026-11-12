# Copy non-Qt runtime DLLs from vcpkg_installed to Bin\Platform\Win.
# Qt DLLs are not copied (they are supplied from C:\Qt).
# Usage: run from repo root, or pass -RepoRoot; optionally -VcpkgBinDir and -DestDir.

param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$VcpkgBinDir = "",
    [string]$DestDir = ""
)

$ErrorActionPreference = "Stop"

if (-not $VcpkgBinDir) {
    $VcpkgBinDir = Join-Path $RepoRoot "build\vcpkg_installed\x64-windows\bin"
}
if (-not $DestDir) {
    $DestDir = Join-Path $RepoRoot "Bin\Platform\Win"
}

if (-not (Test-Path -LiteralPath $VcpkgBinDir -PathType Container)) {
    Write-Error "vcpkg bin directory not found: $VcpkgBinDir"
}

if (-not (Test-Path -LiteralPath $DestDir -PathType Container)) {
    New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
}

$count = 0
Get-ChildItem -Path $VcpkgBinDir -Filter "*.dll" -File | ForEach-Object {
    $name = $_.Name
    # Skip debug DLLs (suffix d.dll or _d.dll)
    if ($name -match 'd\.dll$' -or $name -match '_d\.dll$') { return }
    # Skip Qt DLLs (supplied from C:\Qt)
    if ($name -match '^Qt') { return }
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $DestDir $name) -Force
    $script:count++
}

Write-Host "Copied $count non-Qt DLL(s) to $DestDir"
