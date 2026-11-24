$ErrorActionPreference='Stop'
$taskRepo=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$taskRows=@()
$taskProcesses=Get-CimInstance Win32_Process | Where-Object {
 ($_.Name -eq 'python.exe' -and $_.CommandLine -like '*Scripts/ClassicStructTrain/training_*') -or
 ($_.Name -like 'ClassicTrainingRepro-*.exe' -and $_.CommandLine.StartsWith((Join-Path $taskRepo 'Bin\Platform\Win\')))
}
foreach($taskEntry in $taskProcesses){
 $taskProc=Get-Process -Id $taskEntry.ProcessId -ErrorAction SilentlyContinue
 if($taskProc -and $taskProc.PriorityClass -eq 'BelowNormal'){
  $taskRows+=@{pid=$taskEntry.ProcessId;command=$taskEntry.CommandLine;before=[string]$taskProc.PriorityClass;reason='Stale supervisor loaded before explicit NORMAL_PRIORITY_CLASS; normalize to the common intended scheduler class without interrupting native computation'}
  $taskProc.PriorityClass='Normal'
 }
}
$taskRows | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $taskRepo 'Reports/StructTrainClassic/_work/TrainingReproducibility-20261123/stale-controller-priority-correction.json') -Encoding utf8
Write-Output "Normalized $($taskRows.Count) stale study processes to Normal"
