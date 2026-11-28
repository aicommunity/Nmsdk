[CmdletBinding()]
param(
    [ValidateSet('configure','build','all')][string]$Action = 'all',
    [Parameter(Mandatory=$true)][string]$VcpkgRoot,
    [Parameter(Mandatory=$true)][string]$QtRoot,
    [Parameter(Mandatory=$true)][string]$CMakeExecutable,
    [Parameter(Mandatory=$true)][string]$NinjaExecutable,
    [Parameter(Mandatory=$true)][string]$BuildRoot,
    [Parameter(Mandatory=$true)][string]$RuntimeRoot,
    [Parameter(Mandatory=$true)][string]$DependencyRoot,
    [Parameter(Mandatory=$true)][string]$EvidenceRoot,
    [string]$DataRoot = 'E:\Nmsdk-AxoneTimeLearner-Data',
    [string]$PythonExecutable = '',
    [string[]]$Targets = @('NeuroModelerConsole','Test_PulseLib_StorageComponents'),
    [int]$Jobs = 6
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$originalEnvironment = @{}
Get-ChildItem Env: | ForEach-Object { $originalEnvironment[$_.Name] = $_.Value }
try {
    if($env:COMPUTERNAME -ne 'AQUA3060') { throw 'This execution profile is for server .15 (AQUA3060).' }
    if($Jobs -lt 1 -or $Jobs -gt 8) { throw 'Jobs must be between 1 and 8.' }
    $repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
    foreach($candidate in @($VcpkgRoot,$QtRoot,$CMakeExecutable,$NinjaExecutable)) {
        if(!(Test-Path -LiteralPath $candidate)) { throw "Missing build prerequisite: $candidate" }
    }
    if(!(Test-Path -LiteralPath (Join-Path $VcpkgRoot 'vcpkg.exe'))) { throw 'Bootstrap the pinned vcpkg checkout first.' }
    $markerPath = Join-Path $DataRoot 'archive.root.json'
    if(!(Test-Path -LiteralPath $markerPath)) { throw 'Initialize the E: data root first.' }
    $marker = Get-Content -LiteralPath $markerPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='E:'"
    if($marker.kind -ne 'nmsdk_axone_timelearner_data_root' -or $marker.schema_version -ne 1 -or
       $marker.volume_serial -ne $disk.VolumeSerialNumber -or $marker.computer -ne $env:COMPUTERNAME -or
       $marker.authoritative_root -ne [IO.Path]::GetFullPath($DataRoot) -or $disk.FileSystem -ne 'NTFS') {
        throw 'Data-root marker or volume identity differs.'
    }
    $evidenceAbsolute = [IO.Path]::GetFullPath($EvidenceRoot)
    if(!$evidenceAbsolute.StartsWith(([IO.Path]::GetFullPath($DataRoot)+'\'),[StringComparison]::OrdinalIgnoreCase)) {
        throw 'Server .15 evidence must stay below its declared E: data root.'
    }
    foreach($directory in @($BuildRoot,$RuntimeRoot,$DependencyRoot,$EvidenceRoot)) {
        if(![IO.Path]::IsPathRooted($directory)) { throw 'Use absolute operation paths.' }
        $null = [IO.Directory]::CreateDirectory($directory)
    }
    $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
    if(!(Test-Path -LiteralPath $vswhere)) { throw 'Visual Studio Installer/vswhere is required.' }
    $instances = & $vswhere -all -products '*' -format json | ConvertFrom-Json
    if($LASTEXITCODE) { throw 'vswhere failed.' }
    $selection = foreach($instance in $instances) {
        if(!$instance.installationVersion.StartsWith('17.') -or !$instance.isComplete) { continue }
        $toolsRoot = Join-Path $instance.installationPath 'VC/Tools/MSVC'
        if(!(Test-Path -LiteralPath $toolsRoot)) { continue }
        foreach($tool in Get-ChildItem -LiteralPath $toolsRoot -Directory) {
            if($tool.Name -match '^14\.(3\d|4\d)\.' -and
               (Test-Path -LiteralPath (Join-Path $tool.FullName 'bin/Hostx64/x64/cl.exe'))) {
                [pscustomobject]@{ Instance=$instance; Tool=$tool; Version=[version]$tool.Name }
            }
        }
    }
    $chosen = $selection | Sort-Object Version -Descending | Select-Object -First 1
    if(!$chosen) { throw 'VS2022 v143 x64 toolset is required.' }
    $vcvars = Join-Path $chosen.Instance.installationPath 'VC/Auxiliary/Build/vcvarsall.bat'
    $command = 'call "' + $vcvars + '" x64 -vcvars_ver=' + $chosen.Tool.Name + ' >nul && set'
    $developerEnvironment = & $env:ComSpec /d /c $command
    if($LASTEXITCODE) { throw 'vcvarsall failed.' }
    foreach($line in $developerEnvironment) {
        if($line -match '^([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($Matches[1],$Matches[2],'Process')
        }
    }
    $env:VCPKG_DOWNLOADS = Join-Path $DataRoot 'VcpkgDownloads'
    $env:VCPKG_DEFAULT_BINARY_CACHE = Join-Path $DataRoot 'VcpkgCache'
    $env:VCPKG_ROOT = (Resolve-Path -LiteralPath $VcpkgRoot).Path
    $env:VCPKG_VISUAL_STUDIO_PATH = $chosen.Instance.installationPath
    $env:VCPKG_MAX_CONCURRENCY = "$Jobs"
    $env:CMAKE_BUILD_PARALLEL_LEVEL = "$Jobs"
    $env:QT_ROOT = (Resolve-Path -LiteralPath $QtRoot).Path
    Remove-Item Env:QT_PLUGIN_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:QML2_IMPORT_PATH -ErrorAction SilentlyContinue

    $git = Join-Path $chosen.Instance.installationPath 'Common7/IDE/CommonExtensions/Microsoft/TeamFoundation/Team Explorer/Git/cmd/git.exe'
    if(!(Test-Path -LiteralPath $git)) { $git = (Get-Command git -ErrorAction Stop).Source }
    $env:PATH = "$(Split-Path $git);$(Split-Path $CMakeExecutable);$(Split-Path $NinjaExecutable);$env:PATH"
    $rootHead = & $git -C $repo rev-parse HEAD
    if($LASTEXITCODE) { throw 'Cannot identify source commit.' }
    $vcpkgHead = & $git -C $VcpkgRoot rev-parse HEAD
    if($LASTEXITCODE) { throw 'Cannot identify vcpkg commit.' }
    if($vcpkgHead -ne '5cad485d1ddb649c8fa1022bf0b3908555e6e6ba') { throw 'Pinned reference vcpkg checkout differs.' }
    $submodules = @(& $git -C $repo submodule status --recursive)
    if($LASTEXITCODE -or @($submodules | Where-Object {$_ -match '^[+-U]'}).Count) {
        throw 'All declared submodule revisions must be initialized and exact.'
    }
    $dirty = @(& $git -C $repo status --porcelain --untracked-files=all)
    if($LASTEXITCODE -or $dirty.Count) { throw 'Build only clean, committed source trees.' }
    $plan = [ordered]@{
        kind='axone_server15_build_attempt'; schema_version=1
        computer=$env:COMPUTERNAME; created_utc=[DateTime]::UtcNow.ToString('o')
        action=$Action; source_root=$repo; root_commit=$rootHead; submodules=$submodules
        vcpkg_root=$VcpkgRoot; vcpkg_commit=$vcpkgHead
        compiler_directory=$chosen.Tool.FullName; visual_studio=$chosen.Instance.installationPath
        vc_tools_version=$env:VCToolsVersion; windows_sdk_version=$env:WindowsSDKVersion
        cmake=$CMakeExecutable; ninja=$NinjaExecutable; qt_root=$QtRoot
        build_root=$BuildRoot; runtime_root=$RuntimeRoot; dependency_root=$DependencyRoot
        targets=$Targets; jobs=$Jobs; scientific_execution=$false; tests_executed=$false
    }
    $planPath = Join-Path $EvidenceRoot 'build-attempt.json'
    if(Test-Path -LiteralPath $planPath) { throw 'Use a fresh evidence directory for each build attempt.' }
    [IO.File]::WriteAllText($planPath,($plan | ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
    $result = [ordered]@{kind='axone_server15_build_result';schema_version=1;configure_exit=$null;build_exit=$null;deployment_exit=$null;completed=$false;error=$null}
    try {
        Push-Location $repo
        try {
            if($Action -in @('configure','all')) {
                $configure = @('--preset','axone-win-v143-localqt','-B',$BuildRoot,
                    "-DCMAKE_MAKE_PROGRAM=$NinjaExecutable","-DCMAKE_PREFIX_PATH=$QtRoot",
                    "-DQt5_DIR=$QtRoot/lib/cmake/Qt5","-DVCPKG_INSTALLED_DIR=$DependencyRoot",
                    "-DNMSDK_DEPLOY_ROOT=$RuntimeRoot")
                if($PythonExecutable) {
                    $configure += @("-DNMSDK_PYTHON=$PythonExecutable","-DPython3_EXECUTABLE=$PythonExecutable")
                }
                $ErrorActionPreference = 'Continue'
                & $CMakeExecutable @configure 2>&1 | ForEach-Object { $_.ToString() } |
                    Tee-Object -FilePath (Join-Path $EvidenceRoot 'configure.log')
                $result.configure_exit = $LASTEXITCODE
                $ErrorActionPreference = 'Stop'
                if($result.configure_exit) { throw "Configure failed: $($result.configure_exit)" }
            }
            if($Action -in @('build','all')) {
                $arguments = @('--build',$BuildRoot,'--parallel',"$Jobs",'--target') + $Targets
                $ErrorActionPreference = 'Continue'
                & $CMakeExecutable @arguments 2>&1 | ForEach-Object { $_.ToString() } |
                    Tee-Object -FilePath (Join-Path $EvidenceRoot 'build.log')
                $result.build_exit = $LASTEXITCODE
                $ErrorActionPreference = 'Stop'
                if($result.build_exit) { throw "Build failed: $($result.build_exit)" }
                $deploy = Join-Path $QtRoot 'bin/windeployqt.exe'
                if(!(Test-Path -LiteralPath $deploy)) { throw 'Selected Qt windeployqt is missing.' }
                foreach($target in $Targets) {
                    $executable = Join-Path $RuntimeRoot "$target.exe"
                    if(!(Test-Path -LiteralPath $executable)) { throw "Built target missing: $executable" }
                    & $deploy --release --no-translations --no-compiler-runtime --dir $RuntimeRoot --plugindir "$RuntimeRoot/plugins" $executable
                    if($LASTEXITCODE) { throw "Qt deployment failed: $target" }
                }
                [IO.File]::WriteAllText((Join-Path $RuntimeRoot 'qt.conf'),"[Paths]`nPrefix=.`nPlugins=plugins`n",[Text.UTF8Encoding]::new($false))
                $result.deployment_exit = 0
            }
            $result.completed = $true
        } finally { Pop-Location }
    } catch {
        $result.error = $_.ToString()
        throw
    } finally {
        $result.finished_utc = [DateTime]::UtcNow.ToString('o')
        [IO.File]::WriteAllText((Join-Path $EvidenceRoot 'build-result.json'),($result | ConvertTo-Json -Depth 6),[Text.UTF8Encoding]::new($false))
    }
} finally {
    foreach($entry in @(Get-ChildItem Env:)) {
        if(!$originalEnvironment.ContainsKey($entry.Name)) {
            [Environment]::SetEnvironmentVariable($entry.Name,$null,'Process')
        }
    }
    foreach($name in $originalEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name,$originalEnvironment[$name],'Process')
    }
}
