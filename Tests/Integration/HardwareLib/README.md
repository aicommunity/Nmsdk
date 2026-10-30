# HardwareLib integration tests

| Env | Meaning |
|-----|---------|
| `ARDUINO_SKIP_UPLOAD=1` | Connect-only; do not flash |
| `ARDUINO_SYNC_UPLOAD=1` | Blocking upload path |
| `WHEELED_PORT` | Serial device for wheeled L5 (`Test_WheeledHardwareIntegration`) |
| `NMSDK_ROOT` / `NMSDK_SOURCE_DIR` | Repo root for catalog / firmware paths |
| `RDK_HARDWARE_CATALOG_DIR` | Override catalog root |

Without `WHEELED_PORT`, wheeled L5 **skips** (pass).
