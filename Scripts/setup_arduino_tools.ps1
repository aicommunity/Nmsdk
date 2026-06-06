# Windows: download arduino-cli, install arduino:avr, copy avrdude to Bin/Platform/Win/ArduinoTools, build HEX.

param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [ValidateSet("Win")]
    [string]$Platform = "Win",
    [string]$ArduinoCliVersion = "",
    [switch]$SkipFirmwareBuild,
    [switch]$SkipAvrdudeCopy,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$PlatformDir = Join-Path $RepoRoot "Bin\Platform\Win"
$CliDir = Join-Path $PlatformDir "ArduinoCLI"
$CliExe = Join-Path $CliDir "arduino-cli.exe"
$DataDir = Join-Path $PlatformDir "ArduinoData"
$ToolsOut = Join-Path $PlatformDir "ArduinoTools"
$ToolsBin = Join-Path $ToolsOut "bin"
$ToolsEtc = Join-Path $ToolsOut "etc"
$BuildScript = Join-Path $RepoRoot "Scripts\build_arduino_firmware.ps1"

function Install-ArduinoCli {
    if ((Test-Path -LiteralPath $CliExe) -and -not $Force) {
        Write-Host "arduino-cli already present: $CliExe"
        return
    }

    New-Item -ItemType Directory -Force -Path $CliDir | Out-Null
    $zipPath = Join-Path $env:TEMP "arduino-cli-setup.zip"
    $extractDir = Join-Path $env:TEMP "arduino-cli-extract"

    $downloadUrl = $null
    if ($ArduinoCliVersion) {
        $downloadUrl = "https://github.com/arduino/arduino-cli/releases/download/v$ArduinoCliVersion/arduino-cli_${ArduinoCliVersion}_Windows_64bit.zip"
    }
    else {
        try {
            $release = Invoke-RestMethod -Uri "https://api.github.com/repos/arduino/arduino-cli/releases/latest" -Headers @{ "User-Agent" = "nmsdk-setup" }
            $asset = $release.assets | Where-Object { $_.name -match "Windows_64bit\.zip$" } | Select-Object -First 1
            if ($asset) {
                $downloadUrl = $asset.browser_download_url
                Write-Host "Using arduino-cli release: $($release.tag_name)"
            }
        }
        catch {
            Write-Warning "GitHub API failed: $_"
        }
    }

    if (-not $downloadUrl) {
        $downloadUrl = "https://github.com/arduino/arduino-cli/releases/download/v1.2.0/arduino-cli_1.2.0_Windows_64bit.zip"
        Write-Host "Using fallback arduino-cli URL: $downloadUrl"
    }

    Write-Host "Downloading arduino-cli..."
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing

    if (Test-Path -LiteralPath $extractDir) {
        Remove-Item -LiteralPath $extractDir -Recurse -Force
    }
    Expand-Archive -LiteralPath $zipPath -DestinationPath $extractDir -Force

    $found = Get-ChildItem -Path $extractDir -Filter "arduino-cli.exe" -Recurse -File | Select-Object -First 1
    if (-not $found) {
        Write-Error "arduino-cli.exe not found in downloaded archive"
    }
    Copy-Item -LiteralPath $found.FullName -Destination $CliExe -Force
    Write-Host "Installed: $CliExe"
}

function Install-AvrCore {
    New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
    $env:ARDUINO_DIRECTORIES_DATA = $DataDir
    $env:ARDUINO_DIRECTORIES_USER = $DataDir

    try {
        & $CliExe config init 2>$null
    }
    catch { }

    & $CliExe core update-index
    if ($LASTEXITCODE -ne 0) { throw "core update-index failed" }

    & $CliExe core install arduino:avr
    if ($LASTEXITCODE -ne 0) { throw "core install arduino:avr failed" }

    & $CliExe lib install "DHT sensor library"
    if ($LASTEXITCODE -ne 0) { throw "lib install DHT failed" }

    & $CliExe lib install Servo
    if ($LASTEXITCODE -ne 0) { throw "lib install Servo failed" }

    & $CliExe lib install Firmata
    if ($LASTEXITCODE -ne 0) { throw "lib install Firmata failed" }
}

function Copy-AvrdudeToArduinoTools {
    $avrdudeRoot = Join-Path $DataDir "packages\arduino\tools\avrdude"
    if (-not (Test-Path -LiteralPath $avrdudeRoot)) {
        Write-Error "avrdude not found under $avrdudeRoot"
    }

    $versions = Get-ChildItem -LiteralPath $avrdudeRoot -Directory | Sort-Object Name -Descending
    if (-not $versions) {
        Write-Error "No avrdude version directories under $avrdudeRoot"
    }
    $latest = $versions[0].FullName
    Write-Host "Copying avrdude from $latest"

    New-Item -ItemType Directory -Force -Path $ToolsBin, $ToolsEtc | Out-Null
    Copy-Item -Path (Join-Path $latest "bin\*") -Destination $ToolsBin -Recurse -Force

    $confSrc = Join-Path $latest "etc\avrdude.conf"
    if (-not (Test-Path -LiteralPath $confSrc)) {
        Write-Error "avrdude.conf not found: $confSrc"
    }
    Copy-Item -LiteralPath $confSrc -Destination (Join-Path $ToolsEtc "avrdude.conf") -Force

    $avrdudeExe = Join-Path $ToolsBin "avrdude.exe"
    if (-not (Test-Path -LiteralPath $avrdudeExe)) {
        Write-Error "avrdude.exe not found after copy: $avrdudeExe"
    }
    Write-Host "avrdude ready: $avrdudeExe"
}

function Build-Firmware {
    & $BuildScript -RepoRoot $RepoRoot -ArduinoCli $CliExe -ArduinoData $DataDir
    if ($LASTEXITCODE -ne 0) {
        throw "Firmware build failed"
    }
}

function Write-Summary {
    Write-Host ""
    Write-Host "========== Arduino tools setup complete =========="
    Write-Host "Arduino CLI:  $CliExe"
    Write-Host "Arduino data: $DataDir"
    Write-Host "avrdude:      $(Join-Path $ToolsBin 'avrdude.exe')"
    Write-Host "avrdude.conf: $(Join-Path $ToolsEtc 'avrdude.conf')"
    Write-Host "HEX root:     $(Join-Path $RepoRoot 'Bin\ArduinoFirmware')"
    Write-Host "Run NeuroModeler from: $PlatformDir"
    Write-Host "Set PortName (COMx) in Hardware test config before Upload."
    Write-Host "=================================================="
}

Install-ArduinoCli
Install-AvrCore

if (-not $SkipAvrdudeCopy) {
    Copy-AvrdudeToArduinoTools
}

if (-not $SkipFirmwareBuild) {
    Build-Firmware
}

Write-Summary
