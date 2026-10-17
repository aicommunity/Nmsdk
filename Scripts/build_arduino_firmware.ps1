param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$ArduinoCli = "",
    [string]$ArduinoData = "",
    [string]$ArduinoUser = "",
    [switch]$SkipLibraries
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$SrcFw = Join-Path $RepoRoot "Libraries\Rdk-HardwareLib\Firmware"
$BinFw = Join-Path $RepoRoot "Bin\ArduinoFirmware"
$ManifestPath = Join-Path $SrcFw "manifest.json"

function Resolve-ArduinoCli {
    if ($script:ArduinoCli -and (Test-Path -LiteralPath $script:ArduinoCli)) {
        return (Resolve-Path -LiteralPath $script:ArduinoCli).Path
    }
    $fromEnv = $env:ARDUINO_CLI
    if ($fromEnv -and (Test-Path -LiteralPath $fromEnv)) {
        return (Resolve-Path -LiteralPath $fromEnv).Path
    }
    $cmd = Get-Command arduino-cli -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    throw "arduino-cli not found. Install it or pass -ArduinoCli."
}

function Invoke-ArduinoCli {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$CliArgs)
    & $script:CliExe @CliArgs
    if ($LASTEXITCODE -ne 0) {
        throw "arduino-cli failed (exit $LASTEXITCODE): arduino-cli $($CliArgs -join ' ')"
    }
}

function Install-RequiredLibraries {
    $libraries = @(
        "Adafruit Unified Sensor@1.1.15",
        "Adafruit BusIO@1.17.4",
        "DHT sensor library@1.4.7",
        "Servo@1.3.0",
        "Firmata@2.5.9",
        "Adafruit BME280 Library@2.3.0",
        "Adafruit_VL53L0X@1.2.5",
        "Adafruit MPU6050@2.2.9",
        "Adafruit INA219@1.2.3",
        "Adafruit PWM Servo Driver Library@3.0.3",
        "Adafruit GFX Library@1.12.6",
        "Adafruit SSD1306@2.5.17",
        "LiquidCrystal I2C@1.1.2",
        "Adafruit NeoPixel@1.15.5",
        "LedControl@1.0.6",
        "RF24@1.6.2",
        "MFRC522@1.4.12"
    )
    foreach ($library in $libraries) {
        Invoke-ArduinoCli lib install $library
    }
}

function Build-Sketch {
    param(
        [string]$SketchId,
        [string]$SketchName,
        [string]$Fqbn,
        [string]$BoardKey
    )

    $sketchDir = Join-Path $SrcFw $SketchId
    $inoPath = Join-Path $sketchDir "$SketchName.ino"
    if (-not (Test-Path -LiteralPath $inoPath)) {
        throw "Sketch not found: $inoPath"
    }

    $outDir = Join-Path $BinFw ".build_${SketchId}_${BoardKey}"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    Invoke-ArduinoCli compile -b $Fqbn $sketchDir --output-dir $outDir

    $hex = Get-ChildItem -LiteralPath $outDir -Filter "*.hex" -File |
        Where-Object { $_.Name -notmatch "with_bootloader" } |
        Select-Object -First 1
    if (-not $hex) {
        throw "HEX output not found for $SketchId ($BoardKey) in $outDir"
    }

    $runtimeDir = Join-Path $BinFw $SketchId
    New-Item -ItemType Directory -Force -Path $runtimeDir, $sketchDir | Out-Null
    $runtimeHex = Join-Path $runtimeDir "$BoardKey.hex"
    $sourceHex = Join-Path $sketchDir "$BoardKey.hex"
    Copy-Item -LiteralPath $hex.FullName -Destination $runtimeHex -Force
    Copy-Item -LiteralPath $hex.FullName -Destination $sourceHex -Force
}

$script:CliExe = Resolve-ArduinoCli
$previousData = $env:ARDUINO_DIRECTORIES_DATA
$previousUser = $env:ARDUINO_DIRECTORIES_USER
try {
    if ($ArduinoData) {
        $ArduinoData = [System.IO.Path]::GetFullPath($ArduinoData)
        New-Item -ItemType Directory -Force -Path $ArduinoData | Out-Null
        $env:ARDUINO_DIRECTORIES_DATA = $ArduinoData
        if (-not $ArduinoUser) {
            $ArduinoUser = $ArduinoData
        }
    }
    if ($ArduinoUser) {
        $ArduinoUser = [System.IO.Path]::GetFullPath($ArduinoUser)
        New-Item -ItemType Directory -Force -Path $ArduinoUser | Out-Null
        $env:ARDUINO_DIRECTORIES_USER = $ArduinoUser
    }

    New-Item -ItemType Directory -Force -Path $BinFw | Out-Null
    Invoke-ArduinoCli core update-index
    Invoke-ArduinoCli core install arduino:avr@1.8.8
    if (-not $SkipLibraries) {
        Install-RequiredLibraries
    }

    $userDir = $ArduinoUser
    if (-not $userDir -and $ArduinoData) {
        $userDir = $ArduinoData
    }
    if (-not $userDir) {
        $userDir = (& $script:CliExe config get directories.user).Trim()
    }
    if (-not $userDir) {
        $userDir = Join-Path $env:USERPROFILE "Documents\Arduino"
    }
    $firmataIno = Join-Path $userDir "libraries\Firmata\examples\StandardFirmata\StandardFirmata.ino"
    if (-not (Test-Path -LiteralPath $firmataIno)) {
        throw "StandardFirmata.ino not found: $firmataIno"
    }

    foreach ($board in @(@{ Key = "uno"; Fqbn = "arduino:avr:uno" },
                          @{ Key = "mega2560"; Fqbn = "arduino:avr:mega" })) {
        $outDir = Join-Path $BinFw ".build_firmata_$($board.Key)"
        New-Item -ItemType Directory -Force -Path $outDir | Out-Null
        Invoke-ArduinoCli compile -b $board.Fqbn $firmataIno --output-dir $outDir
        $hex = Get-ChildItem -LiteralPath $outDir -Filter "*.hex" -File |
            Where-Object { $_.Name -notmatch "with_bootloader" } |
            Select-Object -First 1
        if (-not $hex) {
            throw "StandardFirmata HEX not found for $($board.Key)."
        }
        $runtimeDir = Join-Path $BinFw "firmata"
        $sourceDir = Join-Path $SrcFw "firmata"
        New-Item -ItemType Directory -Force -Path $runtimeDir, $sourceDir | Out-Null
        $name = "standard_firmata_$($board.Key).hex"
        Copy-Item -LiteralPath $hex.FullName -Destination (Join-Path $runtimeDir $name) -Force
        Copy-Item -LiteralPath $hex.FullName -Destination (Join-Path $sourceDir $name) -Force
    }

    $sketches = @(
        @{ Id = "sensor_lab"; Name = "sensor_lab" },
        @{ Id = "nmsdk_sensor_hub"; Name = "nmsdk_sensor_hub" },
        @{ Id = "nmsdk_motor_hub"; Name = "nmsdk_motor_hub" },
        @{ Id = "nmsdk_i2c_hub"; Name = "nmsdk_i2c_hub" },
        @{ Id = "nmsdk_display_hub"; Name = "nmsdk_display_hub" },
        @{ Id = "nmsdk_pixel_hub"; Name = "nmsdk_pixel_hub" },
        @{ Id = "nmsdk_radio_hub"; Name = "nmsdk_radio_hub" },
        @{ Id = "nmsdk_uart_device_hub"; Name = "nmsdk_uart_device_hub" }
    )
    foreach ($sketch in $sketches) {
        Build-Sketch -SketchId $sketch.Id -SketchName $sketch.Name `
            -Fqbn "arduino:avr:uno" -BoardKey "uno"
        Build-Sketch -SketchId $sketch.Id -SketchName $sketch.Name `
            -Fqbn "arduino:avr:mega" -BoardKey "mega2560"
    }

    Copy-Item -LiteralPath $ManifestPath -Destination (Join-Path $BinFw "manifest.json") -Force
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    foreach ($firmware in $manifest.bundled) {
        foreach ($board in $firmware.boards.PSObject.Properties) {
            $relativeHex = [string]$board.Value.hex
            $hexPath = Join-Path $BinFw ($relativeHex -replace '/', '\')
            if (-not (Test-Path -LiteralPath $hexPath)) {
                throw "Manifest entry '$($firmware.id)'/$($board.Name) points to missing HEX: $relativeHex"
            }
        }
    }

    Write-Host "Built AVR firmware for Uno and Mega 2560 into $BinFw"
}
finally {
    if ($null -ne $previousData) { $env:ARDUINO_DIRECTORIES_DATA = $previousData }
    else { Remove-Item Env:ARDUINO_DIRECTORIES_DATA -ErrorAction SilentlyContinue }
    if ($null -ne $previousUser) { $env:ARDUINO_DIRECTORIES_USER = $previousUser }
    else { Remove-Item Env:ARDUINO_DIRECTORIES_USER -ErrorAction SilentlyContinue }
}
