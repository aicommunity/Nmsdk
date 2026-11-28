[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{40}$')][string]$RootCommit,
    [string]$WaitForAttemptId = 'stabilized-bursts-2363ab16-01'
)
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
if($env:COMPUTERNAME -ne 'AQUA3060'){throw 'Server .15 is required'}
$data='E:\Nmsdk-AxoneTimeLearner-Data'
$short=$RootCommit.Substring(0,8)
$sdk="C:\Projects\nmsdk-axone-sdks\$short"
$build="C:\Projects\nmsdk-axone-builds\$short-release-01"
$runtime="$data\Runtime\$short-release-01"
$python='C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe'
$initializer='C:\Projects\nmsdk-axone-control\Initialize-Server15-922da286.ps1'
$seal='C:\Projects\nmsdk-axone-control\Seal-Server15Attempt-conduction-v4.py'
$archive='7d37d9df-beda-4bdd-9cc2-7068e364f154'
if((Get-FileHash -LiteralPath $initializer -Algorithm SHA256).Hash -ne '3B970F9C58A351A122BB5C64154D56804E59A2418DD9A93BD04E68FEC97AC43D'){throw 'Initializer changed'}
if((Get-FileHash -LiteralPath $seal -Algorithm SHA256).Hash -ne '272750CB2550ED30C7339AE5E75B776D56314B95EBD17CC59EC8030DB66B03E4'){throw 'Archive adapter changed'}
if($WaitForAttemptId){
    if($WaitForAttemptId -notmatch '^[a-z0-9-]+$'){throw 'Invalid prerequisite identity'}
    $deadline=[DateTime]::UtcNow.AddHours(2)
    while(!(Test-Path -LiteralPath "$data\NativeChecks\$WaitForAttemptId\result.json")){
        if([DateTime]::UtcNow -gt $deadline){throw 'Prerequisite native gate has not closed'}
        Start-Sleep -Seconds 5
    }
}
$env:PATH='C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd;C:\Windows\System32\WindowsPowerShell\v1.0;C:\Windows\System32;C:\Windows'
$setup="$data\Setup\prepare-$short-01"
& $initializer -RootCommit $RootCommit -CloneRoot $sdk -EvidenceRoot $setup -ExpectedVolumeSerial 'CC129017'
if($LASTEXITCODE){throw 'Source initialization failed'}
Copy-Item -LiteralPath $PSCommandPath -Destination "$setup\controller-producer.ps1" -ErrorAction Stop
@{kind='axone_terminal_controller_validation_invocation';schema_version=1;root_commit=$RootCommit;
  prerequisite=$WaitForAttemptId;producer_sha256=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash;
  data_root=$data;source_root=$sdk;runtime=$runtime;build=$build;started_utc=[DateTime]::UtcNow.ToString('o')} |
  ConvertTo-Json | Set-Content -LiteralPath "$setup\controller-invocation.json" -Encoding UTF8
& "$sdk\Scripts\StructTrain\AxoneTimeLearner\Build-Server15.ps1" -Action all `
  -VcpkgRoot 'C:\Projects\vcpkg-5cad' -QtRoot 'C:\Qt\5.15.2\msvc2019_64' `
  -CMakeExecutable 'C:\Qt\Tools\CMake_64\bin\cmake.exe' -NinjaExecutable 'C:\Qt\Tools\Ninja\ninja.exe' `
  -BuildRoot $build -RuntimeRoot $runtime -DependencyRoot 'C:\Projects\nmsdk-axone-deps\v143-5cad-localqt-tests' `
  -EvidenceRoot "$data\Builds\build-$short-01" -PythonExecutable $python -Jobs 6
if($LASTEXITCODE){throw 'Build failed; preserve this attempt before a fresh correction'}
$attempts=@(@{id="prepare-$short-01";folder='Setup';role='setup'},@{id="build-$short-01";folder='Builds';role='build'})
$failed=@()
function Gate([string]$id,[string]$protocol,[string]$partition='all',[string]$case=''){
    $arguments=@('-I','-S','-B',"$sdk\Scripts\StructTrain\AxoneTimeLearner\Run-Server15NativeGate.py",
      '--source-root',$sdk,'--runtime',$runtime,'--cache',"$build\CMakeCache.txt",'--protocol',
      "$sdk\Bin\Configs\SpikeSamples\StructTrain\AxoneTimeLearner\protocols\$protocol",'--data-root',$data,
      '--output',"$data\NativeChecks\$id",'--archive-id',$archive,'--expected-root-commit',$RootCommit,
      '--partition',$partition,'--wall-seconds','1800','--memory-bytes','2147483648')
    if($case){$arguments+=@('--case-id',$case)}
    & $python @arguments
    $script:attempts+=@{id=$id;folder='NativeChecks';role='native'}
    if($LASTEXITCODE){$script:failed+=$id}
}
$snapshotCases=@('TreeNativeSnapshotPreservesPortsParametersAndActualWaveforms',
  'TreeSnapshotRejectsWrongEnvelopeAndUnknownFields',
  'TreeSnapshotRejectsGraphMismatchAfterEnvelopeDigestIsRecomputed',
  'TreeSnapshotKeepsAxonalAndNeuronSnapshotTypesSeparate')
$index=0
foreach($name in $snapshotCases){$index++;Gate "tree-snapshot$index-$short-01" 'P1-native-contracts-v7.json' 'lifecycle' "AxoneLifecycle.$name"}
Gate "terminal-controller-smoke-$short-01" 'P2-terminal-controller-v2.json' 'all' 'AxoneTimeLearner.ManagedTerminalAlignmentRequiresFreshVerification'
Gate "terminal-controller-$short-01" 'P2-terminal-controller-v2.json'
foreach($attempt in $attempts){
    & $python -I -S -B $seal --data-root $data --archive-id $archive --attempt "$data\$($attempt.folder)\$($attempt.id)" --role $attempt.role --seal-id $attempt.id
    if($LASTEXITCODE){throw "Sealing failed: $($attempt.id)"}
    & $python -I -S -B $seal --data-root $data --archive-id $archive --verify-pointer "$data\Seals\$($attempt.id)\pointer.archive.json"
    if($LASTEXITCODE){throw "Readback failed: $($attempt.id)"}
}
if($failed.Count){throw ('Native failures preserved: '+($failed -join ', '))}
