[CmdletBinding()]
param(
  [string]$QtRoot = 'C:\Qt\5.15.2\msvc2019_64',
  [string]$Preset = 'win-vs2022-ninja-release-localqt',
  [string]$VcpkgRoot = '',
  [int]$Jobs = 4
)
$ErrorActionPreference = 'Stop'
if ($Preset -notmatch '-release-') { throw 'Classic experiments must use Release; Debug is not allowed for these runs.' }
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
if (!$VcpkgRoot) { $VcpkgRoot = Join-Path $repoRoot '.deps\vcpkg-tool' }
if (!(Test-Path -LiteralPath (Join-Path $VcpkgRoot 'vcpkg.exe'))) {
  throw 'Provide a bootstrapped vcpkg checkout containing the manifest baseline and its matching versions database. See README.txt.'
}
$previousVcpkg = $env:VCPKG_ROOT
try {
  $env:VCPKG_ROOT = (Resolve-Path -LiteralPath $VcpkgRoot).Path
  $classicRuntime = (Join-Path $repoRoot 'Bin\Platform\Win').Replace('\','/')
  & (Join-Path $repoRoot 'Scripts\Build-Windows.ps1') -Preset $Preset -QtRoot $QtRoot -WithTests `
    -Targets @('NeuroModelerConsole','ClassicStructTrainReplay','Test_PulseLib_StorageComponents') `
    -Jobs $Jobs -ExtraCMakeArgs @('-UZ_VCPKG_ROOT_DIR', "-DNMSDK_CLASSIC_RUNTIME_DIR=$classicRuntime")
  if ($LASTEXITCODE) { throw "Classic replay build failed ($LASTEXITCODE)" }
} finally {
  if ($null -eq $previousVcpkg) { Remove-Item Env:VCPKG_ROOT -ErrorAction SilentlyContinue }
  else { $env:VCPKG_ROOT = $previousVcpkg }
}
