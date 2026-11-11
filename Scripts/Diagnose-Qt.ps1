[CmdletBinding()]
param(
  [string[]]$Root = @(),
  [string[]]$SearchRoot = @(),
  [version]$CompilerVersion,
  [switch]$WithWebEngine,
  [switch]$Json,
  [switch]$NoExit
)
# Read-only inventory of desktop Windows MSVC x64 Qt kits for Nmsdk.
$ErrorActionPreference = 'Stop'
$candidates = [Collections.Generic.List[string]]::new()
$seenCandidates = @{}
function Add-Candidate([string]$Path) {
  if(!$Path) { return }
  $Path = [Environment]::ExpandEnvironmentVariables($Path.Trim().Trim('"'))
  if(Test-Path -LiteralPath $Path -PathType Leaf) {
    $Path = Split-Path (Split-Path $Path -Parent) -Parent
  }
  $Path = $Path -replace '[\\/]lib[\\/]cmake[\\/]Qt[56][\\/]?$',''
  try { $Path = [IO.Path]::GetFullPath($Path).TrimEnd('\','/') } catch { return }
  if(!$seenCandidates.ContainsKey($Path)) { $seenCandidates[$Path]=$true; $candidates.Add($Path) }
}
foreach($path in $Root) { Add-Candidate $path }
$explicitCandidates=@($candidates.ToArray())
if(!$Root.Count) {
foreach($scope in @('Process','User','Machine')) {
  Add-Candidate ([Environment]::GetEnvironmentVariable('QT_ROOT',$scope))
  foreach($path in ([Environment]::GetEnvironmentVariable('CMAKE_PREFIX_PATH',$scope) -split ';')) { Add-Candidate $path }
}
foreach($name in @('Qt5_DIR','Qt6_DIR')) { Add-Candidate ([Environment]::GetEnvironmentVariable($name)) }
foreach($name in @('qmake.exe','qmake6.exe','qtpaths.exe','qtpaths6.exe')) {
  Get-Command $name -CommandType Application -All -ErrorAction SilentlyContinue | ForEach-Object { Add-Candidate $_.Source }
}
foreach($major in @(5,6)) {
  $key = "HKCU:\Software\Kitware\CMake\Packages\Qt$major"
  if(Test-Path $key) {
    $registry = Get-Item $key
    foreach($name in $registry.GetValueNames()) { Add-Candidate ([string]$registry.GetValue($name)) }
  }
}
$creator = Join-Path $env:APPDATA 'QtProject/qtcreator/qtversion.xml'
if(Test-Path -LiteralPath $creator) {
  try {
    [xml]$versions = Get-Content $creator -Raw
    foreach($node in $versions.SelectNodes('//value[@key="QtVersion.QMakePath"]')) { Add-Candidate $node.InnerText }
  } catch { Write-Warning "Cannot read Qt Creator kit inventory: $($_.Exception.Message)" }
}
}
# Bounded search: installation root, version directory, kit directory. No disk scan.
foreach($path in $SearchRoot) {
  Add-Candidate $path
  if(Test-Path -LiteralPath $path -PathType Container) {
    foreach($versionDir in Get-ChildItem -LiteralPath $path -Directory) {
      Add-Candidate $versionDir.FullName
      foreach($kitDir in Get-ChildItem -LiteralPath $versionDir.FullName -Directory) { Add-Candidate $kitDir.FullName }
    }
  }
}
function Get-PeMachine([string]$Path) {
  $stream = [IO.File]::OpenRead($Path)
  $reader = [IO.BinaryReader]::new($stream)
  try {
    if($reader.ReadUInt16() -ne 0x5A4D) { return 'invalid' }
    $stream.Position=0x3c; $offset=$reader.ReadInt32()
    if($offset -lt 0 -or $offset + 6 -gt $stream.Length) { return 'invalid' }
    $stream.Position=$offset
    if($reader.ReadUInt32() -ne 0x4550) { return 'invalid' }
    switch($reader.ReadUInt16()) { 0x8664 { 'x64' } 0x14c { 'x86' } 0xaa64 { 'arm64' } default { 'unknown' } }
  } finally { $reader.Dispose(); $stream.Dispose() }
}
$results = @()
foreach($candidate in $candidates) {
  $qconfig = Join-Path $candidate 'mkspecs/qconfig.pri'
  $qmake = Join-Path $candidate 'bin/qmake.exe'
  if(!(Test-Path -LiteralPath $qconfig) -and !(Test-Path -LiteralPath $qmake)) {
    if($explicitCandidates -contains $candidate) {
      $results += [pscustomobject]@{Root=$candidate;Version=$null;BuiltWithMsvc=$null;Valid=$false;Problems=@('No qconfig.pri or qmake.exe')}
    }
    continue
  }
  $problems = [Collections.Generic.List[string]]::new()
  $metadata = @{}
  if(Test-Path -LiteralPath $qconfig) {
    foreach($line in Get-Content -LiteralPath $qconfig) {
      if($line -match '^\s*(\w+)\s*=\s*(.*?)\s*$') { $metadata[$Matches[1]]=$Matches[2] }
    }
  }
  $qtVersion = $metadata['QT_VERSION']
  if(Test-Path -LiteralPath $qmake) {
    $query = & $qmake -query 2>&1
    if($LASTEXITCODE -ne 0) { $problems.Add('qmake -query failed') }
    else {
      $queryValues = @{}
      foreach($line in $query) { if("$line" -match '^([^:]+):(.*)$') { $queryValues[$Matches[1]]=$Matches[2] } }
      if($queryValues['QT_VERSION']) { $qtVersion=$queryValues['QT_VERSION'] }
      if($queryValues['QT_INSTALL_PREFIX']) {
        $reported=[IO.Path]::GetFullPath($queryValues['QT_INSTALL_PREFIX']).TrimEnd('\','/')
        if($reported -ne $candidate) { $problems.Add("qmake reports a different prefix: $reported") }
      }
    }
  } else { $problems.Add('Missing bin/qmake.exe') }
  $parsedVersion = $null
  if(![version]::TryParse($qtVersion,[ref]$parsedVersion) -or $parsedVersion.Major -notin @(5,6)) {
    $problems.Add('Cannot identify Qt 5/6 version')
  } else {
    $major=$parsedVersion.Major
    if($major -eq 5 -and $parsedVersion -lt [version]'5.15') { $problems.Add('Qt 5.15 or newer is required') }
    $modules=@('Core','Gui','Widgets','Network','PrintSupport','Sql','Xml','Concurrent','Test','SerialPort','Charts','Svg')
    if($major -eq 6) { $modules+=@('Core5Compat','SvgWidgets') }
    if($WithWebEngine) { $modules+='WebEngineWidgets' }
    foreach($module in $modules) {
      if(!(Test-Path -LiteralPath "$candidate/lib/cmake/Qt$major$module/Qt$major${module}Config.cmake")) { $problems.Add("Missing CMake module: $module") }
      foreach($suffix in @('','d')) {
        $config=if($suffix) { 'Debug' } else { 'Release' }
        if(!(Test-Path -LiteralPath "$candidate/lib/Qt$major$module$suffix.lib")) { $problems.Add("Missing $config import library: $module") }
        if(!(Test-Path -LiteralPath "$candidate/bin/Qt$major$module$suffix.dll")) { $problems.Add("Missing $config DLL: $module") }
      }
    }
    foreach($suffix in @('','d')) {
      $core="$candidate/bin/Qt${major}Core$suffix.dll"
      if(Test-Path -LiteralPath $core) {
        $architecture=Get-PeMachine $core
        if($architecture -ne 'x64') { $problems.Add("QtCore$suffix.dll architecture is $architecture; x64 required") }
      }
      if(!(Test-Path -LiteralPath "$candidate/plugins/platforms/qwindows$suffix.dll")) { $problems.Add("Missing Windows platform plugin: qwindows$suffix.dll") }
    }
  }
  $builtWith=$null
  if($metadata['QT_MSVC_MAJOR_VERSION'] -and $metadata['QT_MSVC_MINOR_VERSION']) {
    $builtWith=[version]"$($metadata['QT_MSVC_MAJOR_VERSION']).$($metadata['QT_MSVC_MINOR_VERSION'])"
    if($CompilerVersion -and $CompilerVersion -lt $builtWith) { $problems.Add("MSVC $CompilerVersion is older than the kit compiler $builtWith") }
  } else { $problems.Add('No MSVC compiler metadata; this may be a MinGW or non-Windows kit') }
  if($metadata['QT_ARCH'] -ne 'x86_64') { $problems.Add("qconfig architecture '$($metadata['QT_ARCH'])' is not x86_64") }
  if(!(Test-Path -LiteralPath "$candidate/bin/windeployqt.exe")) { $problems.Add('Missing bin/windeployqt.exe') }
  if($WithWebEngine) {
    foreach($file in @('bin/QtWebEngineProcess.exe','resources/icudtl.dat','resources/qtwebengine_resources.pak','translations/qtwebengine_locales/en-US.pak')) {
      if(!(Test-Path -LiteralPath (Join-Path $candidate $file))) { $problems.Add("Missing WebEngine runtime: $file") }
    }
  }
  $results += [pscustomobject]@{Root=$candidate;Version=$qtVersion;BuiltWithMsvc="$builtWith";Valid=($problems.Count -eq 0);Problems=@($problems.ToArray())}
}
if($Json) { ConvertTo-Json -InputObject @($results) -Depth 6 }
else {
  foreach($kit in $results) {
    $status=if($kit.Valid) { 'PASS' } else { 'FAIL' }
    Write-Output "$status Qt $($kit.Version), MSVC $($kit.BuiltWithMsvc): $($kit.Root)"
    foreach($problem in $kit.Problems) { Write-Output "  - $problem" }
  }
  if(!$results.Count) { Write-Output 'No Qt kits found. Specify -SearchRoot <installation-directory> or -Root <kit-directory>.' }
  elseif(@($results | Where-Object Valid).Count -gt 1) { Write-Output 'Several kits passed. Select one explicitly with QT_ROOT; no kit was selected automatically.' }
}
if(!$NoExit -and !@($results | Where-Object Valid).Count) { exit 1 }
