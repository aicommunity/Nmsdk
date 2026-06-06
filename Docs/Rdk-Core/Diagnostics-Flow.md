> **Note:** Root-level diagnostic flow doc. Related: [Engine-Detailed.md](../../Rdk/Docs/Engine-Detailed.md), `TProjectLoadDiagnostics` in `Rdk/Core/Engine/`.

# Поток диагностики при загрузке проекта

## RU

## Обзор

Данный документ описывает поток диагностики (`TProjectLoadDiagnostics`) через всю цепочку загрузки проекта, от открытия проекта до загрузки отдельных компонентов и установки связей.

## Структура диагностики

**Файл:** `Rdk/Core/Engine/TProjectLoadDiagnostics.h`

```cpp
struct TProjectLoadDiagnostics
{
  std::vector<std::string> errors;      // Список ошибок
  std::vector<std::string> warnings;    // Список предупреждений
  bool modelExists;                      // Существует ли модель
  bool modelEmpty;                       // Пустая ли модель
  std::vector<int> componentsCount;     // Количество компонентов по каналам
  std::vector<std::string> missingFiles;// Отсутствующие файлы
  std::vector<int> failedChannels;      // Каналы с ошибками
  bool isValid;                         // Общая валидность
  int channelsLoaded;                    // Успешно загруженные каналы
  int channelsTotal;                     // Общее количество каналов
};
```

## Диаграмма потока диагностики

```mermaid
flowchart TD
    Start[OpenProject с diagnostics] --> Init[Инициализация diagnostics]
    Init --> ForEach[Для каждого канала]
    ForEach --> LoadModel[LoadModelFromFile с diagnostics]
    LoadModel --> SetEngine[SetLoadDiagnostics в Engine]
    SetEngine --> CAPI[MModel_LoadComponent]
    CAPI --> GetEngine[GetEngineLock channel_index]
    GetEngine --> GetDiag[GetLoadDiagnostics из Engine]
    GetDiag --> LoadComp[LoadComponent с diagnostics]
    LoadComp --> CheckClass{Класс существует?}
    CheckClass -->|Нет| AddError1[Добавить в diag->errors]
    CheckClass -->|Да| CreateObj{Объект создан?}
    CreateObj -->|Нет| AddError2[Добавить в diag->errors]
    CreateObj -->|Да| AddComp[AddComponent]
    AddComp --> Recursive[LoadComponent рекурсивно с diagnostics]
    Recursive --> SetLinks[SetComponentInternalLinks с diagnostics]
    SetLinks --> CreateLinks[CreateLinks с diagnostics]
    CreateLinks --> ForLink[Для каждой связи]
    ForLink --> FindSource{Источник найден?}
    FindSource -->|Нет| AddError3[Добавить в diag->errors]
    FindSource -->|Да| FindDest{Приемник найден?}
    FindDest -->|Нет| AddError4[Добавить в diag->errors]
    FindDest -->|Да| FindPortOut{Порт-источник найден?}
    FindPortOut -->|Нет| AddError5[Добавить в diag->errors]
    FindPortOut -->|Да| FindPortIn{Порт-приемник найден?}
    FindPortIn -->|Нет| AddError6[Добавить в diag->errors]
    FindPortIn -->|Да| CheckType{Типы совместимы?}
    CheckType -->|Нет| LogError["Логировать ошибку<br/>НЕ накапливать"]
    CheckType -->|Да| Connect[Установить связь]
    AddError1 --> NextComp[Следующий компонент]
    AddError2 --> NextComp
    AddError3 --> NextLink[Следующая связь]
    AddError4 --> NextLink
    AddError5 --> NextLink
    AddError6 --> NextLink
    LogError --> NextLink
    Connect --> NextLink
    NextLink --> MoreLinks{Еще связи?}
    MoreLinks -->|Да| ForLink
    MoreLinks -->|Нет| NextComp
    NextComp --> MoreComps{Еще компоненты?}
    MoreComps -->|Да| LoadComp
    MoreComps -->|Нет| ClearDiag[SetLoadDiagnostics nullptr]
    ClearDiag --> Validate[ValidateProject использует diagnostics]
    Validate --> End[Возврат diagnostics]
```

## Детальное описание потока

### Этап 1: Инициализация диагностики

**Файл:** `Rdk/Core/Application/UApplication.cpp:2037-2040`

```cpp
if(diagnostics)
{
  *diagnostics = TProjectLoadDiagnostics();
}
```

**Действия:**
- Очистка всех полей диагностики
- Инициализация счетчиков

### Этап 2: Передача диагностики в LoadModelFromFile

**Файл:** `Rdk/Core/Application/UApplication.cpp:2131`

```cpp
is_loaded = LoadModelFromFile(i, model_file_path, diagnostics);
```

**Действия:**
- Диагностика передается по указателю
- Все ошибки загрузки файла накапливаются в `diagnostics->errors`

### Этап 3: Временное хранение в Engine

**Файл:** `Rdk/Core/Application/UApplication.cpp:2882-2888`

```cpp
RDK::UELockPtr<RDK::UEngine> engine_lock = RDK::GetEngineLock(channel_index);
if(engine_lock.Get())
{
  engine_lock.Get()->SetLoadDiagnostics(diagnostics);
}
```

**Действия:**
- Диагностика сохраняется в поле `UEngine::LoadDiagnostics`
- Это временное хранилище для передачи через C API

**Проблема:** Если `GetEngineLock` возвращает другой Engine (например, при переключении канала), диагностика теряется.

### Этап 4: Получение диагностики в Model_LoadComponent

**Файл:** `Rdk/Core/Engine/UEngine.cpp:5615`

```cpp
void* load_diagnostics = GetLoadDiagnostics();
if(!cont->LoadComponent(&XmlStorage, true, load_diagnostics))
  return RDK_E_MODEL_LOAD_COMPONENT_FAIL;
```

**Действия:**
- Диагностика извлекается из временного хранилища Engine
- Передается в `LoadComponent` как `void*` для обратной совместимости

**Проблема:** Если `GetLoadDiagnostics()` возвращает `nullptr`, диагностика не передается дальше.

### Этап 5: Накопление ошибок в LoadComponent

**Файл:** `Rdk/Core/Engine/UNet.cpp:789-895`

```cpp
TProjectLoadDiagnostics* diag = diagnostics ? static_cast<TProjectLoadDiagnostics*>(diagnostics) : nullptr;

// При ошибке:
if(diag)
{
  diag->errors.push_back(error_msg);
}
```

**Действия:**
- Диагностика приводится к правильному типу
- Ошибки накапливаются в `diag->errors`
- Проверка `if(diag)` предотвращает разыменование `nullptr`

**Обрабатываемые ошибки:**
1. Несуществующий класс: `EClassNameNotExist` → `diag->errors`
2. Неудачное создание: `TakeObject` возвращает `nullptr` → `diag->errors`
3. Неудачное добавление: `AddComponent` возвращает `ForbiddenId` → `diag->errors`
4. Неудачная загрузка дочернего: `LoadComponent` возвращает `false` → `diag->errors`

### Этап 6: Накопление ошибок в CreateLink

**Файл:** `Rdk/Core/Engine/UNet.h:399-422`

```cpp
TProjectLoadDiagnostics* diag = diagnostics ? static_cast<TProjectLoadDiagnostics*>(diagnostics) : nullptr;

if(!pitem)
{
  if(diag)
    diag->errors.push_back("Source component 'X' not found");
  return false;
}
```

**Действия:**
- Диагностика приводится к правильному типу
- Ошибки отсутствующих компонентов накапливаются в `diag->errors`

**Обрабатываемые ошибки:**
1. Компонент-источник не найден → `diag->errors`
2. Компонент-приемник не найден → `diag->errors`

### Этап 7: Накопление ошибок в ConnectToItem

**Файл:** `Rdk/Core/Engine/UConnector.cpp:457-483`

```cpp
TProjectLoadDiagnostics* diag = diagnostics ? static_cast<TProjectLoadDiagnostics*>(diagnostics) : nullptr;

if(!i_item_property)
{
  if(diag)
    diag->errors.push_back("Output port 'X' not found in component 'Y'");
  return false;
}
```

**Действия:**
- Диагностика приводится к правильному типу
- Ошибки отсутствующих портов накапливаются в `diag->errors`

**Обрабатываемые ошибки:**
1. Порт-источник не найден → `diag->errors`
2. Порт-приемник не найден → `diag->errors`

**Не обрабатывается:**
- Несовместимость типов портов → только логирование, не накопление

## Проблемы потока диагностики

### Проблема 1: Потеря диагностики между LoadModelFromFile и Model_LoadComponent

**Местоположение:** `Rdk/Core/Application/UApplication.cpp:2882-2893`

**Описание:**
- Диагностика устанавливается в Engine через `SetLoadDiagnostics`
- Затем вызывается `MModel_LoadComponent`, который создает новый `UELockPtr`
- Если между установкой и получением произошло переключение канала, диагностика может быть потеряна

**Решение:**
- Убедиться, что `GetEngineLock(channel_index)` всегда возвращает указатель на один и тот же Engine
- Добавить проверку, что диагностика не потерялась
- Рассмотреть альтернативный подход: передача через параметры

### Проблема 2: Диагностика может быть nullptr

**Местоположение:** Различные места в коде

**Описание:**
- Во многих местах проверяется `if(diag)`, но если диагностика не передана, ошибки теряются
- Это нормально для обратной совместимости, но может скрывать ошибки

**Решение:**
- Убедиться, что диагностика передается во все рекурсивные вызовы
- Добавить логирование, если диагностика не передана (для отладки)

### Проблема 3: Ошибка несовместимости типов не накапливается

**Местоположение:** `Rdk/Core/Engine/UConnector.cpp:485-494`

**Описание:**
- При несовместимости типов портов ошибка логируется, но не накапливается в диагностике
- Это критическая ошибка, которая должна быть в диагностике

**Решение:**
- Добавить накопление ошибки в `diag->errors` при несовместимости типов

## Рекомендации по улучшению

### Рекомендация 1: Единый механизм передачи диагностики

**Текущее состояние:**
- Диагностика передается через временное хранилище в Engine
- Это работает, но не идеально

**Предложение:**
- Рассмотреть передачу диагностики через параметры функций
- Это потребует изменения C API, но будет более надежно

### Рекомендация 2: Накопление всех ошибок

**Текущее состояние:**
- Большинство ошибок накапливаются
- Но ошибка несовместимости типов не накапливается

**Предложение:**
- Добавить накопление всех ошибок, включая несовместимость типов

### Рекомендация 3: Накопление предупреждений

**Текущее состояние:**
- Предупреждения о неактивных компонентах только логируются

**Предложение:**
- Добавить накопление предупреждений в `diag->warnings`

## Примеры использования

### Пример 1: Валидация конфигурации

```cpp
TProjectLoadDiagnostics diagnostics;
bool loaded = app->OpenProject("project.ini", &diagnostics);

if(!diagnostics.errors.empty())
{
  std::cout << "Errors:" << std::endl;
  for(const auto& error : diagnostics.errors)
    std::cout << "  - " << error << std::endl;
}

if(!diagnostics.warnings.empty())
{
  std::cout << "Warnings:" << std::endl;
  for(const auto& warning : diagnostics.warnings)
    std::cout << "  - " << warning << std::endl;
}
```

### Пример 2: Проверка валидности

```cpp
TProjectLoadDiagnostics diagnostics = app->ValidateProject("project.ini");

if(!diagnostics.isValid)
{
  // Обработка ошибок
  return false;
}
```

## См. также

- [Engine Architecture](../../Rdk/Docs/Architecture/Engine-Architecture.md) — загрузка компонентов
- [Serialize Architecture](../../Rdk/Docs/Architecture/Serialize-Architecture.md) — сериализация и связи
- [Архитектура Application](Application-Architecture.md)

---

## EN

## Overview

This document describes the diagnostic flow (`TProjectLoadDiagnostics`) through the entire project load chain, from opening a project to loading individual components and establishing links.

## Diagnostic structure

**File:** `Rdk/Core/Engine/TProjectLoadDiagnostics.h`

```cpp
struct TProjectLoadDiagnostics
{
  std::vector<std::string> errors;      // Список ошибок
  std::vector<std::string> warnings;    // Список предупреждений
  bool modelExists;                      // Существует ли модель
  bool modelEmpty;                       // Пустая ли модель
  std::vector<int> componentsCount;     // Количество компонентов по каналам
  std::vector<std::string> missingFiles;// Отсутствующие файлы
  std::vector<int> failedChannels;      // Каналы с ошибками
  bool isValid;                         // Общая валидность
  int channelsLoaded;                    // Успешно загруженные каналы
  int channelsTotal;                     // Общее количество каналов
};
```

## Diagnostic flow diagram

```mermaid
flowchart TD
    Start[OpenProject с diagnostics] --> Init[Инициализация diagnostics]
    Init --> ForEach[Для каждого канала]
    ForEach --> LoadModel[LoadModelFromFile с diagnostics]
    LoadModel --> SetEngine[SetLoadDiagnostics в Engine]
    SetEngine --> CAPI[MModel_LoadComponent]
    CAPI --> GetEngine[GetEngineLock channel_index]
    GetEngine --> GetDiag[GetLoadDiagnostics из Engine]
    GetDiag --> LoadComp[LoadComponent с diagnostics]
    LoadComp --> CheckClass{Класс существует?}
    CheckClass -->|Нет| AddError1[Добавить в diag->errors]
    CheckClass -->|Да| CreateObj{Объект создан?}
    CreateObj -->|Нет| AddError2[Добавить в diag->errors]
    CreateObj -->|Да| AddComp[AddComponent]
    AddComp --> Recursive[LoadComponent рекурсивно с diagnostics]
    Recursive --> SetLinks[SetComponentInternalLinks с diagnostics]
    SetLinks --> CreateLinks[CreateLinks с diagnostics]
    CreateLinks --> ForLink[Для каждой связи]
    ForLink --> FindSource{Источник найден?}
    FindSource -->|Нет| AddError3[Добавить в diag->errors]
    FindSource -->|Да| FindDest{Приемник найден?}
    FindDest -->|Нет| AddError4[Добавить в diag->errors]
    FindDest -->|Да| FindPortOut{Порт-источник найден?}
    FindPortOut -->|Нет| AddError5[Добавить в diag->errors]
    FindPortOut -->|Да| FindPortIn{Порт-приемник найден?}
    FindPortIn -->|Нет| AddError6[Добавить в diag->errors]
    FindPortIn -->|Да| CheckType{Типы совместимы?}
    CheckType -->|Нет| LogError["Логировать ошибку<br/>НЕ накапливать"]
    CheckType -->|Да| Connect[Установить связь]
    AddError1 --> NextComp[Следующий компонент]
    AddError2 --> NextComp
    AddError3 --> NextLink[Следующая связь]
    AddError4 --> NextLink
    AddError5 --> NextLink
    AddError6 --> NextLink
    LogError --> NextLink
    Connect --> NextLink
    NextLink --> MoreLinks{Еще связи?}
    MoreLinks -->|Да| ForLink
    MoreLinks -->|Нет| NextComp
    NextComp --> MoreComps{Еще компоненты?}
    MoreComps -->|Да| LoadComp
    MoreComps -->|Нет| ClearDiag[SetLoadDiagnostics nullptr]
    ClearDiag --> Validate[ValidateProject использует diagnostics]
    Validate --> End[Возврат diagnostics]
```

## Detailed flow description

### Stage 1: Initialize diagnostics

**File:** `Rdk/Core/Application/UApplication.cpp:2037-2040`

```cpp
if(diagnostics)
{
  *diagnostics = TProjectLoadDiagnostics();
}
```

**Actions:**
- Clear all diagnostic fields
- Initialize counters

### Stage 2: Pass diagnostics to LoadModelFromFile

**File:** `Rdk/Core/Application/UApplication.cpp:2131`

```cpp
is_loaded = LoadModelFromFile(i, model_file_path, diagnostics);
```

**Actions:**
- Diagnostics passed by pointer
- All file load errors accumulate in `diagnostics->errors`

### Stage 3: Temporary storage in Engine

**File:** `Rdk/Core/Application/UApplication.cpp:2882-2888`

```cpp
RDK::UELockPtr<RDK::UEngine> engine_lock = RDK::GetEngineLock(channel_index);
if(engine_lock.Get())
{
  engine_lock.Get()->SetLoadDiagnostics(diagnostics);
}
```

**Actions:**
- Diagnostics stored in `UEngine::LoadDiagnostics`
- Temporary storage for passing through the C API

**Issue:** If `GetEngineLock` returns a different Engine (e.g. on channel switch), diagnostics may be lost.

### Stage 4: Retrieve diagnostics in Model_LoadComponent

**File:** `Rdk/Core/Engine/UEngine.cpp:5615`

```cpp
void* load_diagnostics = GetLoadDiagnostics();
if(!cont->LoadComponent(&XmlStorage, true, load_diagnostics))
  return RDK_E_MODEL_LOAD_COMPONENT_FAIL;
```

**Actions:**
- Diagnostics retrieved from Engine temporary storage
- Passed to `LoadComponent` as `void*` for backward compatibility

**Issue:** If `GetLoadDiagnostics()` returns `nullptr`, diagnostics are not passed further.

### Stage 5: Accumulate errors in LoadComponent

**File:** `Rdk/Core/Engine/UNet.cpp:789-895`

```cpp
TProjectLoadDiagnostics* diag = diagnostics ? static_cast<TProjectLoadDiagnostics*>(diagnostics) : nullptr;

// При ошибке:
if(diag)
{
  diag->errors.push_back(error_msg);
}
```

**Actions:**
- Diagnostics cast to the correct type
- Errors accumulate in `diag->errors`
- `if(diag)` prevents dereferencing `nullptr`

**Handled errors:**
1. Nonexistent class: `EClassNameNotExist` → `diag->errors`
2. Failed creation: `TakeObject` returns `nullptr` → `diag->errors`
3. Failed add: `AddComponent` returns `ForbiddenId` → `diag->errors`
4. Failed child load: `LoadComponent` returns `false` → `diag->errors`

### Stage 6: Accumulate errors in CreateLink

**File:** `Rdk/Core/Engine/UNet.h:399-422`

```cpp
TProjectLoadDiagnostics* diag = diagnostics ? static_cast<TProjectLoadDiagnostics*>(diagnostics) : nullptr;

if(!pitem)
{
  if(diag)
    diag->errors.push_back("Source component 'X' not found");
  return false;
}
```

**Actions:**
- Diagnostics cast to the correct type
- Missing component errors accumulate in `diag->errors`

**Handled errors:**
1. Source component not found → `diag->errors`
2. Destination component not found → `diag->errors`

### Stage 7: Accumulate errors in ConnectToItem

**File:** `Rdk/Core/Engine/UConnector.cpp:457-483`

```cpp
TProjectLoadDiagnostics* diag = diagnostics ? static_cast<TProjectLoadDiagnostics*>(diagnostics) : nullptr;

if(!i_item_property)
{
  if(diag)
    diag->errors.push_back("Output port 'X' not found in component 'Y'");
  return false;
}
```

**Actions:**
- Diagnostics cast to the correct type
- Missing port errors accumulate in `diag->errors`

**Handled errors:**
1. Source port not found → `diag->errors`
2. Destination port not found → `diag->errors`

**Not handled:**
- Port type mismatch → logging only, not accumulated

## Diagnostic flow issues

### Issue 1: Lost diagnostics between LoadModelFromFile and Model_LoadComponent

**Location:** `Rdk/Core/Application/UApplication.cpp:2882-2893`

**Description:**
- Diagnostics set in Engine via `SetLoadDiagnostics`
- Then `MModel_LoadComponent` is called, creating a new `UELockPtr`
- If a channel switch occurs between set and get, diagnostics may be lost

**Solution:**
- Ensure `GetEngineLock(channel_index)` always returns the same Engine pointer
- Add a check that diagnostics were not lost
- Consider an alternative: pass via function parameters

### Issue 2: Diagnostics may be nullptr

**Location:** Various places in the code

**Description:**
- Many places check `if(diag)`, but if diagnostics were not passed, errors are lost
- Normal for backward compatibility, but may hide errors

**Solution:**
- Ensure diagnostics are passed to all recursive calls
- Add logging when diagnostics are not passed (for debugging)

### Issue 3: Type mismatch error is not accumulated

**Location:** `Rdk/Core/Engine/UConnector.cpp:485-494`

**Description:**
- On port type mismatch, the error is logged but not accumulated in diagnostics
- This is a critical error that should be in diagnostics

**Solution:**
- Accumulate the error in `diag->errors` on type mismatch

## Improvement recommendations

### Recommendation 1: Unified diagnostics passing mechanism

**Current state:**
- Diagnostics passed via temporary storage in Engine
- Works, but not ideal

**Proposal:**
- Consider passing diagnostics via function parameters
- Requires C API changes, but more reliable

### Recommendation 2: Accumulate all errors

**Current state:**
- Most errors are accumulated
- Type mismatch error is not accumulated

**Proposal:**
- Accumulate all errors, including type mismatch

### Recommendation 3: Accumulate warnings

**Current state:**
- Warnings about inactive components are logged only

**Proposal:**
- Accumulate warnings in `diag->warnings`

## Usage examples

### Example 1: Configuration validation

```cpp
TProjectLoadDiagnostics diagnostics;
bool loaded = app->OpenProject("project.ini", &diagnostics);

if(!diagnostics.errors.empty())
{
  std::cout << "Errors:" << std::endl;
  for(const auto& error : diagnostics.errors)
    std::cout << "  - " << error << std::endl;
}

if(!diagnostics.warnings.empty())
{
  std::cout << "Warnings:" << std::endl;
  for(const auto& warning : diagnostics.warnings)
    std::cout << "  - " << warning << std::endl;
}
```

### Example 2: Validity check

```cpp
TProjectLoadDiagnostics diagnostics = app->ValidateProject("project.ini");

if(!diagnostics.isValid)
{
  // Обработка ошибок
  return false;
}
```

## See also

- [Engine Architecture](../../Rdk/Docs/Architecture/Engine-Architecture.md) — component loading
- [Serialize Architecture](../../Rdk/Docs/Architecture/Serialize-Architecture.md) — serialization and links
- [Application Architecture](Application-Architecture.md)
