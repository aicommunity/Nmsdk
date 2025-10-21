# Applications

Эта папка содержит исходные файлы приложений проекта NMSDK.

## Структура

- `NeuroModeler/` - Графическое приложение для моделирования нейронных сетей
- `NeuroModelerConsole/` - Консольная версия приложения

## Сборка

Все приложения собираются через CMake из корневой директории проекта:

```bash
mkdir build && cd build
cmake ..
make
```

Бинарные файлы будут помещены в `Bin/Platform/Linux/` или `Bin/Platform/Win/`.

## Миграция от старой структуры

Ранее файлы приложений находились в `Build/Qt/`. Эта структура была удалена 
в пользу использования только CMake для сборки проекта.

## Структура файлов

Каждое приложение содержит:
- `main.cpp` - основной исходный файл приложения
- `CMakeLists.txt` - конфигурация сборки CMake

## Зависимости

Приложения используют следующие компоненты:
- RDK Core Library (rdk.static.qt)
- Rdk-BasicLib.qt
- Nmsdk-PulseLib.qt
- Nmsdk-MotionControlLib.qt
- Rdk-CvBasicLib.qt
- Rdk-HardwareLib.qt
- Qt5 (Core, Widgets, Network, Charts для NeuroModeler)
- Boost (опционально для некоторых компонентов)
