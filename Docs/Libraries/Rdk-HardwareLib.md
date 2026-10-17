# Rdk-HardwareLib

## RU

### Назначение

**Rdk-HardwareLib** — компоненты для работы с Arduino/ESP32 (USB serial): подключение, прошивка bundled HEX, custom протокол `sensor_lab` / Nmsdk hub, Standard Firmata, wheeled robots, GUI pinout в NeuroModeler.

### Компоненты (актуальные ClassName)

- **ArduinoBoard** — порт, upload, heartbeat
- **ArduinoSensorSketch** — sensor_lab, команды, матрица
- **ArduinoFirmata** — Firmata pin control
- **ArduinoAdc** — ADC через связанный Firmata
- **ArduinoDcDemo** — DC demo (один узел, CustomLink + sensor_lab_v1)
- **ArduinoDeviceIO** / **ArduinoCustomFirmware** — модули DeviceIO / произвольный hub plugin
- **Esp32Board** — ESP32 serial (DTR/RTS off, Connect-only P0)
- **ArduinoWheeledRobot** / **Esp32WheeledRobot** — open-loop Left/Right PWM+Dir (Nmsdk motor hub)
- **WaveRover** — Waveshare UGV JSON (`T:11`)

Property API и поток движка: [Architecture.md](../../Libraries/Rdk-HardwareLib/Docs/Architecture.md), [API-Overview.md](../../Libraries/Rdk-HardwareLib/Docs/API-Overview.md).  
Wheeled ADR: [WheeledRobots.md](../../Libraries/Rdk-HardwareLib/Docs/WheeledRobots.md).

### Зависимости

- Qt (Core, SerialPort, Widgets, Svg для GUI)
- `rdk.static.qt`, `Rdk-BasicLib.qt`
- Targets: `Rdk-HardwareLib.qt`, `Rdk-HardwareLib.gui`

### Документация в репозитории

[Libraries/Rdk-HardwareLib/Docs](../../Libraries/Rdk-HardwareLib/Docs/) — README, Architecture, API, компоненты, Transport/Protocol/GUI, Modules-Catalog.

Прошивки и чеклист: [Libraries/Rdk-HardwareLib/Firmware/README.md](../../Libraries/Rdk-HardwareLib/Firmware/README.md).

### Миграция

Старые `Arduino`, `ADC`, `DC` → см. [Component-Catalog.md](../../Libraries/Rdk-HardwareLib/Docs/Component-Catalog.md) и `Scripts/migrate_arduino_classnames.py`.

---

## EN

### Purpose

**Rdk-HardwareLib** provides Arduino/ESP32 hardware components for NeuroModeler (serial, firmware, sensor_lab, Firmata, wheeled hubs, WaveRover JSON, GUI).

### Main components

`ArduinoBoard`, `ArduinoSensorSketch`, `ArduinoFirmata`, `ArduinoAdc`, `ArduinoDcDemo`, `ArduinoDeviceIO`, `ArduinoCustomFirmware`, `Esp32Board`, `ArduinoWheeledRobot`, `Esp32WheeledRobot`, `WaveRover`.

### Dependencies

Qt SerialPort; libraries `Rdk-HardwareLib.qt` and `Rdk-HardwareLib.gui`.

### Documentation

[Libraries/Rdk-HardwareLib/Docs](../../Libraries/Rdk-HardwareLib/Docs/).
