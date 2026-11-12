# Сборка на Windows (Build Windows)

## RU

### Обзор

Инструкции по сборке Nmsdk на платформе Windows.

### Требования

- Windows 10 или новее
- Visual Studio 2019 или новее (или MinGW)
- CMake 3.16 или новее
- Qt5 (Core)

### Процесс сборки

```bash
# 1. Создать директорию сборки
mkdir build
cd build

# 2. Конфигурация CMake
cmake .. -G "Visual Studio 16 2019" -A x64
# или для MinGW
cmake .. -G "MinGW Makefiles"

# 3. Сборка
cmake --build . --config Release
```

### Особенности Windows

- Используется WinAPI для системных операций
- Поддержка Visual Studio и MinGW
- Зависимости могут быть статически слинкованы

### См. также

- [Build System](Build-System.md)
- [Reports/26-Build-Windows.md](../../Reports/26-Build-Windows.md) - детальное описание

---

## EN

### Overview

Instructions for building Nmsdk on Windows platform.

### Requirements

- Windows 10 or newer
- Visual Studio 2019 or newer (or MinGW)
- CMake 3.16 or newer
- Qt5 (Core)

### Build Process

### Windows Specifics

- Uses WinAPI for system operations
- Supports Visual Studio and MinGW
- Dependencies can be statically linked

### See Also

- [Build System](Build-System.md)
- [Reports/26-Build-Windows.md](../../Reports/26-Build-Windows.md) - detailed description
