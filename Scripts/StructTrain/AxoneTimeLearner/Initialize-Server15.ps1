[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{40}$')][string]$RootCommit,
    [string]$RootBranch = 'work/axone_timelearner/02-server-validation',
    [string]$CloneRoot = 'C:\Projects\nmsdk-axone-timelearner',
    [string]$VcpkgRoot = 'C:\Projects\vcpkg',
    [string]$DataRoot = 'E:\Nmsdk-AxoneTimeLearner-Data',
    [Parameter(Mandatory=$true)][string]$EvidenceRoot,
    [Parameter(Mandatory=$true)][string]$ExpectedVolumeSerial
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
if($env:COMPUTERNAME -ne 'AQUA3060') { throw 'Expected server .15 (AQUA3060).' }
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='E:'"
if($disk.FileSystem -ne 'NTFS' -or $disk.VolumeSerialNumber -ne $ExpectedVolumeSerial) {
    throw 'Data volume identity/filesystem differs; inspect it before writing.'
}
$dataAbsolute = [IO.Path]::GetFullPath($DataRoot)
$evidenceAbsolute = [IO.Path]::GetFullPath($EvidenceRoot)
if(!$dataAbsolute.StartsWith('E:\',[StringComparison]::OrdinalIgnoreCase) -or
   !$evidenceAbsolute.StartsWith($dataAbsolute+'\',[StringComparison]::OrdinalIgnoreCase)) {
    throw 'Evidence must stay inside the declared E: data root.'
}
$null = [IO.Directory]::CreateDirectory($DataRoot)
$null = [IO.Directory]::CreateDirectory($EvidenceRoot)
$markerPath = Join-Path $DataRoot 'archive.root.json'
if(Test-Path -LiteralPath $markerPath) {
    $marker = Get-Content -LiteralPath $markerPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if($marker.kind -ne 'nmsdk_axone_timelearner_data_root' -or
       $marker.schema_version -ne 1 -or $marker.volume_serial -ne $ExpectedVolumeSerial -or
       $marker.computer -ne $env:COMPUTERNAME -or $marker.authoritative_root -ne $dataAbsolute) {
        throw 'Existing data-root marker differs.'
    }
} else {
    $marker = [ordered]@{kind='nmsdk_axone_timelearner_data_root';schema_version=1;
        archive_id=[Guid]::NewGuid().ToString();computer=$env:COMPUTERNAME;
        authoritative_root=$dataAbsolute;volume_serial=$ExpectedVolumeSerial;
        file_system=$disk.FileSystem;share='\\10.245.1.15\E\Nmsdk-AxoneTimeLearner-Data';
        created_utc=[DateTime]::UtcNow.ToString('o')}
    [IO.File]::WriteAllText($markerPath,($marker | ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
}
$statePath = Join-Path $EvidenceRoot 'initialization.json'
if(Test-Path -LiteralPath $statePath) { throw 'Use a fresh initialization evidence directory.' }
$state = [ordered]@{kind='axone_server15_initialization';schema_version=1;
    created_utc=[DateTime]::UtcNow.ToString('o');pid=$PID;computer=$env:COMPUTERNAME;
    clone_root=$CloneRoot;data_root=$dataAbsolute;volume_serial=$ExpectedVolumeSerial;
    root_commit=$RootCommit;root_branch=$RootBranch;vcpkg_commit='cc73782a88db48af17f8bfb8328d4cab3d4c246f';
    current_step='preflight';steps=@();completed=$false;error=$null}
function Save-State {
    $temporary = Join-Path $EvidenceRoot 'initialization.json.tmp'
    [IO.File]::WriteAllText($temporary,($state | ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $statePath -Force
}
Save-State
$git = 'C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe'
if(!(Test-Path -LiteralPath $git)) { throw 'Validated Visual Studio Git is missing.' }
$env:PATH = "$(Split-Path $git);C:\Qt\Tools\CMake_64\bin;C:\Qt\Tools\Ninja;$env:PATH"
$env:GIT_TERMINAL_PROMPT = '0'
$env:GCM_INTERACTIVE = 'Never'
$env:VCPKG_DISABLE_METRICS = '1'
$env:VCPKG_DOWNLOADS = Join-Path $DataRoot 'VcpkgDownloads'
$env:VCPKG_DEFAULT_BINARY_CACHE = Join-Path $DataRoot 'VcpkgCache'
$null = [IO.Directory]::CreateDirectory($env:VCPKG_DOWNLOADS)
$null = [IO.Directory]::CreateDirectory($env:VCPKG_DEFAULT_BINARY_CACHE)
function Native-Step([string]$Name,[string]$Executable,[string[]]$Arguments) {
    $state.current_step = $Name
    Save-State
    Write-Output "START $Name"
    $previousError = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & $Executable @Arguments 2>&1 | ForEach-Object { $_.ToString() }
    $code = $LASTEXITCODE
    $ErrorActionPreference = $previousError
    $state.steps += [ordered]@{name=$Name;exit_code=$code;finished_utc=[DateTime]::UtcNow.ToString('o')}
    Save-State
    if($code) { throw "$Name failed: $code" }
    Write-Output "DONE $Name"
}
function Configure-Clone([string]$Directory) {
    Native-Step 'clone-longpaths' $git @('-C',$Directory,'config','--local','core.longpaths','true')
    Native-Step 'clone-exact-eol' $git @('-C',$Directory,'config','--local','core.autocrlf','false')
    Native-Step 'clone-no-recurse' $git @('-C',$Directory,'config','--local','submodule.recurse','false')
    Native-Step 'clone-no-fetch-recurse' $git @('-C',$Directory,'config','--local','fetch.recurseSubmodules','false')
}
try {
    $null = [IO.Directory]::CreateDirectory('C:\Projects')
    if(!(Test-Path -LiteralPath $VcpkgRoot)) {
        Native-Step 'clone-vcpkg' $git @('-c','core.longpaths=true','clone','--filter=blob:none','--no-checkout',
            'https://github.com/microsoft/vcpkg.git',$VcpkgRoot)
    }
    if(!(Test-Path -LiteralPath (Join-Path $VcpkgRoot '.git'))) { throw 'Existing vcpkg path is not a Git clone.' }
    Configure-Clone $VcpkgRoot
    Native-Step 'select-vcpkg' $git @('-C',$VcpkgRoot,'checkout','--detach',$state.vcpkg_commit)
    Push-Location $VcpkgRoot
    try { Native-Step 'bootstrap-vcpkg' $env:ComSpec @('/d','/c','bootstrap-vcpkg.bat -disableMetrics') }
    finally { Pop-Location }

    $pythonCandidates = @(Get-ChildItem -Path "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" -File -ErrorAction SilentlyContinue)
    if(!$pythonCandidates.Count) {
        $winget = (Get-Command winget -ErrorAction Stop).Source
        Native-Step 'install-python313' $winget @('install','--exact','--id','Python.Python.3.13',
            '--scope','user','--source','winget','--silent','--accept-source-agreements','--accept-package-agreements')
    }
    $python = Join-Path $env:LOCALAPPDATA 'Programs/Python/Python313/python.exe'
    if(!(Test-Path -LiteralPath $python)) { throw 'Installed Python 3.13 executable is missing.' }
    Native-Step 'python-version' $python @('--version')
    $state.python = $python

    if(!(Test-Path -LiteralPath $CloneRoot)) {
        Native-Step 'clone-nmsdk' $git @('-c','core.longpaths=true','clone','--filter=blob:none','--no-checkout',
            '--branch','axone_timelearner','https://github.com/aicommunity/Nmsdk.git',$CloneRoot)
    }
    if(!(Test-Path -LiteralPath (Join-Path $CloneRoot '.git'))) { throw 'Existing SDK path is not a Git clone.' }
    Configure-Clone $CloneRoot
    Native-Step 'fetch-sdk-branches' $git @('-C',$CloneRoot,'fetch','--no-recurse-submodules','origin')
    & $git -C $CloneRoot show-ref --verify --quiet ('refs/heads/'+$RootBranch)
    if($LASTEXITCODE) {
        Native-Step 'select-sdk-work' $git @('-C',$CloneRoot,'switch','--create',$RootBranch,$RootCommit)
    } else {
        if((& $git -C $CloneRoot rev-parse $RootBranch).Trim() -ne $RootCommit) { throw 'Existing SDK work branch differs.' }
        Native-Step 'select-existing-sdk-work' $git @('-C',$CloneRoot,'switch',$RootBranch)
    }
    Native-Step 'track-sdk-work' $git @('-C',$CloneRoot,'branch',('--set-upstream-to=origin/'+$RootBranch),$RootBranch)
    $actual = (& $git -C $CloneRoot rev-parse HEAD).Trim()
    if($LASTEXITCODE -or $actual -ne $RootCommit) { throw 'Published SDK work branch moved; use a newly declared attempt.' }
    $moduleRows = & $git -C $CloneRoot config -f .gitmodules --get-regexp '^submodule\..*\.path$'
    if($LASTEXITCODE) { throw 'Submodule inventory is missing.' }
    foreach($row in $moduleRows) {
        if($row -notmatch '^submodule\.(.+)\.path\s+(.+)$') { throw 'Unexpected submodule inventory row.' }
        $name = $Matches[1]
        $relative = $Matches[2]
        $url = (& $git -C $CloneRoot config -f .gitmodules --get ("submodule."+$name+".url")).Trim()
        if($LASTEXITCODE) { throw 'Missing submodule URL.' }
        $url = $url -replace '^git@github.com:','https://github.com/'
        $target = Join-Path $CloneRoot $relative
        $entry = (& $git -C $CloneRoot ls-tree HEAD -- $relative)
        if($entry -notmatch '^160000 commit ([0-9a-f]{40})\s') { throw 'Missing pinned submodule gitlink.' }
        $pinned = $Matches[1]
        Native-Step 'register-module-url' $git @('-C',$CloneRoot,'config',("submodule."+$name+".url"),$url)
        if(!(Test-Path -LiteralPath (Join-Path $target '.git'))) {
            Native-Step ("clone-"+$name) $git @('-c','core.longpaths=true','clone','--filter=blob:none','--no-checkout',$url,$target)
        }
        Configure-Clone $target
        if($relative -eq 'Bin') {
            Native-Step 'bin-sparse-init' $git @('-C',$target,'sparse-checkout','init','--cone')
            Native-Step 'bin-source-scope' $git @('-C',$target,'sparse-checkout','set','ClDesc','WatchPresets',
                'WatchTemplates','Styles','CodeTemplates','HardwareCatalog',
                'Configs/SpikeSamples/StructTrain/AxoneTimeLearner')
        }
        Native-Step ("pin-"+$name) $git @('-C',$target,'checkout','--detach',$pinned)
        if($relative -in @('Bin','Rdk','Libraries/Nmsdk-PulseLib')) {
            & $git -C $target show-ref --verify --quiet refs/heads/axone_timelearner
            if($LASTEXITCODE) {
                Native-Step 'create-module-base' $git @('-C',$target,'branch','axone_timelearner','origin/axone_timelearner')
            }
            if($relative -eq 'Rdk') {
                Native-Step 'select-rdk-base' $git @('-C',$target,'switch','axone_timelearner')
            } else {
                $work = 'work/axone_timelearner/01-axon-lifecycle'
                & $git -C $target show-ref --verify --quiet ('refs/heads/'+$work)
                if($LASTEXITCODE) {
                    Native-Step 'select-prepared-module' $git @('-C',$target,'switch','--create',$work,$pinned)
                } else {
                    if((& $git -C $target rev-parse $work).Trim() -ne $pinned) { throw 'Existing module work branch differs.' }
                    Native-Step 'select-existing-module-work' $git @('-C',$target,'switch',$work)
                }
                Native-Step 'track-prepared-module' $git @('-C',$target,'branch',
                    '--set-upstream-to=origin/work/axone_timelearner/01-axon-lifecycle','work/axone_timelearner/01-axon-lifecycle')
            }
            if((& $git -C $target rev-parse HEAD).Trim() -ne $pinned) { throw 'Prepared module branch differs from root gitlink.' }
        }
    }
    Native-Step 'absorb-submodule-gitdirs' $git @('-C',$CloneRoot,'submodule','absorbgitdirs')
    Native-Step 'initialize-nested-links' $git @('-C',$CloneRoot,'-c','core.longpaths=true',
        '-c','url.https://github.com/.insteadOf=git@github.com:','submodule','update','--init','--recursive')
    $status = @(& $git -C $CloneRoot status --porcelain --untracked-files=all)
    if($LASTEXITCODE -or $status.Count) { throw 'Initialized SDK is not clean.' }
    $state.submodules = @(& $git -C $CloneRoot submodule status --recursive)
    if($LASTEXITCODE -or @($state.submodules | Where-Object {$_ -match '^[+-U]'}).Count) { throw 'Submodule closure is not exact.' }
    $state.current_step = 'complete'
    $state.completed = $true
    Save-State
} catch {
    $state.error = $_.ToString()
    $state.finished_utc = [DateTime]::UtcNow.ToString('o')
    Save-State
    throw
}
$state.finished_utc = [DateTime]::UtcNow.ToString('o')
Save-State
Write-Output ($state | ConvertTo-Json -Depth 8)
