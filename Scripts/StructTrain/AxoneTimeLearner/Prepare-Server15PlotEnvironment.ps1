[CmdletBinding()]
param(
    [string]$EnvironmentRoot='C:\Projects\nmsdk-axone-analysis\py313-mpl3107',
    [string]$EvidenceRoot='E:\Nmsdk-AxoneTimeLearner-Data\Setup\plot-environment-py313-mpl3107-01'
)
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
if($env:COMPUTERNAME -ne 'AQUA3060'){throw 'Server .15 required'}
$data='E:\Nmsdk-AxoneTimeLearner-Data'
$marker=Get-Content -LiteralPath "$data\archive.root.json" -Raw|ConvertFrom-Json
$disk=Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='E:'"
if($marker.archive_id -ne '7d37d9df-beda-4bdd-9cc2-7068e364f154' -or $disk.FileSystem -ne 'NTFS' -or
   $marker.volume_serial -ne $disk.VolumeSerialNumber){throw 'Archive root identity differs'}
if(![IO.Path]::GetFullPath($EvidenceRoot).StartsWith($data+'\Setup\',[StringComparison]::OrdinalIgnoreCase) -or
   ![IO.Path]::GetFullPath($EnvironmentRoot).StartsWith('C:\Projects\nmsdk-axone-analysis\',[StringComparison]::OrdinalIgnoreCase)){
    throw 'Unexpected environment or evidence scope'
}
if((Test-Path -LiteralPath $EnvironmentRoot) -or (Test-Path -LiteralPath $EvidenceRoot)){throw 'Fresh environment and attempt required'}
$null=[IO.Directory]::CreateDirectory($EvidenceRoot)
Copy-Item -LiteralPath $PSCommandPath -Destination "$EvidenceRoot\producer.ps1"
$state=@{kind='axone_analysis_environment_setup';schema_version=1;completed=$false;error=$null;
  environment_root=$EnvironmentRoot;matplotlib='3.10.7';model_executed=$false;started_utc=[DateTime]::UtcNow.ToString('o')}
try{
    & 'C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe' -I -B -m venv $EnvironmentRoot
    if($LASTEXITCODE){throw 'venv creation failed'}
    $python=Join-Path $EnvironmentRoot 'Scripts\python.exe'
    $env:MPLCONFIGDIR="$data\PythonPackageCache\matplotlib3107"
    $ErrorActionPreference='Continue'
    & $python -I -B -m pip --isolated --disable-pip-version-check --cache-dir "$data\PythonPackageCache" install --only-binary=:all: `
      --report "$EvidenceRoot\pip-install.json" matplotlib==3.10.7 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath "$EvidenceRoot\install.log"
    $code=$LASTEXITCODE
    $ErrorActionPreference='Stop'
    if($code){throw 'Plot dependencies installation failed'}
    & $python -I -B -m pip freeze --all | Set-Content -LiteralPath "$EvidenceRoot\requirements-freeze.txt" -Encoding UTF8
    if($LASTEXITCODE){throw 'Environment freeze failed'}
    & $python -I -B -c "import json,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as p; f=p.figure(); p.close(f); print(json.dumps({'matplotlib':matplotlib.__version__,'backend':matplotlib.get_backend()}))" |
      Set-Content -LiteralPath "$EvidenceRoot\renderer-probe.json" -Encoding UTF8
    if($LASTEXITCODE){throw 'Agg renderer import failed'}
    $state.completed=$true
}catch{$state.error=$_.ToString();throw}
finally{
    $state.finished_utc=[DateTime]::UtcNow.ToString('o')
    [IO.File]::WriteAllText("$EvidenceRoot\initialization.json",($state|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
}
