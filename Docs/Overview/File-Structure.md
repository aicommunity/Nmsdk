# Структура исходников проекта (File Structure)

## RU

### Обзор

Описание структуры директорий и файлов проекта Nmsdk.

### Корневая структура

```
Nmsdk/
├── Rdk/                    # Основной модуль (ядро)
│   ├── Core/               # Исходный код ядра
│   ├── Deploy/             # Заголовочные файлы для использования
│   ├── GUI/                # Графический интерфейс
│   ├── Tests/              # Тесты
│   └── ThirdParty/         # Сторонние библиотеки
│
├── Libraries/              # Библиотеки компонентов
│   ├── Rdk-BasicLib/       # Базовые компоненты
│   ├── Rdk-CvBasicLib/     # Компьютерное зрение
│   ├── Rdk-HardwareLib/    # Работа с железом
│   ├── Nmsdk-PulseLib/     # Импульсные нейронные сети
│   ├── Nmsdk-MotionControlLib/  # Управление движением
│   ├── Rdk-PyMachineLearningLib/  # Python ML интеграция
│   ├── Rdk-TensorflowLib/  # TensorFlow интеграция
│   └── Rdk-DarknetLib/     # Darknet интеграция
│
├── Bin/                    # Скомпилированные бинарники и конфиги
│   ├── Configs/            # Конфигурационные файлы
│   ├── ClDesc/             # Описания классов компонентов
│   ├── Help/               # Справочная документация
│   ├── Styles/             # Стили и темы
│   └── Platform/           # Платформенные артефакты
│
├── Build/                  # Файлы сборки (CMake, Qt, VS, etc.)
├── Docs/                   # Документация
├── Docs.old/               # Старая документация
├── Reports/                # Отчеты и анализ
└── CMakeLists.txt          # Корневой файл сборки
```

### Структура Rdk

```
Rdk/
├── Core/                   # Исходный код ядра
│   ├── Application/        # Приложение, RPC, сервер
│   ├── Engine/             # Движок, компоненты, окружение
│   ├── Graphics/           # Графика и визуализация
│   ├── Math/              # Математические утилиты
│   ├── Serialize/         # Сериализация (XML, Binary)
│   ├── System/            # Системные утилиты
│   ├── Utilities/         # Вспомогательные утилиты
│   └── Console/           # Консольный движок
├── Deploy/                # Заголовочные файлы
│   └── Include/           # Публичные заголовки
├── GUI/                   # Графический интерфейс
│   └── Qt/               # Qt реализация GUI
├── Tests/                 # Тесты
│   ├── Unit/             # Юнит-тесты
│   └── Integration/      # Интеграционные тесты
└── ThirdParty/           # Сторонние библиотеки
```

### Структура Libraries

Каждая библиотека следует общей структуре:

```
LibraryName/
├── Core/                  # Исходный код компонентов
│   ├── Component1.h
│   ├── Component1.cpp
│   └── ...
├── Deploy/                # Заголовочные файлы
│   └── Include/
│       └── Lib.h          # Главный заголовок
├── CMake/                 # Файлы сборки CMake
│   └── CMakeLists.txt
├── Build/                 # Файлы сборки для различных IDE
├── Docs/                  # Документация библиотеки
└── Tests/                 # Тесты библиотеки
```

### Структура Bin

```
Bin/
├── Configs/               # Конфигурационные файлы проектов
├── ClDesc/                # Описания классов компонентов (XML)
├── Help/                  # Справочная документация
│   ├── en/               # Английская версия
│   └── ru/               # Русская версия
├── Styles/                # Стили и темы GUI
└── Platform/              # Платформенные артефакты
    ├── Linux/            # Linux специфичные файлы
    └── Win/              # Windows специфичные файлы
```

### См. также

- [Архитектура системы](Architecture-Overview.md) - архитектурное описание
- [Build System](../Build-And-Deploy/Build-System.md) - система сборки

---

## EN

### Overview

Description of Nmsdk project directory and file structure.

### Root Structure

### Rdk Structure

### Libraries Structure

Each library follows a common structure.

### Bin Structure

### See Also

- [System Architecture](Architecture-Overview.md) - architectural description
- [Build System](../Build-And-Deploy/Build-System.md) - build system
