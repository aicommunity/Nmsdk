param([Parameter(Mandatory=$true)][string]$ToolRoot,
      [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{40}$')][string]$ToolCommit,
      [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{40}$')][string]$SpecificationBlob,
      [Parameter(Mandatory=$true)][ValidatePattern('^[a-z0-9-]+$')][string]$Attempt,
      [ValidateSet('sdk-build.py','audit-closed-build.py','validate-native.py')][string]$WorkerName='sdk-build.py')
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
Import-Module (Join-Path $PSScriptRoot 'GitPreparation.psm1') -Force
$base='C:/Projects/TimeLearnerWorker'
$root=[IO.Path]::GetFullPath($ToolRoot)
if(-not $root.StartsWith('C:\Projects\TimeLearnerWorker\',[StringComparison]::OrdinalIgnoreCase)) {
    throw 'Tool source must be in private worker workspace'
}
if(((Invoke-CheckedGit @('-C',$root,'rev-parse','HEAD')) -join '') -ne $ToolCommit) {throw 'Tool HEAD differs'}
$raw=(Invoke-CheckedGit @('-C',$root,'cat-file','blob',$SpecificationBlob)) -join "`n"
$spec=ConvertFrom-Json -InputObject $raw
$worker=Join-Path $PSScriptRoot $WorkerName
if((Get-FileHash -LiteralPath $worker -Algorithm SHA256).Hash.ToLowerInvariant() -ne $spec.worker_sha256) {
    throw 'Worker content differs'
}
$python=$base+'/downloads/tools/python/python-3.14.2-x64-1/python.exe'
if((Get-FileHash -LiteralPath $python -Algorithm SHA256).Hash.ToLowerInvariant() -ne
    'fda7026477256845afab371e354c4d512896665f1761939cb5887d0a9dec257a') {throw 'Python content differs'}
$control=$base+'/requests/'+$Attempt
if(Test-Path -LiteralPath $control){throw 'Attempt control already exists'}
if(Test-Path -LiteralPath $spec.output_root){throw 'Attempt output already exists'}
$scheduler=New-Object -ComObject Schedule.Service
$scheduler.Connect();$folder=$scheduler.GetFolder('\');$name='TimeLearner-'+$Attempt
foreach($task in $folder.GetTasks(0)) {
    if($task.Name -eq $name){throw 'Scheduled attempt already exists'}
    if($task.Name -like 'TimeLearner-*' -and $task.GetInstances(0).Count -gt 0) {
        throw ('Prior TimeLearner task active: '+$task.Name)
    }
}
$null=New-Item -ItemType Directory -Path $control
$utf8=[Text.UTF8Encoding]::new($false)
$specFile=$control+'/specification.json'
[IO.File]::WriteAllText($specFile,$raw+"`n",$utf8)
$batch=$control+'/launch.cmd'
$line='"'+$python+'" -B -X utf8 "'+$worker+'" --specification "'+$specFile+'" 1>"'+$control+'/stdout.log" 2>"'+$control+'/stderr.log"'
[IO.File]::WriteAllText($batch,"@echo off`r`n"+$line+"`r`nexit /b %errorlevel%`r`n",[Text.Encoding]::ASCII)
$definition=$scheduler.NewTask(0)
$user=[Security.Principal.WindowsIdentity]::GetCurrent().Name
$definition.Principal.UserId=$user;$definition.Principal.LogonType=2;$definition.Principal.RunLevel=0
$definition.Settings.Enabled=$true;$definition.Settings.AllowDemandStart=$true
$definition.Settings.ExecutionTimeLimit='PT3H';$definition.Settings.MultipleInstances=2
$definition.Settings.DisallowStartIfOnBatteries=$false;$definition.Settings.StopIfGoingOnBatteries=$false
$action=$definition.Actions.Create(0)
$action.Path='C:\Windows\System32\cmd.exe';$action.Arguments='/d /c "'+$batch+'"';$action.WorkingDirectory=$base
$registered=$folder.RegisterTaskDefinition($name,$definition,2,$user,$null,2,$null)
[IO.File]::WriteAllText($control+'/task.xml',$registered.Xml,$utf8)
$instance=$registered.Run($null)
$receipt=@{kind=$(switch($WorkerName){'sdk-build.py'{'windows_sdk_build_dispatch'};'audit-closed-build.py'{'windows_closed_build_audit_dispatch'};default{'windows_native_validation_dispatch'}});task=$name;instance=$instance.InstanceGuid;
    tool_commit=$ToolCommit;specification_git_blob=$SpecificationBlob;worker_sha256=$spec.worker_sha256;
    scientific_verdict=$null;output=$spec.output_root}
[IO.File]::WriteAllText($control+'/dispatch.json',($receipt|ConvertTo-Json -Depth 5)+"`n",$utf8)
$receipt|ConvertTo-Json -Depth 5
