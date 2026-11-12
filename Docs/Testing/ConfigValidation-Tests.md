# Тесты валидации конфигураций

## RU

## Обзор

Интеграционные тесты для проверки функциональности валидации конфигураций проектов через команду `--check-config` в `NeuroModelerConsole`.

## Расположение

- **Тесты:** `Tests/Integration/ConfigValidation/`
- **Тестовые конфигурации:** `Bin/Configs/TestValidation/`
- **Документация:** `Tests/Integration/ConfigValidation/README.md`

## Быстрый старт

### 1. Сборка тестов

```bash
cd /path/to/Nmsdk
mkdir -p build
cd build
cmake ..
cmake --build . --target Test_ConfigValidation
```

### 2. Запуск тестов

```bash
# Через CTest
ctest -R ConfigValidationTests -V

# Или напрямую
./Tests/Integration/ConfigValidation/Test_ConfigValidation
```

## Тестовые конфигурации

Все тестовые конфигурации находятся в `Bin/Configs/TestValidation/`:

### test_valid
**Назначение:** Валидная конфигурация для проверки успешной валидации

**Ожидаемый результат:**
- Exit code: 0
- Ошибок: 0
- Предупреждений: 0

### test_missing_model
**Назначение:** Конфигурация с отсутствующим файлом модели

**Ожидаемый результат:**
- Exit code: 1
- Ошибки о отсутствующих файлах модели

### test_missing_parameters
**Назначение:** Конфигурация с отсутствующим файлом параметров

**Ожидаемый результат:**
- Exit code: 1
- Ошибки о отсутствующих файлах параметров

### test_invalid_xml
**Назначение:** Конфигурация с невалидным XML

**Ожидаемый результат:**
- Exit code: 1
- Ошибки парсинга XML

### test_empty_model
**Назначение:** Конфигурация с пустой моделью (без компонентов)

**Ожидаемый результат:**
- Exit code: 1
- Предупреждения о пустой модели

### test_invalid_classes
**Назначение:** Конфигурация с компонентами несуществующих классов

**Содержимое:**
- `NonExistentComponent1` с классом `NonExistentClass123`
- `NonExistentComponent2` с классом `FakeComponentClass`
- `ValidComponent` с классом `NPGenerator` (валидный)

**Ожидаемый результат:**
- Exit code: 1
- Ошибки о несуществующих классах компонентов
- Должны быть обнаружены классы: `NonExistentClass123`, `FakeComponentClass`

### test_invalid_links
**Назначение:** Конфигурация с неправильными связями

**Содержимое:**
- Правильная связь: `Generator1.Output` -> `Neuron1.Soma1.ExcSynapse1.Input`
- Неправильная связь: `NonExistentGenerator.Output` -> `Neuron1.Soma1.ExcSynapse1.Input` (несуществующий источник)
- Неправильная связь: `Generator1.Output` -> `NonExistentNeuron.Soma1.ExcSynapse1.Input` (несуществующий приемник)
- Неправильная связь: `Generator1.NonExistentOutput` -> `Neuron1.Soma1.ExcSynapse1.Input` (несуществующий выходной порт)
- Неправильная связь: `Generator1.Output` -> `Neuron1.Soma1.ExcSynapse1.NonExistentInput` (несуществующий входной порт)

**Ожидаемый результат:**
- Exit code: 1
- Ошибки о неправильных связях
- Должны быть обнаружены несуществующие компоненты и порты

## Ручной запуск валидации

Для ручной проверки валидации конфигурации:

```bash
./Bin/Platform/Linux/NeuroModelerConsole --check-config Bin/Configs/TestValidation/test_invalid_classes/project.ini
```

### Примеры вывода

**Валидная конфигурация:**
```
Configuration validation results:
  Model exists: Yes
  Model empty: No
  Components count per channel: [0]=4
  Channels loaded: 1/1
  Errors: 0
  Warnings: 0

Configuration is VALID
```

**Конфигурация с ошибками:**
```
Configuration validation results:
  Model exists: Yes
  Model empty: Yes
  Components count per channel: [0]=1
  Channels loaded: 1/1
  Errors: 2
  Warnings: 0

Errors:
  - Channel 0, Component 'NonExistentComponent1': Class 'NonExistentClass123' does not exist in storage
  - Channel 0, Component 'NonExistentComponent2': Class 'FakeComponentClass' does not exist in storage

Configuration is INVALID
```

## Структура тестов

### Test_ConfigValidation.cpp

Основной файл тестов, который:
1. Находит исполняемый файл `NeuroModelerConsole`
2. Находит директорию с тестовыми конфигурациями
3. Запускает валидацию для каждой тестовой конфигурации
4. Проверяет exit code и содержимое вывода
5. Выводит результаты

### CMakeLists.txt

Настройка сборки тестов через CMake:
- Поиск исполняемого файла `NeuroModelerConsole`
- Компиляция тестового файла
- Регистрация теста в CTest

## Добавление новых тестов

1. **Создайте тестовую конфигурацию:**
   ```bash
   mkdir -p Bin/Configs/TestValidation/test_new_case
   # Создайте project.ini и необходимые файлы
   ```

2. **Добавьте тест в Test_ConfigValidation.cpp:**
   ```cpp
   {
       "Название теста",
       "test_new_case/project.ini",
       1,  // ожидаемый exit code
       true,  // должны быть ошибки
       false,  // должны быть предупреждения
       {"паттерн ошибки 1", "паттерн ошибки 2"},
       {"паттерн предупреждения"}
   }
   ```

## Отладка

### Проблема: NeuroModelerConsole не найден

**Решение:** Убедитесь, что проект собран:
```bash
cd build
cmake --build . --target NeuroModelerConsole
```

### Проблема: Тестовые конфигурации не найдены

**Решение:** Проверьте наличие директории:
```bash
ls -la Bin/Configs/TestValidation/
```

### Проблема: Тесты не проходят

**Решение:** 
1. Запустите валидацию вручную для проблемной конфигурации
2. Проверьте фактический вывод и сравните с ожидаемым
3. Обновите паттерны в тесте, если они не соответствуют фактическому выводу

## Интеграция в CI/CD

Тесты можно интегрировать в систему непрерывной интеграции:

```yaml
# Пример для GitHub Actions
- name: Run Config Validation Tests
  run: |
    cd build
    ctest -R ConfigValidationTests -V
```

## comp_gui smoke-check (presets)

Для comp_gui-итераций дополнительно выполняйте короткий smoke-check GUI pipeline:

```bash
cmake --preset linux-gcc-debug-tests
cmake --build --preset linux-gcc-debug-tests
ctest --preset linux-component-gui-registry
```

Это обеспечивает воспроизводимую проверку `Test_ComponentGuiRegistry` без ручной настройки путей/таргетов.

## См. также

- [README тестов](../../Tests/Integration/ConfigValidation/README.md)
- [Документация валидации конфигураций](../Development-Guides/Config-Validation.md)

---

## EN

## Overview

Integration tests for project configuration validation via the `--check-config` command in `NeuroModelerConsole`.

## Location

- **Tests:** `Tests/Integration/ConfigValidation/`
- **Test configurations:** `Bin/Configs/TestValidation/`
- **Documentation:** `Tests/Integration/ConfigValidation/README.md`

## Quick start

### 1. Build tests

```bash
cd /path/to/Nmsdk
mkdir -p build
cd build
cmake ..
cmake --build . --target Test_ConfigValidation
```

### 2. Run tests

```bash
# Via CTest
ctest -R ConfigValidationTests -V

# Or directly
./Tests/Integration/ConfigValidation/Test_ConfigValidation
```

## Test configurations

All test configurations are in `Bin/Configs/TestValidation/`:

### test_valid
**Purpose:** Valid configuration for successful validation check

**Expected result:**
- Exit code: 0
- Errors: 0
- Warnings: 0

### test_missing_model
**Purpose:** Configuration with a missing model file

**Expected result:**
- Exit code: 1
- Errors about missing model files

### test_missing_parameters
**Purpose:** Configuration with a missing parameters file

**Expected result:**
- Exit code: 1
- Errors about missing parameter files

### test_invalid_xml
**Purpose:** Configuration with invalid XML

**Expected result:**
- Exit code: 1
- XML parsing errors

### test_empty_model
**Purpose:** Configuration with an empty model (no components)

**Expected result:**
- Exit code: 1
- Warnings about empty model

### test_invalid_classes
**Purpose:** Configuration with nonexistent component classes

**Content:**
- `NonExistentComponent1` with class `NonExistentClass123`
- `NonExistentComponent2` with class `FakeComponentClass`
- `ValidComponent` with class `NPGenerator` (valid)

**Expected result:**
- Exit code: 1
- Errors about nonexistent component classes
- Classes `NonExistentClass123`, `FakeComponentClass` should be detected

### test_invalid_links
**Purpose:** Configuration with invalid links

**Content:**
- Valid link: `Generator1.Output` -> `Neuron1.Soma1.ExcSynapse1.Input`
- Invalid link: `NonExistentGenerator.Output` -> `Neuron1.Soma1.ExcSynapse1.Input` (nonexistent source)
- Invalid link: `Generator1.Output` -> `NonExistentNeuron.Soma1.ExcSynapse1.Input` (nonexistent destination)
- Invalid link: `Generator1.NonExistentOutput` -> `Neuron1.Soma1.ExcSynapse1.Input` (nonexistent output port)
- Invalid link: `Generator1.Output` -> `Neuron1.Soma1.ExcSynapse1.NonExistentInput` (nonexistent input port)

**Expected result:**
- Exit code: 1
- Errors about invalid links
- Nonexistent components and ports should be detected

## Manual validation run

To manually validate a configuration:

```bash
./Bin/Platform/Linux/NeuroModelerConsole --check-config Bin/Configs/TestValidation/test_invalid_classes/project.ini
```

### Sample output

**Valid configuration:**
```
Configuration validation results:
  Model exists: Yes
  Model empty: No
  Components count per channel: [0]=4
  Channels loaded: 1/1
  Errors: 0
  Warnings: 0

Configuration is VALID
```

**Configuration with errors:**
```
Configuration validation results:
  Model exists: Yes
  Model empty: Yes
  Components count per channel: [0]=1
  Channels loaded: 1/1
  Errors: 2
  Warnings: 0

Errors:
  - Channel 0, Component 'NonExistentComponent1': Class 'NonExistentClass123' does not exist in storage
  - Channel 0, Component 'NonExistentComponent2': Class 'FakeComponentClass' does not exist in storage

Configuration is INVALID
```

## Test structure

### Test_ConfigValidation.cpp

Main test file that:
1. Locates the `NeuroModelerConsole` executable
2. Locates the test configuration directory
3. Runs validation for each test configuration
4. Checks exit code and output content
5. Prints results

### CMakeLists.txt

CMake build setup:
- Locate `NeuroModelerConsole` executable
- Compile test file
- Register test in CTest

## Adding new tests

1. **Create a test configuration:**
   ```bash
   mkdir -p Bin/Configs/TestValidation/test_new_case
   # Create project.ini and required files
   ```

2. **Add a test in Test_ConfigValidation.cpp:**
   ```cpp
   {
       "Test name",
       "test_new_case/project.ini",
       1,  // expected exit code
       true,  // should have errors
       false,  // should have warnings
       {"error pattern 1", "error pattern 2"},
       {"warning pattern"}
   }
   ```

## Debugging

### Issue: NeuroModelerConsole not found

**Solution:** Ensure the project is built:
```bash
cd build
cmake --build . --target NeuroModelerConsole
```

### Issue: Test configurations not found

**Solution:** Check the directory exists:
```bash
ls -la Bin/Configs/TestValidation/
```

### Issue: Tests fail

**Solution:** 
1. Run validation manually for the failing configuration
2. Compare actual output with expected
3. Update patterns in the test if they do not match actual output

## CI/CD integration

Tests can be integrated into continuous integration:

```yaml
# Example for GitHub Actions
- name: Run Config Validation Tests
  run: |
    cd build
    ctest -R ConfigValidationTests -V
```

## comp_gui smoke-check (presets)

For comp_gui iterations, also run a short GUI pipeline smoke check:

```bash
cmake --preset linux-gcc-debug-tests
cmake --build --preset linux-gcc-debug-tests
ctest --preset linux-component-gui-registry
```

This provides a reproducible `Test_ComponentGuiRegistry` check without manual path/target setup.

## See also

- [Test README](../../Tests/Integration/ConfigValidation/README.md)
- [Configuration validation docs](../Development-Guides/Config-Validation.md)
