[CmdletBinding()]
param(
  [string]$Preset = 'win-vs2022-ninja-release-localqt',
  [ValidateSet('configure','build','rebuild','clean','all')][string]$Action = 'all',
  [string]$QtRoot = $env:QT_ROOT,
  [string[]]$Targets = @('NeuroModeler','NeuroModelerConsole'),
  [int]$Jobs = 0,
  [string[]]$ExtraCMakeArgs = @(),
  [switch]$WithTests,
  [switch]$WithWebEngine
)
$ErrorActionPreference = 'Stop'
$originalEnvironment = @{}
Get-ChildItem Env: | ForEach-Object { $originalEnvironment[$_.Name] = $_.Value }
try {
  # Generic QT_ROOT presets are opt-in; the wrapper supplies their environment.
  if($Preset.EndsWith('-localqt')) { $env:NMSDK_SHOW_QT_ROOT_PRESETS = '1' }
  $requestedVcpkgRoot = $env:VCPKG_ROOT
  $preferredCmake = (Get-Command cmake -CommandType Application -ErrorAction SilentlyContinue).Source
  $repo = Split-Path $PSScriptRoot -Parent
  $basePreset = $Preset
  $registeredPreset = $null
  $userPresetsPath = Join-Path $repo 'CMakeUserPresets.json'
  if(Test-Path -LiteralPath $userPresetsPath) {
    $userPresets = Get-Content -LiteralPath $userPresetsPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $registeredPreset = $userPresets.configurePresets | Where-Object {
      $_.name -eq $Preset -and $_.vendor.'nmsdk/qt-discovery/1.0'.generated
    } | Select-Object -First 1
    if($registeredPreset) { $basePreset = $registeredPreset.inherits }
  }
  if($basePreset -notmatch '^win-vs(2019|2022|2026)-(ninja|msbuild)-(debug|release)-(localqt|vcpkgqt)$') {
    throw 'Select a registered local Qt preset or a generic Windows preset. See Docs/Build-Windows.md.'
  }
  $vsYear = $Matches[1]
  $generator = $Matches[2]
  $isLocalQt = $Matches[4] -eq 'localqt'
  $requiredVsMajor = $null
  if($registeredPreset) {
    $requiredVsMajor = $registeredPreset.vendor.'microsoft.com/VisualStudioSettings/CMake/1.0'.vsInstanceVersion
    $pinnedQtRoot = $registeredPreset.environment.QT_ROOT
    if($PSBoundParameters.ContainsKey('QtRoot') -and $QtRoot -and
       (Resolve-Path -LiteralPath $QtRoot).Path -ne (Resolve-Path -LiteralPath $pinnedQtRoot).Path) {
      throw 'This preset pins another Qt kit. Select or register the required kit instead of overriding -QtRoot.'
    }
    $QtRoot = $pinnedQtRoot
  }
  $toolsetPattern = switch($vsYear) { '2019' {'^14\.2[9]\.'} '2022' {'^14\.(3\d|4\d)\.'} '2026' {'^14\.5\d\.'} }
  $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
  if(!(Test-Path -LiteralPath $vswhere)) { throw 'Install Visual Studio Build Tools and its Desktop development with C++ workload.' }
  $instances = & $vswhere -all -products '*' -format json | ConvertFrom-Json
  $selection = foreach($instance in $instances) {
    if($requiredVsMajor -and !($instance.installationVersion.StartsWith("$requiredVsMajor."))) { continue }
    if($vsYear -eq '2022' -and !$instance.installationVersion.StartsWith('17.')) { continue }
    $toolsRoot = Join-Path $instance.installationPath 'VC/Tools/MSVC'
    if(Test-Path -LiteralPath $toolsRoot) {
      foreach($tool in Get-ChildItem -LiteralPath $toolsRoot -Directory) {
        if($tool.Name -match $toolsetPattern -and (Test-Path -LiteralPath (Join-Path $tool.FullName 'bin/Hostx64/x64/cl.exe'))) {
          [pscustomobject]@{ Instance=$instance; Tool=$tool; Version=[version]$tool.Name }
        }
      }
    }
  }
  if($generator -eq 'msbuild') {
    $major = switch($vsYear) { '2019' {'16.'} '2022' {'17.'} '2026' {'18.'} }
    if($requiredVsMajor) { $major = "$requiredVsMajor." }
    $selection = $selection | Where-Object {$_.Instance.installationVersion.StartsWith($major)}
  }
  $chosen = $selection | Sort-Object Version -Descending | Select-Object -First 1
  if(!$chosen) { throw "No compatible MSVC $vsYear x64 toolset is installed for $generator. Ninja can use v142 installed inside VS2022." }
  $vcvars = Join-Path $chosen.Instance.installationPath 'VC/Auxiliary/Build/vcvarsall.bat'
  # Use the environment supplied by the selected VS instance; do not synthesize
  # INCLUDE/LIB or mix SDK/STL files from a different compiler installation.
  $envCommand = 'call "' + $vcvars + '" x64 -vcvars_ver=' + $chosen.Tool.Name + ' >nul && set'
  $environment = & $env:ComSpec /d /c $envCommand
  if($LASTEXITCODE) { throw 'vcvarsall failed' }
  foreach($line in $environment) {
    if($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($Matches[1],$Matches[2],'Process') }
  }
  if($requestedVcpkgRoot) { $env:VCPKG_ROOT = $requestedVcpkgRoot }
  $env:VCPKG_VISUAL_STUDIO_PATH = $chosen.Instance.installationPath
  if(!(Get-Command cmake -ErrorAction SilentlyContinue)) {
    $cmakeBin = Join-Path $chosen.Instance.installationPath 'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin'
    $env:PATH = "$cmakeBin;$env:PATH"
  }
  if($generator -eq 'ninja' -and !(Get-Command ninja -ErrorAction SilentlyContinue)) {
    $ninjaBin = Join-Path $chosen.Instance.installationPath 'Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja'
    $env:PATH = "$ninjaBin;$env:PATH"
  }
  if(!(Get-Command cmake -ErrorAction SilentlyContinue)) { throw 'Install CMake >= 3.23 and put it on PATH.' }
  $cmakeMinimum = if($chosen.Instance.installationVersion.StartsWith('18.') -and $generator -eq 'msbuild') { [version]'4.2' } else { [version]'3.23' }
  $cmakeExecutable = $null
  $cmakeCandidates = @($preferredCmake, (Get-Command cmake -CommandType Application -ErrorAction SilentlyContinue).Source,
    (Join-Path $chosen.Instance.installationPath 'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe')) |
    Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
  foreach($candidate in $cmakeCandidates) {
    $versionLine = & $candidate --version | Select-Object -First 1
    if($versionLine -match 'cmake version (\d+\.\d+(?:\.\d+)?)' -and [version]$Matches[1] -ge $cmakeMinimum) {
      $cmakeExecutable = $candidate; break
    }
  }
  if(!$cmakeExecutable) { throw "Install native Windows CMake >= $cmakeMinimum and put it on PATH." }
  if($QtRoot) { $env:QT_ROOT = (Resolve-Path -LiteralPath $QtRoot).Path }
  if($Action -in @('configure','all','rebuild') -and $isLocalQt -and !$env:QT_ROOT) { throw 'Set QT_ROOT or pass -QtRoot for a complete local Qt 5.15+ / Qt 6 installation.' }
  if(!$env:VCPKG_ROOT) { throw 'Set VCPKG_ROOT to a bootstrapped vcpkg checkout.' }
  # A global plugin path pointing at another Qt can make even a successful build
  # crash before main(). The deployed runtime selects its own matching plugins.
  Remove-Item Env:QT_PLUGIN_PATH -ErrorAction SilentlyContinue
  Remove-Item Env:QML2_IMPORT_PATH -ErrorAction SilentlyContinue
  if($Jobs -lt 1) { $Jobs = [Math]::Min(8,[Environment]::ProcessorCount) }
  $env:CMAKE_BUILD_PARALLEL_LEVEL = "$Jobs"
  $env:VCPKG_MAX_CONCURRENCY = "$Jobs"
  $lockDirectory = Join-Path $repo '.build-audit/locks'
  $null = [IO.Directory]::CreateDirectory($lockDirectory)
  $buildLease = $null
  while(!$buildLease) {
    try { $buildLease = [IO.File]::Open((Join-Path $lockDirectory "$Preset.lock"), 'OpenOrCreate', 'ReadWrite', 'None') }
    catch [IO.IOException] { Start-Sleep -Seconds 2 }
  }
  Push-Location $repo
  try {
    # Also honor an operation started before this helper acquired its lease.
    # Two Ninja/MSBuild invocations must not write the same build tree at once.
    $presetPattern = '(?:^|\s)--preset\s+"?' + [regex]::Escape($Preset) + '"?(?:\s|$)'
    $waitNotice = $false
    while(@(Get-CimInstance Win32_Process -Filter "Name='cmake.exe'" |
        Where-Object { $_.CommandLine -match $presetPattern }).Count) {
      if(!$waitNotice) { Write-Host "Waiting for the existing CMake operation for $Preset..."; $waitNotice = $true }
      Start-Sleep -Seconds 3
    }
    if($Action -in @('configure','all','rebuild')) {
      $configureArgs = @('--preset',$Preset)
      if($WithTests) {
        $features = 'llm;tests' + $(if($Preset.EndsWith('-vcpkgqt')) {';qt'})
        $configureArgs += @('-DBUILD_TESTING=ON',"-DVCPKG_MANIFEST_FEATURES=$features")
      }
      if($WithWebEngine) {
        $features = 'llm' + $(if($Preset.EndsWith('-vcpkgqt')) {';qt;webengine'}) + $(if($WithTests) {';tests'})
        $configureArgs += @('-DNMSDK_USE_WEBENGINE=ON',"-DVCPKG_MANIFEST_FEATURES=$features")
      }
      $configureArgs += $ExtraCMakeArgs
      # Windows PowerShell 5 can turn a native stderr warning into a terminating
      # error when callers redirect output. CMake's exit code is authoritative.
      $ErrorActionPreference = 'Continue'
      & $cmakeExecutable @configureArgs 2>&1 | ForEach-Object { $_.ToString() }
      $ErrorActionPreference = 'Stop'
      if($LASTEXITCODE) { throw "Configure failed ($LASTEXITCODE)" }
    }
    if($Action -in @('build','all','rebuild','clean')) {
      $buildArgs = @('--build','--preset',$Preset,'--parallel',"$Jobs")
      if($Action -eq 'clean') { $buildArgs += @('--target','clean') }
      else {
        if($Action -eq 'rebuild') { $buildArgs += '--clean-first' }
        $buildArgs += '--target'; $buildArgs += $Targets
      }
      $ErrorActionPreference = 'Continue'
      & $cmakeExecutable @buildArgs 2>&1 | ForEach-Object { $_.ToString() }
      $ErrorActionPreference = 'Stop'
      if($LASTEXITCODE) { throw "Build failed ($LASTEXITCODE)" }
    }
  } finally { Pop-Location; $buildLease.Dispose() }
} finally {
  # vcvarsall is not idempotent in an already modified parent environment.
  # Restore the caller so repeated builds/toolset switches cannot grow PATH or
  # retain another compiler's INCLUDE/LIB and VSCMD state.
  foreach($entry in @(Get-ChildItem Env:)) {
    if(!$originalEnvironment.ContainsKey($entry.Name)) {
      [Environment]::SetEnvironmentVariable($entry.Name,$null,'Process')
    }
  }
  foreach($name in $originalEnvironment.Keys) {
    [Environment]::SetEnvironmentVariable($name,$originalEnvironment[$name],'Process')
  }
}
