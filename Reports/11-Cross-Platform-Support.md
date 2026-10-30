> **Historical report.** See [Docs/Overview/](../Docs/Overview/) for current documentation.

# Кроссплатформенная поддержка

## Обзор

Нижние уровни Rdk построены вокруг абстракций, определённых в `Rdk/Core/System/`, а графическая и прикладная логика инкапсулируется в вариантах для разных UI-фреймворков (`Rdk/Core/Application/Bcb` и `Rdk/Core/Application/Qt`). Благодаря этому одна и та же бизнес-логика ядра переиспользуется на Windows, Linux и в старых Windows-сборках на Borland C++ Builder.

Основные принципы:

- **Базовые интерфейсы** (например, `UGenericMutex`, `UGenericEvent`, функции из `rdk_system.h`) задаются в платформонезависимом коде.
- **Реализации для конкретных платформ** находятся в подкаталогах `ANSI/`, `BCB/`, `Gcc/`, `Qt/`, `Win/` и выбираются на этапе сборки.
- **Прикладной уровень** подключает специализированные реализации серверов, UI и деплоймента в зависимости от доступного фреймворка: Qt (современные кроссплатформенные сборки) или VCL/Borland (наследие Win32).
- **Опции CMake** (`RdkDefines.cmake`) позволяют включать/выключать части функциональности (Python, TensorFlow, CUDA и т. д.), что упрощает сборку под разные окружения.

## Системные абстракции (`Rdk/Core/System`)

| Интерфейс | Назначение | Реализации |
|-----------|------------|------------|
| `rdk_system.h` | Файловые/временные операции, sleep, копирование, DLL loader | `ANSI/rdk_system.ansi.cpp`, `Gcc/rdk_system.gcc.cpp`, `Win/rdk_system.win.cpp`, `Qt/rdk_system.qt.cpp`, `BCB/rdk_system.bcb.cpp` |
| `UGenericMutex`, `UGenericEvent` | Универсальные блокировки и события | Qt (`Qt/UGenericMutex.qt.cpp`), Win32 (`Win/UGenericMutex.win.cpp`), Borland (`BCB/UGenericMutex.bcb.cpp`), GCC/pthreads (`Gcc/UGenericMutex.gcc.cpp`), ANSI fallback |
| `USharedMemoryLoader`, `UDllLoader` | Доступ к DLL/so и разделяемой памяти | Аналогичные подкаталоги (`Gcc/`, `Qt/`, `Win/`, `BCB/`, `ANSI/`) |

### Как это работает

1. **Интерфейсы** объявляются в головных заголовках и не зависят от ОС. Например, `UGenericMutex` определяет `shared_lock/exclusive_lock`, а фабрики `UCreateMutex/UCreateEvent` объявлены в `UGenericMutex.h`.
2. **Реализации** вносят конкретику: `Qt/UGenericMutex.qt.cpp` использует `QReadWriteLock`, `Win/UGenericMutex.win.cpp` — WinAPI `CreateMutex`, `Gcc/UGenericMutex.gcc.cpp` — `pthread_rwlock_t`.
3. **Сборка** подключает нужные файлы через CMake/`add_library`. Например, `Rdk/Build/Lib/CMake/CMakeLists.txt` добавляет `Rdk/Core/System/Qt/*.cpp`, а затем фильтрует ненужные реализации для текущей платформы.
4. **Высокоуровневый код** (например, `UEngineControlThread`) работает только с фабриками `UCreateEvent/UCreateMutex`. Благодаря этому потоки управления, RPC и хранилище компонентов не знают о конкретной ОС.

### Примеры

```33:95:Rdk/Core/System/Qt/UGenericMutex.qt.cpp
bool UGenericMutexQt::exclusive_lock(unsigned timeout)
{
 if(timeout == RDK_MUTEX_TIMEOUT)
  m_mutex.lockForWrite();
 else
 {
  return m_mutex.tryLockForWrite(timeout);
 }
```

```1:52:Rdk/Core/System/rdk_system.h
RDK_LIB_TYPE unsigned long long GetCurrentStartupTime(void);
RDK_LIB_TYPE void Sleep(int value);
RDK_LIB_TYPE int CreateNewDirectory(const char* path);
```

Эти функции реализованы отдельно для WinAPI, POSIX, Qt и Borland, но вызываются единообразно из ядра.

## Прикладной уровень (`Rdk/Core/Application`)

### Поддержка Borland C++ Builder (VCL)

- Директива `__BORLANDC__` включает заголовки из `Rdk/Core/Application/Bcb/`.
- Файлы `Application.bcb.*` и `URpcDispatcherVcl.*` адаптируют RPC/диспетчеризацию под VCL-цикл сообщений.
- `UEngineControlThread.cpp` и другие модули содержат ветви `#ifdef __BORLANDC__` для вызова Borland-специфичных API (например, `strcpy_s` vs `strncpy`).
- Используется WinAPI (`#ifdef WIN32`) для потоков/событий, так как Borland-ориентированные версии собираются только под Windows.

### Поддержка Qt (кроссплатформенные GUI/сервисы)

- Заголовки и реализации находятся в `Rdk/Core/Application/Qt/`.
- **Сетевой слой:** `UServerTransportTcpQt` наследует одновременно `QTcpServer` и абстрактный `UServerTransportTcp`, реализуя сетевое API через Qt sockets и `QBasicTimer`.
- **Деплойер проектов:** `UProjectDeployerQt` использует `QThread`, `QMutex`, `QtSql`, а на Linux дополнительно `libcurl` для скачивания шаблонов проектов.
- **Бэкенды RPC:** `URpcDecoderCommonQt` расширяет базовый декодер и управляет бинарными данными, оставаясь совместимым с Qt event loop.
- **UI-логика:** классы (например, `UServerControlQt`) переопределяют виртуальные методы управления каналами, но используют Qt-виджеты и сигналы/слоты.

### Выбор реализации

```1:26:Rdk/Core/Application/UApplication.h
#ifdef __BORLANDC__
#include "Bcb/Application.bcb.h"
#endif
```

Qt-варианты подключаются по умолчанию через `add_subdirectory(Rdk/Core/Application/Qt)` в CMake и активируются в сборках, где доступен Qt5.

## Потоки и события

`UEngineControlThread` демонстрирует, как абстракции связывают кроссплатформенные события/мьютексы с boost-потоками:

```41:66:Rdk/Core/Application/UEngineControlThread.cpp
CalcState = UCreateEvent(false);
CalcEnable = UCreateEvent(false);
CalcStarted = UCreateEvent(false);
CalculationNotInProgress = UCreateEvent(true);
Thread = boost::thread(boost::bind(&UEngineControlThread::Execute, boost::ref(*this)));
```

`UCreateEvent` вернёт Qt-, WinAPI- или POSIX-реализацию, в зависимости от собранного модуля `Rdk/Core/System`. Благодаря этому один и тот же движок расчётов работает и в GUI-приложении на Qt, и в консольной версии.

## Опции сборки и зависимости

`cmake/RdkDefines.cmake` описывает набор `option()` для подключения внешних библиотек:

```1:38:cmake/RdkDefines.cmake
option(RDK_USE_PYTHON "Use Python integration" OFF)
option(RDK_USE_DARKNET "Use Darknet integration" OFF)
option(RDK_USE_TENSORFLOW "Use Tensorflow integration" OFF)
option(RDK_USE_OPENCV "Use OpenCV" OFF)
...
if (RDK_USE_OPENCV)
  find_package(OpenCV QUIET)
  if (OpenCV_FOUND)
    add_compile_definitions(OPENCV_FOUND)
    include_directories(${OpenCV_INCLUDE_DIRS})
  endif()
endif()
```

Это позволяет собирать минимальные конфигурации (например, без Python/TensorFlow) или обогащённые версии, не меняя исходный код.

## Итоговая схема

```
                 +-------------------+
                 |  Ядро Rdk (Engine)|
                 +-------------------+
                         |
                  Абстракции (rdk_system.h,
                     UGenericMutex, ...)
                         |
        +----------------+----------------+
        |                                 |
  Платформенные реализации          UI / Application бэкенды
 (ANSI/Gcc/Win/Qt/BCB)            (Qt widgets, VCL адаптеры)
```

Благодаря строгому разделению интерфейсов и реализаций, компоненты и библиотеки (`Rdk-BasicLib`, `Nmsdk-PulseLib` и т. д.) не зависят от конкретной ОС или UI-стека, что обеспечивает переносимость между Linux и Windows и позволяет поддерживать исторические приложения на Borland C++ Builder.

