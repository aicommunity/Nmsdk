# Rdk-HardwareLib

## RU

### Назначение

**Rdk-HardwareLib** — компоненты для работы с Arduino (USB serial): подключение, прошивка bundled HEX, custom протокол `sensor_lab`, Standard Firmata, GUI pinout в NeuroModeler.

### Компоненты (актуальные ClassName)

- **ArduinoBoard** — порт, upload, heartbeat
- **ArduinoSensorSketch** — sensor_lab, команды, матрица
- **ArduinoFirmata** — Firmata pin control
- **ArduinoAdc** — ADC через связанный Firmata
- **ArduinoDcDemo** — DC demo (один узел, CustomLink + sensor_lab_v1)

Property API (edge/state) и поток движка: [Architecture.md](../../Libraries/Rdk-HardwareLib/Docs/Architecture.md), [API-Overview.md](../../Libraries/Rdk-HardwareLib/Docs/API-Overview.md).

### Зависимости

- Qt (Core, SerialPort, Widgets, Svg для GUI)
- `rdk.static.qt`, `Rdk-BasicLib.qt`
- Targets: `Rdk-HardwareLib.qt`, `Rdk-HardwareLib.gui`

### Документация в репозитории

[Libraries/Rdk-HardwareLib/Docs](../../Libraries/Rdk-HardwareLib/Docs/) — README, Architecture, API, компоненты, Transport/Protocol/GUI.

Прошивки и чеклист: [Libraries/Rdk-HardwareLib/Firmware/README.md](../../Libraries/Rdk-HardwareLib/Firmware/README.md).

### Миграция

Старые `Arduino`, `ADC`, `DC` → см. [Component-Catalog.md](../../Libraries/Rdk-HardwareLib/Docs/Component-Catalog.md) и `Scripts/migrate_arduino_classnames.py`.

---

## EN

### Purpose

**Rdk-HardwareLib** provides Arduino hardware components for NeuroModeler (serial, firmware, sensor_lab, Firmata, GUI).

### Main components

`ArduinoBoard`, `ArduinoSensorSketch`, `ArduinoFirmata`, `ArduinoAdc`, `ArduinoDcDemo`.

### Dependencies

Qt SerialPort; libraries `Rdk-HardwareLib.qt` and `Rdk-HardwareLib.gui`.

### Documentation

[Libraries/Rdk-HardwareLib/Docs](../../Libraries/Rdk-HardwareLib/Docs/).
