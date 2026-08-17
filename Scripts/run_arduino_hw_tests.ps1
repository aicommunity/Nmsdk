# Unattended Arduino Mega hardware tests (serial exclusive: ctest -j1).
param(
    [string]$Port = $(if ($env:ARDUINO_TEST_PORT) { $env:ARDUINO_TEST_PORT } else { "COM3" }),
    [int]$BoardProfile = $(if ($env:ARDUINO_BOARD_PROFILE) { [int]$env:ARDUINO_BOARD_PROFILE } else { 1 }),
    [string]$Preset = "win-vs2019-release-localqt",
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

$env:ARDUINO_TEST_PORT = $Port
$env:ARDUINO_BOARD_PROFILE = "$BoardProfile"
$env:NMSDK_SOURCE_DIR = $RepoRoot
$env:NMSDK_ROOT = $RepoRoot

$FirmwareDir = Join-Path $RepoRoot "Bin\ArduinoFirmware"
if (Test-Path -LiteralPath (Join-Path $FirmwareDir "manifest.json")) {
    $env:RDK_HARDWARE_FIRMWARE_DIR = $FirmwareDir
}

$Avrdude = Join-Path $RepoRoot "Bin\Platform\Win\ArduinoTools\bin\avrdude.exe"
if (Test-Path -LiteralPath $Avrdude) {
    $env:AVRDUDE = $Avrdude
    $env:PATH = "$(Split-Path -Parent $Avrdude);$env:PATH"
}

$BuildDir = Join-Path $RepoRoot "build\$Preset"

Write-Host "Building hardware live tests ($Preset)..."
cmake --build --preset $Preset --target Test_ArduinoHardwareIntegration Test_ArduinoFirmataExtendedProtocols Test_ArduinoHubLive --parallel
if ($LASTEXITCODE -ne 0) {
    throw "cmake --build failed with exit $LASTEXITCODE"
}

Write-Host "Running live tests on $Port (profile=$BoardProfile), ctest -j1..."
# Integration first so StandardFirmata is on the board before TD-001 / hubs.
ctest --test-dir $BuildDir -j1 --output-on-failure -R "ArduinoHardwareIntegration"
if ($LASTEXITCODE -ne 0) { throw "ArduinoHardwareIntegration failed" }

ctest --test-dir $BuildDir -j1 --output-on-failure -R "ArduinoFirmataExtended"
if ($LASTEXITCODE -ne 0) { throw "ArduinoFirmataExtended failed" }

ctest --test-dir $BuildDir -j1 --output-on-failure -R "ArduinoHubLive"
if ($LASTEXITCODE -ne 0) { throw "ArduinoHubLive failed" }

Write-Host "All Arduino live tests passed."
