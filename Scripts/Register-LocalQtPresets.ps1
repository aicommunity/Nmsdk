[CmdletBinding()]
param(
  [string[]]$Root = @(),
  [string[]]$SearchRoot = @(),
  [string[]]$BasePreset = @('win-vs2022-ninja-debug-localqt','win-vs2022-ninja-release-localqt'),
  [switch]$WithWebEngine
)
# Machine-specific Qt paths belong only in the ignored CMakeUserPresets.json.
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot -Parent
$shared=Get-Content (Join-Path $repo 'CMakePresets.json') -Raw -Encoding UTF8 | ConvertFrom-Json
foreach($name in $BasePreset) {
  if($name -notmatch '^win-vs(2019|2022|2026)-(ninja|msbuild)-(debug|release)-localqt$' -or
     $name -notin $shared.configurePresets.name) { throw "Unsupported local Qt base preset: $name" }
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
    $maximum = switch($year) { '2019' {[version]'19.29'} '2022' {[version]'19.49'} '2026' {[version]'19.59'} }
    if([version]$kit.BuiltWithMsvc -gt $maximum) { Write-Warning "Skipping Qt $($kit.Version) for MSVC ${year}: kit compiler is newer"; continue }
    $name="$base-qt$($kit.Version)-$leaf-$id" -replace '[^a-zA-Z0-9_.-]','-'
    if($name -in $configure.name -or $name -in $build.name -or $name -in $test.name) { throw "User preset name collision: $name" }
    $display="Qt $($kit.Version) ($leaf) | MSVC $year $generator $config"
    $vendor=@{'nmsdk/qt-discovery/1.0'=@{generated=$true}}
    $cache=@{CMAKE_PREFIX_PATH=$kit.Root;QT_VERSION_MAJOR=([version]$kit.Version).Major.ToString();NMSDK_USE_WEBENGINE=if($WithWebEngine){'ON'}else{'OFF'}}
    $configure+=@{name=$name;displayName=$display;description=$kit.Root;inherits=$base;environment=@{QT_ROOT=$kit.Root};cacheVariables=$cache;vendor=$vendor}
    $build+=@{name=$name;displayName=$display;inherits=$base;configurePreset=$name;vendor=$vendor}
    $test+=@{name=$name;displayName=$display;inherits=$base;configurePreset=$name;vendor=$vendor}
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
