[CmdletBinding()]
param(
  [string[]]$Root = @(),
  [string[]]$SearchRoot = @(),
  [string[]]$BasePreset = @(),
  [switch]$WithWebEngine
)
# Machine-specific Qt paths belong only in the ignored CMakeUserPresets.json.
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot -Parent
$shared=Get-Content (Join-Path $repo 'CMakePresets.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
if(!(Test-Path -LiteralPath $vswhere)) { throw 'Visual Studio Installer (vswhere) is required to discover installed MSVC toolsets.' }
$instances=& $vswhere -all -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json | ConvertFrom-Json
if($LASTEXITCODE -ne 0) { throw 'Visual Studio discovery failed' }
$installedBases=@{}
foreach($instance in $instances) {
  $vsMajor=([version]$instance.installationVersion).Major
  $generatorName=switch($vsMajor) { 16 {'Visual Studio 16 2019'} 17 {'Visual Studio 17 2022'} 18 {'Visual Studio 18 2026'} default {$null} }
  if(!$generatorName) { continue }
  $tools=Join-Path $instance.installationPath 'VC/Tools/MSVC'
  if(!(Test-Path -LiteralPath $tools)) { continue }
  foreach($tool in Get-ChildItem -LiteralPath $tools -Directory) {
    $toolVersion=$null
    if(![version]::TryParse($tool.Name,[ref]$toolVersion) -or
       !(Test-Path -LiteralPath (Join-Path $tool.FullName 'bin/Hostx64/x64/cl.exe'))) { continue }
    $year=switch -Regex ($tool.Name) { '^14\.29\.' {'2019'} '^14\.(3\d|4\d)\.' {if($vsMajor -eq 17){'2022'}} '^14\.5\d\.' {if($vsMajor -eq 18){'2026'}} }
    if(!$year) { continue }
    $ninja=Join-Path $instance.installationPath 'Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe'
    $generators=@()
    if((Test-Path -LiteralPath $ninja) -or (Get-Command ninja -ErrorAction SilentlyContinue)) { $generators+='ninja' }
    if(Test-Path -LiteralPath (Join-Path $instance.installationPath 'MSBuild/Current/Bin/MSBuild.exe')) { $generators+='msbuild' }
    foreach($generator in $generators) {
      foreach($configuration in @('debug','release')) {
        $name="win-vs$year-$generator-$configuration-localqt"
        $record=[pscustomobject]@{Version=$toolVersion;CompilerVersion=[version]"19.$($toolVersion.Minor)";Instance=$instance;Generator=$generatorName}
        if(!$installedBases.ContainsKey($name) -or $installedBases[$name].Version -lt $toolVersion -or
           ($installedBases[$name].Version -eq $toolVersion -and [version]$installedBases[$name].Instance.installationVersion -lt [version]$instance.installationVersion)) {
          $installedBases[$name]=$record
        }
      }
    }
  }
}
if(!$BasePreset.Count) { $BasePreset=@($installedBases.Keys | Sort-Object) }
if(!$BasePreset.Count) { throw 'No supported MSVC x64 compiler/build tool combination was found.' }
foreach($name in $BasePreset) {
  if($name -notmatch '^win-vs(2019|2022|2026)-(ninja|msbuild)-(debug|release)-localqt$' -or
     $name -notin $shared.configurePresets.name) { throw "Unsupported local Qt base preset: $name" }
  if(!$installedBases.ContainsKey($name)) { throw "No installed compiler/build tool for $name" }
}
$inventoryFile=Join-Path $repo '.build-audit/qt-inventory.json'
New-Item -ItemType Directory -Force (Split-Path $inventoryFile -Parent) | Out-Null
$inventory = & (Join-Path $PSScriptRoot 'Diagnose-Qt.ps1') -Root $Root -SearchRoot $SearchRoot -WithWebEngine:$WithWebEngine -Json -NoExit
$inventory | Set-Content -LiteralPath $inventoryFile -Encoding UTF8
$kits=@(($inventory | ConvertFrom-Json) | Where-Object Valid)
if(!$kits.Count) { throw 'No complete MSVC x64 Qt kit found. Run Diagnose-Qt.ps1 for details.' }
$path=Join-Path $repo 'CMakeUserPresets.json'
if(Test-Path -LiteralPath $path) {
  $userPresets=Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
  Copy-Item -LiteralPath $path -Destination (Join-Path $repo '.build-audit/CMakeUserPresets.before-qt.json') -Force
} else { $userPresets=[pscustomobject]@{version=3} }
$userPresets.version=[Math]::Max(3,[int]$userPresets.version)
$configure=@($userPresets.configurePresets | Where-Object { $_ -and !$_.vendor.'nmsdk/qt-discovery/1.0'.generated })
$build=@($userPresets.buildPresets | Where-Object { $_ -and !$_.vendor.'nmsdk/qt-discovery/1.0'.generated })
$test=@($userPresets.testPresets | Where-Object { $_ -and !$_.vendor.'nmsdk/qt-discovery/1.0'.generated })
$count=0
foreach($kit in $kits) {
  $leaf=Split-Path $kit.Root -Leaf
  $sha=[Security.Cryptography.SHA256]::Create()
  try { $id=([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($kit.Root.ToLowerInvariant())))).Replace('-','').Substring(0,6).ToLowerInvariant() }
  finally { $sha.Dispose() }
  foreach($base in $BasePreset) {
    $null=$base -match '^win-vs(2019|2022|2026)-(ninja|msbuild)-(debug|release)-localqt$'
    $year=$Matches[1];$generator=$Matches[2];$config=$Matches[3]
    $installed=$installedBases[$base]
    if([version]$kit.BuiltWithMsvc -gt $installed.CompilerVersion) { Write-Warning "Skipping Qt $($kit.Version) for MSVC ${year}: kit needs $($kit.BuiltWithMsvc), installed $($installed.CompilerVersion)"; continue }
    $name="$base-qt$($kit.Version)-$leaf-$id" -replace '[^a-zA-Z0-9_.-]','-'
    if($name -in $configure.name -or $name -in $build.name -or $name -in $test.name) { throw "User preset name collision: $name" }
    $hostYear=switch(([version]$installed.Instance.installationVersion).Major) {16 {'2019'} 17 {'2022'} 18 {'2026'}}
    $display="Qt $($kit.Version) ($leaf) | MSVC $year $generator $config"
    if($hostYear -ne $year) { $display+=" (VS $hostYear)" }
    $vendor=@{'nmsdk/qt-discovery/1.0'=@{generated=$true};'microsoft.com/VisualStudioSettings/CMake/1.0'=@{vsInstanceVersion=([version]$installed.Instance.installationVersion).Major}}
    $cache=@{CMAKE_PREFIX_PATH=$kit.Root;QT_VERSION_MAJOR=([version]$kit.Version).Major.ToString();NMSDK_USE_WEBENGINE=if($WithWebEngine){'ON'}else{'OFF'}}
    $entry=@{name=$name;displayName=$display;description=$kit.Root;inherits=$base;environment=@{QT_ROOT=$kit.Root};cacheVariables=$cache;vendor=$vendor;condition=@{type='equals';lhs='${hostSystemName}';rhs='Windows'}}
    if($generator -eq 'msbuild') {
      # An installed v142 inside VS2022 can use the VS2022 MSBuild generator.
      $entry.generator=$installed.Generator
      $cache.CMAKE_GENERATOR_INSTANCE=$installed.Instance.installationPath
    } else {
      $toolset=switch($year){'2019'{'v142'} '2022'{'v143'} '2026'{'v145'}}
      $entry.toolset=@{value="$toolset,host=x64,version=$($installed.Version.Major).$($installed.Version.Minor)";strategy='external'}
    }
    $configure+=,$entry
    $build+=@{name=$name;displayName=$display;inherits=$base;configurePreset=$name;vendor=$vendor;condition=$entry.condition}
    $test+=@{name=$name;displayName=$display;inherits=$base;configurePreset=$name;vendor=$vendor;condition=$entry.condition}
    $count++
  }
}
if(!$count) { throw 'No kit is compatible with the selected preset toolsets' }
$userPresets | Add-Member -NotePropertyName configurePresets -NotePropertyValue @($configure) -Force
$userPresets | Add-Member -NotePropertyName buildPresets -NotePropertyValue @($build) -Force
$userPresets | Add-Member -NotePropertyName testPresets -NotePropertyValue @($test) -Force
$content=($userPresets | ConvertTo-Json -Depth 30)+[Environment]::NewLine
[IO.File]::WriteAllText($path,$content,[Text.UTF8Encoding]::new($false))
Write-Output "Registered $count local Qt presets in $path. In VSCode run CMake: Select Configure Preset."
