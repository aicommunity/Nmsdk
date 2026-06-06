# Build bundled Arduino HEX into Bin/ArduinoFirmware/ (runtime default).
# Sketch sources remain under Libraries/Rdk-HardwareLib/Firmware/.
# Requires arduino-cli with working index and network.

param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$ArduinoCli = "",
    [string]$ArduinoData = "",
    [switch]$SkipLibraries
)

$ErrorActionPreference = "Stop"

$SrcFw = Join-Path $RepoRoot "Libraries\Rdk-HardwareLib\Firmware"
$BinFw = Join-Path $RepoRoot "Bin\ArduinoFirmware"
$Sketch = Join-Path $SrcFw "sensor_lab\sensor_lab.ino"

function Resolve-ArduinoCli {
    if ($ArduinoCli -and (Test-Path -LiteralPath $ArduinoCli)) {
        return (Resolve-Path -LiteralPath $ArduinoCli).Path
    }
    $fromEnv = $env:ARDUINO_CLI
    if ($fromEnv -and (Test-Path -LiteralPath $fromEnv)) {
        return (Resolve-Path -LiteralPath $fromEnv).Path
    }
    $cmd = Get-Command arduino-cli -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    Write-Error "arduino-cli not found. Install from https://arduino.github.io/arduino-cli/ or pass -ArduinoCli."
}

function Invoke-ArduinoCli {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$CliArgs)

    $prevData = $env:ARDUINO_DIRECTORIES_DATA
    $prevUser = $env:ARDUINO_DIRECTORIES_USER
    try {
        if ($ArduinoData) {
            $env:ARDUINO_DIRECTORIES_DATA = $ArduinoData
            $env:ARDUINO_DIRECTORIES_USER = $ArduinoData
        }
        & $script:CliExe @CliArgs
        if ($LASTEXITCODE -ne 0) {
            throw "arduino-cli failed (exit $LASTEXITCODE): arduino-cli $($CliArgs -join ' ')"
        }
    }
    finally {
        if ($null -ne $prevData) { $env:ARDUINO_DIRECTORIES_DATA = $prevData } else { Remove-Item Env:ARDUINO_DIRECTORIES_DATA -ErrorAction SilentlyContinue }
        if ($null -ne $prevUser) { $env:ARDUINO_DIRECTORIES_USER = $prevUser } else { Remove-Item Env:ARDUINO_DIRECTORIES_USER -ErrorAction SilentlyContinue }
    }
}

if (-not (Test-Path -LiteralPath $Sketch)) {
    Write-Error "Sketch not found: $Sketch"
}

$script:CliExe = Resolve-ArduinoCli

New-Item -ItemType Directory -Force -Path (Join-Path $BinFw "sensor_lab"), (Join-Path $BinFw "firmata") | Out-Null

try {
    Invoke-ArduinoCli config init
}
catch {
    # already initialized
}

Invoke-ArduinoCli core update-index
Invoke-ArduinoCli core install arduino:avr

if (-not $SkipLibraries) {
    Invoke-ArduinoCli lib install "DHT sensor library"
    Invoke-ArduinoCli lib install Servo
    Invoke-ArduinoCli lib install Firmata
}

function Build-SensorLab {
    param([string]$Fqbn, [string]$OutDir, [string]$Dest)

    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
    Invoke-ArduinoCli compile -b $Fqbn $Sketch --output-dir $OutDir
    $built = Join-Path $OutDir "sensor_lab.ino.hex"
    if (-not (Test-Path -LiteralPath $built)) {
        Write-Error "Build output not found: $built"
    }
    Copy-Item -LiteralPath $built -Destination $Dest -Force
}

Build-SensorLab -Fqbn "arduino:avr:uno" -OutDir (Join-Path $BinFw ".build_uno") -Dest (Join-Path $BinFw "sensor_lab\uno.hex")
Build-SensorLab -Fqbn "arduino:avr:mega" -OutDir (Join-Path $BinFw ".build_mega") -Dest (Join-Path $BinFw "sensor_lab\mega2560.hex")

if ($ArduinoData) {
    $FirmataIno = Join-Path $ArduinoData "libraries\Firmata\examples\StandardFirmata\StandardFirmata.ino"
}
else {
    $FirmataIno = Join-Path $env:USERPROFILE "Arduino\libraries\Firmata\examples\StandardFirmata\StandardFirmata.ino"
}

if (-not (Test-Path -LiteralPath $FirmataIno)) {
    Write-Error "StandardFirmata.ino not found at $FirmataIno"
}

$buildFirmataUno = Join-Path $BinFw ".build_firmata_uno"
$buildFirmataMega = Join-Path $BinFw ".build_firmata_mega"
New-Item -ItemType Directory -Force -Path $buildFirmataUno, $buildFirmataMega | Out-Null

Invoke-ArduinoCli compile -b arduino:avr:uno $FirmataIno --output-dir $buildFirmataUno
Copy-Item -LiteralPath (Join-Path $buildFirmataUno "StandardFirmata.ino.hex") `
    -Destination (Join-Path $BinFw "firmata\standard_firmata_uno.hex") -Force

Invoke-ArduinoCli compile -b arduino:avr:mega $FirmataIno --output-dir $buildFirmataMega
Copy-Item -LiteralPath (Join-Path $buildFirmataMega "StandardFirmata.ino.hex") `
    -Destination (Join-Path $BinFw "firmata\standard_firmata_mega2560.hex") -Force

Copy-Item -LiteralPath (Join-Path $SrcFw "manifest.json") -Destination (Join-Path $BinFw "manifest.json") -Force

New-Item -ItemType Directory -Force -Path (Join-Path $SrcFw "sensor_lab"), (Join-Path $SrcFw "firmata") | Out-Null
Copy-Item -Path (Join-Path $BinFw "sensor_lab\*.hex") -Destination (Join-Path $SrcFw "sensor_lab\") -Force
Copy-Item -Path (Join-Path $BinFw "firmata\*.hex") -Destination (Join-Path $SrcFw "firmata\") -Force

Write-Host "Done. Runtime HEX (Bin/ArduinoFirmware):"
Get-ChildItem -Path (Join-Path $BinFw "sensor_lab\*.hex"), (Join-Path $BinFw "firmata\*.hex") | Format-Table Name, Length
