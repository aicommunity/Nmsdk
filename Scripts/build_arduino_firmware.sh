#!/usr/bin/env bash
# Build all bundled AVR HEX files into Bin/ArduinoFirmware and Firmware/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_FW="${ROOT}/Libraries/Rdk-HardwareLib/Firmware"
BIN_FW="${ROOT}/Bin/ArduinoFirmware"
CLI="${ARDUINO_CLI:-arduino-cli}"

if ! command -v "${CLI}" >/dev/null 2>&1; then
  echo "arduino-cli not found. Install it or set ARDUINO_CLI." >&2
  exit 1
fi

"${CLI}" core update-index
"${CLI}" core install arduino:avr@1.8.8

if [[ "${NMSDK_SKIP_ARDUINO_LIBRARIES:-0}" != "1" ]]; then
  libraries=(
    "Adafruit Unified Sensor@1.1.15" "Adafruit BusIO@1.17.4"
    "DHT sensor library@1.4.7" "Servo@1.3.0" "Firmata@2.5.9"
    "Adafruit BME280 Library@2.3.0" "Adafruit_VL53L0X@1.2.5"
    "Adafruit MPU6050@2.2.9" "Adafruit INA219@1.2.3"
    "Adafruit PWM Servo Driver Library@3.0.3" "Adafruit GFX Library@1.12.6"
    "Adafruit SSD1306@2.5.17" "LiquidCrystal I2C@1.1.2"
    "Adafruit NeoPixel@1.15.5" "LedControl@1.0.6" "RF24@1.6.2" "MFRC522@1.4.12"
  )
  for library in "${libraries[@]}"; do
    "${CLI}" lib install "${library}"
  done
fi

user_dir="${ARDUINO_DIRECTORIES_USER:-}"
if [[ -z "${user_dir}" ]]; then
  user_dir="$("${CLI}" config get directories.user)"
fi
if [[ -z "${user_dir}" ]]; then
  user_dir="${HOME}/Arduino"
fi
firmata_ino="${user_dir}/libraries/Firmata/examples/StandardFirmata/StandardFirmata.ino"
if [[ ! -f "${firmata_ino}" ]]; then
  echo "StandardFirmata.ino not found: ${firmata_ino}" >&2
  exit 1
fi

mkdir -p "${BIN_FW}"
build_one() {
  local fqbn="$1"
  local sketch_dir="$2"
  local board_key="$3"
  local sketch_id="$4"
  local out_dir="${BIN_FW}/.build_${sketch_id}_${board_key}"
  mkdir -p "${out_dir}" "${BIN_FW}/${sketch_id}" "${sketch_dir}"
  "${CLI}" compile -b "${fqbn}" "${sketch_dir}" --output-dir "${out_dir}"
  local hex
  hex="$(find "${out_dir}" -maxdepth 1 -type f -name '*.hex' ! -name '*with_bootloader*' -print -quit)"
  if [[ -z "${hex}" ]]; then
    echo "HEX output not found for ${sketch_id} (${board_key})" >&2
    exit 1
  fi
  cp "${hex}" "${BIN_FW}/${sketch_id}/${board_key}.hex"
  cp "${hex}" "${sketch_dir}/${board_key}.hex"
}

for board in "uno:arduino:avr:uno" "mega2560:arduino:avr:mega"; do
  board_key="${board%%:*}"
  fqbn="${board#*:}"
  out_dir="${BIN_FW}/.build_firmata_${board_key}"
  mkdir -p "${out_dir}" "${BIN_FW}/firmata" "${SRC_FW}/firmata"
  "${CLI}" compile -b "${fqbn}" "${firmata_ino}" --output-dir "${out_dir}"
  hex="$(find "${out_dir}" -maxdepth 1 -type f -name '*.hex' ! -name '*with_bootloader*' -print -quit)"
  if [[ -z "${hex}" ]]; then
    echo "StandardFirmata HEX output not found (${board_key})" >&2
    exit 1
  fi
  name="standard_firmata_${board_key}.hex"
  cp "${hex}" "${BIN_FW}/firmata/${name}"
  cp "${hex}" "${SRC_FW}/firmata/${name}"
done

sketches=(sensor_lab nmsdk_sensor_hub nmsdk_motor_hub nmsdk_i2c_hub
          nmsdk_display_hub nmsdk_pixel_hub nmsdk_radio_hub nmsdk_uart_device_hub)
for sketch in "${sketches[@]}"; do
  for board in "uno:arduino:avr:uno" "mega2560:arduino:avr:mega"; do
    board_key="${board%%:*}"
    fqbn="${board#*:}"
    build_one "${fqbn}" "${SRC_FW}/${sketch}" "${board_key}" "${sketch}"
  done
done

cp "${SRC_FW}/manifest.json" "${BIN_FW}/manifest.json"
echo "Built bundled AVR HEX files for Uno and Mega 2560 into ${BIN_FW}"
