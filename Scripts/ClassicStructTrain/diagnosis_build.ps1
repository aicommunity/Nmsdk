[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Variant,
    [Parameter(Mandatory)] [string] $Python
)
$ErrorActionPreference = 'Stop'
$repository = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$previousVcpkg = $env:VCPKG_ROOT
try {
    $env:VCPKG_ROOT = Join-Path $repository '.deps\vcpkg-tool'
    & (Join-Path $repository 'Scripts\Build-Windows.ps1') -Action build -Preset 'win-vs2022-ninja-release-localqt' `
        -QtRoot 'C:\Qt\5.15.2\msvc2019_64' -WithTests -Targets ClassicTrainingRepro -Jobs 4
    if ($LASTEXITCODE -ne 0) { throw "Release build failed for $Variant" }
    & $Python -I -B -X utf8 (Join-Path $PSScriptRoot 'diagnosis_run.py') package --variant $Variant
    if ($LASTEXITCODE -ne 0) { throw "Packaging failed for $Variant" }
} finally {
    $env:VCPKG_ROOT = $previousVcpkg
}
