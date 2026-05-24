#!/usr/bin/env bash
# Build bundled Arduino HEX into Bin/ArduinoFirmware/ (runtime default).
# Sketch sources remain under Libraries/Rdk-HardwareLib/Firmware/.
# Requires arduino-cli with working index and network.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_FW="${ROOT}/Libraries/Rdk-HardwareLib/Firmware"
BIN_FW="${ROOT}/Bin/ArduinoFirmware"
SKETCH="${SRC_FW}/sensor_lab/sensor_lab.ino"
CLI="${ARDUINO_CLI:-arduino-cli}"

if ! command -v "${CLI}" >/dev/null 2>&1; then
  echo "arduino-cli not found. Install from https://arduino.github.io/arduino-cli/" >&2
  exit 1
fi

mkdir -p "${BIN_FW}/sensor_lab" "${BIN_FW}/firmata"

"${CLI}" config init 2>/dev/null || true
"${CLI}" core update-index
"${CLI}" core install arduino:avr
"${CLI}" lib install "DHT sensor library"
"${CLI}" lib install Servo
"${CLI}" lib install Firmata

build_one() {
  local fqbn="$1"
  local outdir="$2"
  local dest="$3"
  mkdir -p "${outdir}"
  "${CLI}" compile -b "${fqbn}" "${SKETCH}" --output-dir "${outdir}"
  cp "${outdir}/sensor_lab.ino.hex" "${dest}"
}

build_one "arduino:avr:uno" "${BIN_FW}/.build_uno" "${BIN_FW}/sensor_lab/uno.hex"
build_one "arduino:avr:mega" "${BIN_FW}/.build_mega" "${BIN_FW}/sensor_lab/mega2560.hex"

FIRMATA_INO="${HOME}/Arduino/libraries/Firmata/examples/StandardFirmata/StandardFirmata.ino"
if [[ ! -f "${FIRMATA_INO}" ]]; then
  echo "StandardFirmata.ino not found at ${FIRMATA_INO}" >&2
  exit 1
fi

"${CLI}" compile -b arduino:avr:uno "${FIRMATA_INO}" --output-dir "${BIN_FW}/.build_firmata_uno"
cp "${BIN_FW}/.build_firmata_uno/StandardFirmata.ino.hex" "${BIN_FW}/firmata/standard_firmata_uno.hex"
"${CLI}" compile -b arduino:avr:mega "${FIRMATA_INO}" --output-dir "${BIN_FW}/.build_firmata_mega"
cp "${BIN_FW}/.build_firmata_mega/StandardFirmata.ino.hex" "${BIN_FW}/firmata/standard_firmata_mega2560.hex"

cp "${SRC_FW}/manifest.json" "${BIN_FW}/manifest.json"

# Optional: keep Libraries tree in sync for dev/docs
mkdir -p "${SRC_FW}/sensor_lab" "${SRC_FW}/firmata"
cp "${BIN_FW}/sensor_lab/"*.hex "${SRC_FW}/sensor_lab/"
cp "${BIN_FW}/firmata/"*.hex "${SRC_FW}/firmata/"

echo "Done. Runtime HEX (Bin/ArduinoFirmware):"
ls -la "${BIN_FW}/sensor_lab/"*.hex "${BIN_FW}/firmata/"*.hex
