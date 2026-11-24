[CmdletBinding()]
param([int]$Jobs=4,[switch]$Configure)
$ErrorActionPreference='Stop'
$taskRepo=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$taskPreviousVcpkg=$env:VCPKG_ROOT
$taskSources=@('Scripts/ClassicStructTrain/replay.cpp','Scripts/ClassicStructTrain/legacy_replay.inc','Scripts/ClassicStructTrain/training_replay.inc')
if((Get-Content -LiteralPath (Join-Path $taskRepo 'Scripts/ClassicStructTrain/replay.cpp') -Raw).Contains('#include "training_file_protocol.inc"')){$taskSources+='Scripts/ClassicStructTrain/training_file_protocol.inc'}
$taskBefore=@{}
foreach($taskSource in $taskSources){$taskBefore[$taskSource]=(Get-FileHash -LiteralPath (Join-Path $taskRepo $taskSource) -Algorithm SHA256).Hash}
$taskPulseBefore=git -C (Join-Path $taskRepo 'Libraries/Nmsdk-PulseLib') rev-parse HEAD
$taskRdkBefore=git -C (Join-Path $taskRepo 'Rdk') rev-parse HEAD
try {
 $env:VCPKG_ROOT=Join-Path $taskRepo '.deps\vcpkg-tool'
 $taskAction=if($Configure){'all'}else{'build'}
 & (Join-Path $taskRepo 'Scripts\Build-Windows.ps1') -Action $taskAction -Preset 'win-vs2022-ninja-release-localqt' -QtRoot 'C:\Qt\5.15.2\msvc2019_64' -WithTests -Targets @('ClassicTrainingRepro') -Jobs $Jobs -ExtraCMakeArgs @('-UZ_VCPKG_ROOT_DIR', ('-DNMSDK_CLASSIC_RUNTIME_DIR='+ (Join-Path $taskRepo 'Bin\Platform\Win').Replace('\','/')))
 if($LASTEXITCODE){throw 'Release training replay build failed'}
 foreach($taskSource in $taskSources){if((Get-FileHash -LiteralPath (Join-Path $taskRepo $taskSource) -Algorithm SHA256).Hash -ne $taskBefore[$taskSource]){throw 'Native controller sources changed during the build'}}
 if((git -C (Join-Path $taskRepo 'Libraries/Nmsdk-PulseLib') rev-parse HEAD) -ne $taskPulseBefore -or (git -C (Join-Path $taskRepo 'Rdk') rev-parse HEAD) -ne $taskRdkBefore){throw 'Native module revision changed during the build'}
 $taskBuildRecord=[ordered]@{sources=$taskBefore;pulselib_sha=$taskPulseBefore;rdk_sha=$taskRdkBefore;binary_sha256=(Get-FileHash -LiteralPath (Join-Path $taskRepo 'Bin/Platform/Win/ClassicTrainingRepro.exe') -Algorithm SHA256).Hash;source_stability_verified=$true}
 $taskBuildRecord | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskRepo 'Reports/StructTrainClassic/_work/TrainingReproducibility-20261123/last-build.json') -Encoding utf8
} finally {
 if($null -eq $taskPreviousVcpkg){Remove-Item Env:VCPKG_ROOT -ErrorAction SilentlyContinue}else{$env:VCPKG_ROOT=$taskPreviousVcpkg}
}
