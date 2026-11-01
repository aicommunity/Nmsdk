# Сборка на Linux (Build Linux)

## RU

### Обзор

Инструкции по сборке Nmsdk на платформе Linux.

### Требования

- Linux (Ubuntu 20.04+, Debian 11+, или аналогичные)
- GCC 9+ или Clang 10+
- CMake 3.16+
- Qt5 (Core)

### Установка зависимостей

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential cmake qtbase5-dev
```

**Fedora:**
```bash
sudo dnf install gcc-c++ cmake qt5-qtbase-devel
```

### Процесс сборки

```bash
# 1. Создать директорию сборки
mkdir build
cd build

# 2. Конфигурация CMake
cmake ..

# 3. Сборка
cmake --build . -j$(nproc)
# или
make -j$(nproc)
```

### Особенности Linux

- Используется стандартный компилятор GCC или Clang
- Зависимости устанавливаются через пакетный менеджер
- Пути к библиотекам через pkg-config

### См. также

- [Build System](Build-System.md)
- [Cross-Platform Support](Cross-Platform.md)

---

## EN

### Overview

Instructions for building Nmsdk on Linux platform.

### Requirements

- Linux (Ubuntu 20.04+, Debian 11+, or similar)
- GCC 9+ or Clang 10+
- CMake 3.16+
- Qt5 (Core)

### Installing Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential cmake qtbase5-dev
```

**Fedora:**
```bash
sudo dnf install gcc-c++ cmake qt5-qtbase-devel
```

### Build Process

### Linux Specifics

- Uses standard GCC or Clang compiler
- Dependencies installed via package manager
- Library paths via pkg-config

### See Also

- [Build System](Build-System.md)
- [Cross-Platform Support](Cross-Platform.md)
