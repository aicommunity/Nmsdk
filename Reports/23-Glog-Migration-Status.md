# Миграция логирования на glog - Статус

## Выполненные задачи

### 1. Добавление glog как зависимости
- ✅ Добавлен поиск glog в `Rdk/CMakeLists.txt`
- ✅ Настроена линковка glog для всех целевых библиотек
- ✅ Добавлен `#include <glog/logging.h>` в необходимые файлы

### 2. Создание макросов-оберток
- ✅ Создан `Rdk/Deploy/Include/rdk_logging.h` с ленивыми макросами (`RLOG`, `VRLOG`, `RLOG_IF`, `RLOG_COUNTED`)
- ✅ Реализованы вспомогательные функции `DispatchLazy()`, `ChannelLog()`, `SystemLog()` и `GlobalLog()`, которые маппят уровни на glog
- ✅ Fallback без glog полностью удалён: теперь сборка требует `RDK_USE_GLOG`

- ✅ `ProcessExceptionRaw`/`UExceptionLogger` используют `RDK::Logging::ChannelLog()` для отправки сообщений в glog
- ✅ `LogMessageEx` вызывает `ProcessException` для правильной обработки исключений
- ✅ Сохранена функциональность добавления логов в `LogList` для GUI виджета
- ✅ Сохранена правильная обработка препроцессоров, постпроцессоров и обработчиков исключений

### 4. Инициализация glog
- ✅ Добавлена инициализация glog в `UApplication::Init()`
- ✅ Настроены уровни логирования через `FLAGS_minloglevel` и `FLAGS_v`
- ✅ `UGlogGuiSink` регистрируется как sink для доставки сообщений в GUI
- ✅ Добавлен shutdown glog и снятие всех sink'ов в `UApplication::UnInit()`

### 5. Управление каталогами логов
- ✅ `UApplication::CalcCurrentLogDir()` и `UpdateLoggers()` переработаны для автоматического выбора:
  - при открытом проекте — `ProjectPath/EventsLog/`
  - без проекта — `WorkDirectory/EventsLog/`
  - фиксированный путь из ini переопределяет оба варианта
- ✅ Добавлена функция `ApplyPrimaryLogDestination()` для синхронизации `FLAGS_log_dir` и `google::SetLogDestination`
- ✅ Введён `UFileLogSink`, который по флагу конфигурации дублирует логи в рабочую папку
- ✅ Состояние зеркалирования (`EventsLogEnabled`) подхватывается из `TProjectConfig` и обновляется при любом изменении конфигурации

### 6. Устранение дублирования каналов
- ✅ `UExceptionLogger::ProcessException()` больше не пересылает сообщения системного канала (`ChannelIndex = -1`) в глобальный
- ✅ При необходимости можно использовать только глобальный канал, установив положительный `ChannelIndex`

## Текущая реализация

### Архитектура логирования

1. **Вызов логирования**: `LogMessage()` → `LogMessageEx()` → создание исключения → `ProcessException()`
2. **Обработка исключения**: `ProcessException()` → форматирование с префиксом канала → `ProcessExceptionRaw()`
3. **Логирование в glog**: `ProcessExceptionRaw()` → `RDK::Logging::ChannelLog()`/`DispatchLazy()` → glog
4. **Добавление в LogList/GUI**: `ProcessExceptionRaw()` передаёт текст в `UGlogGuiSink`, откуда читает `ULoggerWidget`
5. **Обработка GUI**: `UGlogGuiSink::ReadMessages()` используется Qt-виджетом напрямую (без зависимостей от старого `ProcessLog()`)

### Маппинг уровней логирования

- `RDK_EX_FATAL` → `LOG(FATAL)`
- `RDK_EX_ERROR` → `LOG(ERROR)`
- `RDK_EX_WARNING` → `LOG(WARNING)`
- `RDK_EX_INFO` → `LOG(INFO)`
- `RDK_EX_DEBUG` → `VLOG(1)` (условно, если `DebugMode`)
- `RDK_EX_APP` → `LOG(INFO)` с префиксом "[APP]"

### Сохраненная функциональность

- ✅ GUI виджет логирования (`ULoggerWidget`) работает через `LogList`
- ✅ Правильное форматирование сообщений с префиксом канала
- ✅ Обработка исключений (препроцессоры, постпроцессоры, обработчики)
- ✅ Поддержка нескольких каналов логирования
- ✅ Глобальный логгер (`RDK_GLOB_MESSAGE`)

## Известные моменты

- ❗ Каналы `RDK_SYS_MESSAGE` и `RDK_GLOB_MESSAGE` теперь логируются независимо; системный канал больше не продублируется автоматически в глобальный.

## Следующие шаги (опционально)

1. **Замена прямых вызовов LogMessage**: постепенно переходить на макросы glog там, где это оправдано.
2. **Глобальные настройки зеркалирования**: при необходимости добавить в ini отдельный ключ для управления `UFileLogSink`.
3. **Ротация логов**: внедрить очистку/ограничение размера каталога `EventsLog`.

## Новые расширения (ноябрь 2025)

- Добавлены ленивые макросы (`RLOG`, `VRLOG`, `RLOG_COUNTED`, `RLOG_IF`) для безопасного формирования сообщений без лишних `std::string`.
- Появилась конфигурация уровней логирования на канал:
  - Настраивается через проект (`EventsLogMode`, `DebugMode`), переменные окружения (`RDK_LOG_LEVEL`, `RDK_LOG_SYS_LEVEL`, `RDK_LOG_GLOB_LEVEL`, `RDK_LOG_CHANNELS`, `RDK_LOG_VERBOSITY`) и флаги командной строки (`--log-level`, `--log-channel-level`, `--log-verbosity`, `--log-sys-level`, `--log-glob-level`).
  - Ленивая маршрутизация реализована в `rdk_logging.h` / `rdk_engine_support.cpp`.
- Введён реестр приёмников логов:
  - Интерфейс `RDK::Logging::ILogSink` и функции `RegisterLogSink`/`UnregisterLogSink`.
  - Стандартные приёмники (`UGlogGuiSink`, `UFileLogSink`) подключены через реестр.
- Добавлен JSON-приёмник (`UJsonLogSink`). Активируется установкой `RDK_LOG_JSON_PATH=/tmp/rdk-log.json`; каждая запись пишется отдельной JSON-строкой.
- Для интеграционных тестов добавлен `Test_Logging_Sinks`, гарантирующий, что новый JSON-sink создаёт корректные записи.

## Файлы изменены

- `Rdk/CMakeLists.txt` - добавление glog
- `Rdk/Deploy/Include/rdk_logging.h` - ленивые макросы и вспомогательные функции (создан)
- `Rdk/Deploy/Include/rdk.h` - включение rdk_logging.h
- `Rdk/Core/Engine/UExceptionLogger.cpp` — интеграция с glog, блокировка дублирования каналов
- `Rdk/Core/Engine/UFileLogSink.{h,cpp}` — новый sink для зеркалирования логов
- `Rdk/Core/Application/UApplication.cpp/.h` — выбор каталогов, регистрация sink'ов, новые флаги
- `Rdk/Deploy/Include/rdk_engine_support.cpp` — настройка системного/глобального логгеров
- `Rdk/Deploy/Include/rdk_logging.h` — макросы + fallback

## Статус сборки

✅ Проект успешно собирается без ошибок
✅ Все цели собраны (NeuroModeler, NeuroModelerConsole, rdk.static.qt)

