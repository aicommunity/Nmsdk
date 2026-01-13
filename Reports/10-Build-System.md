# Система сборки

## Обзор

Проект Nmsdk использует **CMake** как основную систему сборки. Проект поддерживает сборку на платформах Linux и Windows, с использованием различных компиляторов и IDE.

## Основные настройки CMake

### Корневой CMakeLists.txt

Расположен в корне проекта: `/home/user/Nmsdk/CMakeLists.txt`

#### Ключевые параметры

```cmake
cmake_minimum_required(VERSION 3.16)
project(Nmsdk LANGUAGES CXX)

# Стандарт C++
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Автоматическая обработка Qt
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)
```

#### Платформо-зависимые настройки

```cmake
if (WIN32)
  set(PLATFORM_DIR "Win")
else()
  set(PLATFORM_DIR "Linux")
endif()

set(DEPLOY_ROOT "${CMAKE_SOURCE_DIR}/Bin/Platform/${PLATFORM_DIR}")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${DEPLOY_ROOT}/Lib.CMake")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${DEPLOY_ROOT}/Lib.CMake")
```

#### Подключение модулей

```cmake
# Общие определения и зависимости
include(RdkDefines OPTIONAL)

# Подпроекты
add_subdirectory(Rdk/Build/Lib/CMake)              # rdk.static.qt
add_subdirectory(Libraries/Rdk-BasicLib/CMake)      # Rdk-BasicLib
add_subdirectory(Libraries/Rdk-CvBasicLib/CMake)     # Rdk-CvBasicLib
add_subdirectory(Libraries/Rdk-HardwareLib/CMake)   # Rdk-HardwareLib
add_subdirectory(Libraries/Nmsdk-MotionControlLib/CMake)  # Nmsdk-MotionControlLib
add_subdirectory(Libraries/Nmsdk-PulseLib/CMake)    # Nmsdk-PulseLib

# Приложения
add_subdirectory(Build/Qt/NeuroModeler/CMake)
add_subdirectory(Build/Qt/NeuroModelerConsole/CMake)
```

## Структура сборки

### Выходные директории

Все скомпилированные файлы размещаются в:

- **Исполняемые файлы**: `Bin/Platform/<OS>/`
- **Библиотеки**: `Bin/Platform/<OS>/Lib.CMake/`

Где `<OS>` - это `Win` или `Linux` в зависимости от платформы.

### Директория сборки

Промежуточные файлы сборки размещаются в директории `build/` (может быть настроена пользователем).

## Подпроекты

### Rdk (ядро)

**Путь**: `Rdk/Build/Lib/CMake/CMakeLists.txt`

**Цель**: `rdk.static.qt` (статическая библиотека)

**Зависимости**:
- Qt5 (Core)
- Стандартная библиотека C++

### Rdk-BasicLib

**Путь**: `Libraries/Rdk-BasicLib/CMake/CMakeLists.txt`

**Цель**: `Rdk-BasicLib.qt`

**Зависимости**:
- `rdk.static.qt`

### Rdk-CvBasicLib

**Путь**: `Libraries/Rdk-CvBasicLib/CMake/CMakeLists.txt`

**Цель**: `Rdk-CvBasicLib.qt`

**Зависимости**:
- `rdk.static.qt`
- OpenCV

### Rdk-HardwareLib

**Путь**: `Libraries/Rdk-HardwareLib/CMake/CMakeLists.txt`

**Цель**: `Rdk-HardwareLib.qt`

**Зависимости**:
- `rdk.static.qt`
- Qt5 (SerialPort)

### Nmsdk-PulseLib

**Путь**: `Libraries/Nmsdk-PulseLib/CMake/CMakeLists.txt`

**Цель**: `Nmsdk-PulseLib.qt`

**Зависимости**:
- `rdk.static.qt`
- `Rdk-BasicLib.qt`
- ODE Solver (опционально)

### Nmsdk-MotionControlLib

**Путь**: `Libraries/Nmsdk-MotionControlLib/CMake/CMakeLists.txt`

**Цель**: `Nmsdk-MotionControlLib.qt`

**Зависимости**:
- `rdk.static.qt`
- `Rdk-BasicLib.qt`
- `Rdk-CvBasicLib.qt`
- `Rdk-HardwareLib.qt`
- `Nmsdk-PulseLib.qt`
- Qt5 (Core)

## Общие определения (RdkDefines.cmake)

Файл `cmake/RdkDefines.cmake` содержит общие определения и настройки:

- Поиск зависимостей (OpenCV, Boost, Qt и др.)
- Определения компилятора
- Флаги компиляции
- Опциональные зависимости (Python, TensorFlow, Darknet)

### Пример использования

```cmake
# Включение опциональных библиотек
if(RDK_USE_PYTHON)
    find_package(Python3 REQUIRED)
endif()

if(RDK_USE_TENSORFLOW)
    find_package(TensorFlow REQUIRED)
endif()
```

## Зависимости

### Обязательные

- **Qt5** (Core) - базовая функциональность
- **C++20** компилятор (GCC, Clang, MSVC)

### Опциональные

- **OpenCV** - для Rdk-CvBasicLib
- **Python** - для Rdk-PyMachineLearningLib
- **TensorFlow** - для Rdk-TensorflowLib
- **Darknet** - для Rdk-DarknetLib
- **ODE Solver** - для Nmsdk-PulseLib (опционально)

## Процесс сборки

### 1. Конфигурация

```bash
mkdir build
cd build
cmake ..
```

### 2. Сборка

```bash
cmake --build .
# или
make
# или (на Windows)
cmake --build . --config Release
```

### 3. Установка (опционально)

```bash
cmake --install .
```

## Генераторы CMake

Проект поддерживает различные генераторы CMake:

- **Unix Makefiles** (Linux)
- **Ninja** (кроссплатформенный)
- **Visual Studio** (Windows)
- **CodeBlocks**
- **Eclipse CDT4**

### Пример с Ninja

```bash
cmake -G Ninja ..
ninja
```

## Платформо-зависимые особенности

### Linux

- Используется стандартный компилятор GCC или Clang
- Зависимости устанавливаются через пакетный менеджер
- Пути к библиотекам через pkg-config

### Windows

- Поддержка Visual Studio и MinGW
- Зависимости могут быть статически слинкованы
- Использование Windows API для некоторых компонентов

## Переменные окружения и опции

### Опции CMake

- `RDK_USE_PYTHON` - включить поддержку Python
- `RDK_USE_TENSORFLOW` - включить поддержку TensorFlow
- `RDK_USE_DARKNET` - включить поддержку Darknet
- `RDK_USE_ODESOLVER` - включить поддержку ODE Solver

### Пример

```bash
cmake -DRDK_USE_PYTHON=ON -DRDK_USE_TENSORFLOW=ON ..
```

## Альтернативные системы сборки

Проект также поддерживает файлы для других систем сборки (в директории `Build/`):

- **Qt Creator** (.pro файлы)
- **Visual Studio** (.sln, .vcxproj)
- **CodeBlocks** (.cbp)
- **Eclipse** (.mk файлы)
- **Borland C++ Builder** (.cbproj)

Эти файлы могут быть устаревшими и рекомендуется использовать CMake.

## Отладка сборки

### Включение отладочной информации

```bash
cmake -DCMAKE_BUILD_TYPE=Debug ..
```

### Вербозный вывод

```bash
cmake --build . --verbose
```

### Проверка зависимостей

```bash
cmake -L ..
```

## См. также

- [00-Project-Overview.md](00-Project-Overview.md) - общий обзор проекта
- [01-Rdk-Core-Structure.md](01-Rdk-Core-Structure.md) - структура ядра
- [02-Libraries-Overview.md](02-Libraries-Overview.md) - обзор библиотек и их зависимостей

