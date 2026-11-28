[CmdletBinding()]
param([string]$GateId='node-recovery-9d2a87e5-01',[string]$AnalysisSuffix='analysis-01')
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
if($env:COMPUTERNAME -ne 'AQUA3060' -or $GateId -notmatch '^node-recovery-[0-9a-f]{8}-[0-9]+$' -or
   $AnalysisSuffix -notmatch '^analysis-[0-9]+$'){throw 'Invalid server or attempt identity'}
$data='E:\Nmsdk-AxoneTimeLearner-Data'
$control='C:\Projects\nmsdk-axone-control'
$python='C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe'
$analysis="$control\Analyze-Server15Recovery-v1.py"
$seal="$control\Seal-Server15Attempt-recovery-v6.py"
if((Get-FileHash $analysis -Algorithm SHA256).Hash -ne 'C7340198320441BF8FA5C37BE89D20909A8252AC78EFF01223CDFEBADD2DCC9E'){throw 'Analysis producer changed'}
if((Get-FileHash $seal -Algorithm SHA256).Hash -ne '0D47B1F51F1DDFBED995E27B724D66A6738625B65D800DC2F7ED8406D51084FD'){throw 'Archive producer changed'}
$pointer="$data\Seals\$GateId\pointer.archive.json"
$deadline=[DateTime]::UtcNow.AddHours(3)
while(!(Test-Path -LiteralPath $pointer)){
    if([DateTime]::UtcNow -gt $deadline){throw 'The declared native gate was not sealed; no analysis was started'}
    Start-Sleep -Seconds 5
}
$env:PATH='C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd;C:\Windows\System32\WindowsPowerShell\v1.0;C:\Windows\System32;C:\Windows'
$id="$GateId-$AnalysisSuffix"
& $python -I -S -B $analysis --data-root $data --gate-pointer $pointer --archive-id 7d37d9df-beda-4bdd-9cc2-7068e364f154 `
  --archive-adapter $seal --archive-adapter-sha256 0d47b1f51f1ddfbed995e27b724d66a6738625b65d800dc2f7ed8406d51084fd `
  --conduction-helper "$control\Analyze-Server15Conduction-v1.py" `
  --conduction-helper-sha256 29d929f94766b0663ce31558197c0324de4751f7c2524ea2510530f627ced26f `
  --event-helper "$control\Analyze-Server15Factory-regeneration-v2.py" `
  --event-helper-sha256 21afe6e3cfc1c65b1dfc890bdae70837d04f97f2753f9de795e464d0052c962e `
  --output "$data\Experiments\$id"
$analysisExit=$LASTEXITCODE
& $python -I -S -B $seal --data-root $data --archive-id 7d37d9df-beda-4bdd-9cc2-7068e364f154 `
  --attempt "$data\Experiments\$id" --role analysis --seal-id $id
if($LASTEXITCODE){throw 'Analysis sealing failed'}
& $python -I -S -B $seal --data-root $data --archive-id 7d37d9df-beda-4bdd-9cc2-7068e364f154 `
  --verify-pointer "$data\Seals\$id\pointer.archive.json"
if($LASTEXITCODE){throw 'Analysis readback failed'}
if($analysisExit){throw 'The failed analysis is preserved; no physical model was rerun'}
