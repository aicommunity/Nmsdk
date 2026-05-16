#!/usr/bin/env bash
# Build bundled Arduino HEX files into Libraries/Rdk-HardwareLib/Firmware/.
# Requires arduino-cli with working index (downloads.arduino.cc) and network.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FW="${ROOT}/Libraries/Rdk-HardwareLib/Firmware"
SKETCH="${FW}/sensor_lab/sensor_lab.ino"
CLI="${ARDUINO_CLI:-arduino-cli}"

if ! command -v "${CLI}" >/dev/null 2>&1; then
  echo "arduino-cli not found. Install from https://arduino.github.io/arduino-cli/" >&2
  exit 1
fi

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

build_one "arduino:avr:uno" "${FW}/.build_uno" "${FW}/sensor_lab/uno.hex"
build_one "arduino:avr:mega" "${FW}/.build_mega" "${FW}/sensor_lab/mega2560.hex"

FIRMATA_INO="${HOME}/Arduino/libraries/Firmata/examples/StandardFirmata/StandardFirmata.ino"
if [[ ! -f "${FIRMATA_INO}" ]]; then
  echo "StandardFirmata.ino not found at ${FIRMATA_INO}" >&2
  exit 1
fi

mkdir -p "${FW}/firmata"
"${CLI}" compile -b arduino:avr:uno "${FIRMATA_INO}" --output-dir "${FW}/.build_firmata_uno"
cp "${FW}/.build_firmata_uno/StandardFirmata.ino.hex" "${FW}/firmata/standard_firmata_uno.hex"
"${CLI}" compile -b arduino:avr:mega "${FIRMATA_INO}" --output-dir "${FW}/.build_firmata_mega"
cp "${FW}/.build_firmata_mega/StandardFirmata.ino.hex" "${FW}/firmata/standard_firmata_mega2560.hex"

echo "Done. HEX files:"
ls -la "${FW}/sensor_lab/"*.hex "${FW}/firmata/"*.hex
