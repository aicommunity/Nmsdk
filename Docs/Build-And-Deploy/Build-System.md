# Система сборки (Build System)

## RU

### Обзор

Проект Nmsdk использует **CMake** как основную систему сборки. Проект поддерживает сборку на платформах Linux и Windows.

### Основные настройки

- **Минимальная версия CMake:** 3.16
- **Стандарт C++:** C++20
- **Поддержка Qt5:** AUTOMOC, AUTOUIC, AUTORCC
- **Платформы:** Linux и Windows

### Структура сборки

Все скомпилированные файлы размещаются в:
- **Исполняемые файлы:** `Bin/Platform/<OS>/`
- **Библиотеки:** `Bin/Platform/<OS>/Lib.CMake/`

### Основные цели сборки

- `rdk.static.qt` - статическая библиотека ядра Rdk
- `Rdk-BasicLib.qt` - базовая библиотека
- `Rdk-CvBasicLib.qt` - библиотека компьютерного зрения
- `Rdk-HardwareLib.qt` - библиотека работы с железом
- `Nmsdk-MotionControlLib.qt` - библиотека управления движением
- `Nmsdk-PulseLib.qt` - библиотека импульсных нейросетей
- Приложения: NeuroModeler, NeuroModelerConsole

### Процесс сборки

```bash
# 1. Конфигурация
mkdir build
cd build
cmake ..

# 2. Сборка
cmake --build .
# или
make
# или (на Windows)
cmake --build . --config Release
```

**Процесс сборки:**

```mermaid
flowchart TB
    Start[Запуск CMake] --> Config[Конфигурация<br/>CMakeLists.txt]
    Config --> Detect[Определение платформы<br/>QT_FOUND, WIN32, UNIX]
    Detect --> SelectSys[Выбор системных абстракций<br/>System/Qt, System/Win, System/Gcc]
    SelectSys --> Compile[Компиляция<br/>gcc/clang/msvc]
    Compile --> Link[Линковка<br/>rdk.static.qt + библиотеки]
    Link --> Deploy[Деплой<br/>Bin/Platform/OS/]
    
    Config --> LoadLibs[Загрузка библиотек<br/>RdkLoadPredefinedLibraries]
    LoadLibs --> Compile
```

**Зависимости между модулями:**

```mermaid
flowchart LR
    RdkCore[rdk.static.qt] --> BasicLib[Rdk-BasicLib]
    RdkCore --> CvLib[Rdk-CvBasicLib]
    RdkCore --> HardwareLib[Rdk-HardwareLib]
    BasicLib --> PulseLib[Nmsdk-PulseLib]
    BasicLib --> MotionLib[Nmsdk-MotionControlLib]
    
    RdkCore --> App[NeuroModeler]
    BasicLib --> App
    CvLib --> App
```

### Зависимости

**Обязательные:**
- Qt5 (Core)
- C++20 компилятор (GCC, Clang, MSVC)

**Опциональные:**
- OpenCV - для Rdk-CvBasicLib
- ODE Solver - для Nmsdk-PulseLib

### Опции CMake и preset-ы

Ключевые флаги сборки задаются **в одном месте** — hidden preset `nmsdk-global-defaults` в [`CMakePresets.json`](../../CMakePresets.json). Все платформенные preset-ы (`win-msvc-base`, `win-vs2019-base`, `win-vs2022-base`, `linux-gcc-debug`) наследуют его через `"inherits": ["nmsdk-global-defaults"]`.

Тот же набор опций объявлен в [`cmake/RdkDefines.cmake`](../../cmake/RdkDefines.cmake) как `option()` и превращается в compile definitions. Это работает и при ручном `cmake ..` без preset-ов.

| Опция | Preset по умолчанию | Назначение |
|-------|---------------------|------------|
| `RDK_USE_ODESOLVER` | OFF | ODE solver в Nmsdk-PulseLib |
| `RDK_USE_PYTHON` | OFF | Python/Boost.Python |
| `RDK_USE_DARKNET` | OFF | Darknet |
| `RDK_USE_TENSORFLOW` | OFF | TensorFlow |
| `RDK_LLM_BUILD_EMBEDDED` | OFF | Встроенный llama.cpp (RDK LLM) |
| `RDK_UNICODE_RUN` | OFF | UTF-8 API (`RDK_UNICODE_RUN` define) |
| `NO_MOTION_CONTROL` | ON | Не регистрировать MotionControlLibrary в runtime |

Параллельная сборка: `CMAKE_BUILD_PARALLEL_LEVEL` задаётся в `nmsdk-global-defaults` через `$env{NUMBER_OF_PROCESSORS}` и наследуется всеми preset-ами. На Linux переменная может быть не задана — CMake использует значение по умолчанию.

**После изменения флагов** нужен re-configure (в Qt Creator: «Run CMake» или очистка каталога `build/`). Иначе CMake cache сохранит старые значения.

Локальные override-ы без правки общего preset-а: необязательный `CMakeUserPresets.json` с `"inherits": ["win-vs2019-debug-localqt"]` и точечными `cacheVariables`.

### См. также

- [Cross-Platform Support](Cross-Platform.md)
- [Build Windows](Build-Windows.md)
- [Build Linux](Build-Linux.md)
- [Reports/10-Build-System.md](../../Reports/10-Build-System.md) - детальное описание

---

## EN

### Overview

The Nmsdk project uses **CMake** as the main build system. The project supports building on Linux and Windows platforms.

### Main Settings

- **Minimum CMake version:** 3.16
- **C++ standard:** C++20
- **Qt5 support:** AUTOMOC, AUTOUIC, AUTORCC
- **Platforms:** Linux and Windows

### Build Structure

All compiled files are placed in:
- **Executables:** `Bin/Platform/<OS>/`
- **Libraries:** `Bin/Platform/<OS>/Lib.CMake/`

### Main Build Targets

- `rdk.static.qt` - static Rdk core library
- `Rdk-BasicLib.qt` - basic library
- `Rdk-CvBasicLib.qt` - computer vision library
- `Rdk-HardwareLib.qt` - hardware library
- `Nmsdk-MotionControlLib.qt` - motion control library
- `Nmsdk-PulseLib.qt` - spiking neural networks library
- Applications: NeuroModeler, NeuroModelerConsole

### Build Process

The build process follows these steps:
1. **Configuration**: CMake analyzes `CMakeLists.txt` files and detects platform, dependencies, and build options
2. **Platform Detection**: Determines which system abstraction implementation to use (Qt/Win/Gcc)
3. **Compilation**: Compiles all source files with C++20 standard
4. **Linking**: Links libraries and executables together
5. **Deployment**: Copies binaries and resources to `Bin/Platform/<OS>/`

The flowchart in the Russian section illustrates the complete build pipeline, including the selection of system abstractions and the dependency chain between modules.

### Dependencies

**Required:**
- Qt5 (Core)
- C++20 compiler (GCC, Clang, MSVC)

**Optional:**
- OpenCV - for Rdk-CvBasicLib
- ODE Solver - for Nmsdk-PulseLib

### CMake Options and Presets

Key build flags are defined **in one place** — hidden preset `nmsdk-global-defaults` in [`CMakePresets.json`](../../CMakePresets.json). All platform presets inherit it via `"inherits": ["nmsdk-global-defaults"]`.

The same options are declared in [`cmake/RdkDefines.cmake`](../../cmake/RdkDefines.cmake) as `option()` and become compile definitions. This also applies to manual `cmake ..` without presets.

| Option | Preset default | Purpose |
|--------|----------------|---------|
| `RDK_USE_ODESOLVER` | OFF | ODE solver in Nmsdk-PulseLib |
| `RDK_USE_PYTHON` | OFF | Python/Boost.Python |
| `RDK_USE_DARKNET` | OFF | Darknet |
| `RDK_USE_TENSORFLOW` | OFF | TensorFlow |
| `RDK_LLM_BUILD_EMBEDDED` | OFF | Embedded llama.cpp (RDK LLM) |
| `RDK_UNICODE_RUN` | OFF | UTF-8 API (`RDK_UNICODE_RUN` define) |
| `NO_MOTION_CONTROL` | ON | Skip MotionControlLibrary runtime registration |

Parallel builds: `CMAKE_BUILD_PARALLEL_LEVEL` is set in `nmsdk-global-defaults` via `$env{NUMBER_OF_PROCESSORS}` and inherited by all presets. On Linux the variable may be unset — CMake falls back to its default.

**After changing flags**, re-run configure (Qt Creator: «Run CMake» or clear the `build/` directory). Otherwise the CMake cache keeps old values.

Local overrides without editing the shared preset: optional `CMakeUserPresets.json` with `"inherits": ["win-vs2019-debug-localqt"]` and targeted `cacheVariables`.

### See Also

- [Cross-Platform Support](Cross-Platform.md)
- [Build Windows](Build-Windows.md)
- [Build Linux](Build-Linux.md)
- [Reports/10-Build-System.md](../../Reports/10-Build-System.md) - detailed description
