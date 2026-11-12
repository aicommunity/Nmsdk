# Интеграционные тесты валидации конфигураций

## RU

## Описание

Эти тесты проверяют функциональность валидации конфигураций проектов через команду `--check-config` в `NeuroModelerConsole`.

## Требования

- Собранный проект (исполняемый файл `NeuroModelerConsole`)
- Тестовые конфигурации в `Bin/Configs/TestValidation/`

## Тестовые случаи

### 1. Валидная конфигурация (`test_valid`)
- **Ожидаемый результат:** Exit code 0, нет ошибок и предупреждений
- **Проверяет:** Корректная обработка валидной конфигурации

### 2. Отсутствующий файл модели (`test_missing_model`)
- **Ожидаемый результат:** Exit code 1, ошибки о отсутствующих файлах
- **Проверяет:** Обнаружение отсутствующих файлов модели

### 3. Отсутствующий файл параметров (`test_missing_parameters`)
- **Ожидаемый результат:** Exit code 1, ошибки о отсутствующих файлах параметров
- **Проверяет:** Обнаружение отсутствующих файлов параметров

### 4. Невалидный XML (`test_invalid_xml`)
- **Ожидаемый результат:** Exit code 1, ошибки парсинга XML
- **Проверяет:** Обнаружение синтаксических ошибок в XML

### 5. Пустая модель (`test_empty_model`)
- **Ожидаемый результат:** Exit code 1, предупреждения о пустой модели
- **Проверяет:** Обнаружение пустых моделей (без компонентов)

### 6. Несуществующие классы компонентов (`test_invalid_classes`)
- **Ожидаемый результат:** Exit code 1, ошибки о несуществующих классах
- **Проверяет:** Обнаружение компонентов с несуществующими классами
- **Тестовые данные:**
  - `NonExistentComponent1` с классом `NonExistentClass123`
  - `NonExistentComponent2` с классом `FakeComponentClass`

### 7. Неправильные связи (`test_invalid_links`)
- **Ожидаемый результат:** Exit code 1, ошибки о неправильных связях
- **Проверяет:** Обнаружение связей с несуществующими компонентами и портами
- **Тестовые данные:**
  - Связь с несуществующим компонентом-источником
  - Связь с несуществующим компонентом-приемником
  - Связь с несуществующим выходным портом
  - Связь с несуществующим входным портом

## Сборка тестов

### Через CMake

```bash
cd /path/to/Nmsdk
mkdir -p build
cd build
cmake ..
cmake --build . --target Test_ConfigValidation
```

### Прямая компиляция

```bash
cd Tests/Integration/ConfigValidation
g++ -std=c++17 -o Test_ConfigValidation Test_ConfigValidation.cpp
```

## Запуск тестов

### Через CTest

```bash
cd build
ctest -R ConfigValidationTests -V
```

### Прямой запуск

```bash
cd build/Tests/Integration/ConfigValidation
./Test_ConfigValidation
```

### На Windows

```cmd
cd build\Tests\Integration\ConfigValidation
Test_ConfigValidation.exe
```

## Структура вывода

Тесты выводят:
- Название каждого теста
- Команду, которая выполняется
- Exit code (фактический и ожидаемый)
- Результаты проверки паттернов ошибок и предупреждений
- Итоговую статистику (пройдено/провалено)

## Пример вывода

```
=== Интеграционные тесты валидации конфигураций ===
NeuroModelerConsole: /path/to/Bin/Platform/Linux/NeuroModelerConsole
Тестовые конфигурации: /path/to/Bin/Configs/TestValidation

=== Тест: Валидная конфигурация ===
Команда: "/path/to/NeuroModelerConsole" --check-config "/path/to/test_valid/project.ini"
Exit code: 0 (ожидалось: 0)
✓ Тест пройден

=== Тест: Несуществующие классы компонентов ===
Команда: "/path/to/NeuroModelerConsole" --check-config "/path/to/test_invalid_classes/project.ini"
Exit code: 1 (ожидалось: 1)
  ✓ Найден паттерн ошибки: does not exist in storage
  ✓ Найден паттерн ошибки: NonExistentClass123
  ✓ Найден паттерн ошибки: FakeComponentClass
✓ Тест пройден

=== Итоги ===
Пройдено: 7
Провалено: 0
Всего: 7
```

## Отладка

Если тесты не проходят:

1. **Проверьте наличие NeuroModelerConsole:**
   ```bash
   ls -la Bin/Platform/Linux/NeuroModelerConsole
   ```

2. **Проверьте наличие тестовых конфигураций:**
   ```bash
   ls -la Bin/Configs/TestValidation/
   ```

3. **Запустите валидацию вручную:**
   ```bash
   ./Bin/Platform/Linux/NeuroModelerConsole --check-config Bin/Configs/TestValidation/test_invalid_classes/project.ini
   ```

4. **Проверьте вывод теста:**
   - Тесты выводят полный STDOUT и STDERR при провале
   - Проверьте, что паттерны ошибок соответствуют фактическому выводу

## Добавление новых тестов

Для добавления нового теста:

1. Создайте тестовую конфигурацию в `Bin/Configs/TestValidation/`
2. Добавьте новый `TestCase` в массив `testCases` в `Test_ConfigValidation.cpp`:

```cpp
{
    "Название теста",
    "путь/к/конфигурации/project.ini",
    ожидаемый_exit_code,
    должны_быть_ошибки,
    должны_быть_предупреждения,
    {"паттерн1", "паттерн2"},  // Ожидаемые паттерны ошибок
    {"паттерн1"}                // Ожидаемые паттерны предупреждений
}
```

## Примечания

- Тесты требуют собранного проекта
- Тесты выполняют реальные команды через системный shell
- На Windows используется `CreateProcess`, на Linux - `fork/exec`
- Тесты проверяют как exit code, так и содержимое вывода

---

## EN

## Description

These tests verify project configuration validation via the `--check-config` command in `NeuroModelerConsole`.

## Requirements

- Built project (`NeuroModelerConsole` executable)
- Test configurations in `Bin/Configs/TestValidation/`

## Test cases

### 1. Valid configuration (`test_valid`)
- **Expected:** Exit code 0, no errors or warnings
- **Checks:** Correct handling of a valid configuration

### 2. Missing model file (`test_missing_model`)
- **Expected:** Exit code 1, errors about missing files
- **Checks:** Detection of missing model files

### 3. Missing parameters file (`test_missing_parameters`)
- **Expected:** Exit code 1, errors about missing parameter files
- **Checks:** Detection of missing parameter files

### 4. Invalid XML (`test_invalid_xml`)
- **Expected:** Exit code 1, XML parsing errors
- **Checks:** Detection of XML syntax errors

### 5. Empty model (`test_empty_model`)
- **Expected:** Exit code 1, warnings about empty model
- **Checks:** Detection of empty models (no components)

### 6. Nonexistent component classes (`test_invalid_classes`)
- **Expected:** Exit code 1, errors about nonexistent classes
- **Checks:** Detection of components with nonexistent classes
- **Test data:**
  - `NonExistentComponent1` with class `NonExistentClass123`
  - `NonExistentComponent2` with class `FakeComponentClass`

### 7. Invalid links (`test_invalid_links`)
- **Expected:** Exit code 1, errors about invalid links
- **Checks:** Detection of links with nonexistent components and ports
- **Test data:**
  - Link with nonexistent source component
  - Link with nonexistent destination component
  - Link with nonexistent output port
  - Link with nonexistent input port

## Building tests

### Via CMake

```bash
cd /path/to/Nmsdk
mkdir -p build
cd build
cmake ..
cmake --build . --target Test_ConfigValidation
```

### Direct compilation

```bash
cd Tests/Integration/ConfigValidation
g++ -std=c++17 -o Test_ConfigValidation Test_ConfigValidation.cpp
```

## Running tests

### Via CTest

```bash
cd build
ctest -R ConfigValidationTests -V
```

### Direct run

```bash
cd build/Tests/Integration/ConfigValidation
./Test_ConfigValidation
```

### On Windows

```cmd
cd build\Tests\Integration\ConfigValidation
Test_ConfigValidation.exe
```

## Output structure

Tests print:
- Name of each test
- Command executed
- Exit code (actual and expected)
- Error and warning pattern check results
- Summary (passed/failed)

## Sample output

```
=== Интеграционные тесты валидации конфигураций ===
NeuroModelerConsole: /path/to/Bin/Platform/Linux/NeuroModelerConsole
Тестовые конфигурации: /path/to/Bin/Configs/TestValidation

=== Тест: Валидная конфигурация ===
Команда: "/path/to/NeuroModelerConsole" --check-config "/path/to/test_valid/project.ini"
Exit code: 0 (ожидалось: 0)
✓ Тест пройден

=== Тест: Несуществующие классы компонентов ===
Команда: "/path/to/NeuroModelerConsole" --check-config "/path/to/test_invalid_classes/project.ini"
Exit code: 1 (ожидалось: 1)
  ✓ Найден паттерн ошибки: does not exist in storage
  ✓ Найден паттерн ошибки: NonExistentClass123
  ✓ Найден паттерн ошибки: FakeComponentClass
✓ Тест пройден

=== Итоги ===
Пройдено: 7
Провалено: 0
Всего: 7
```

## Debugging

If tests fail:

1. **Check NeuroModelerConsole exists:**
   ```bash
   ls -la Bin/Platform/Linux/NeuroModelerConsole
   ```

2. **Check test configurations exist:**
   ```bash
   ls -la Bin/Configs/TestValidation/
   ```

3. **Run validation manually:**
   ```bash
   ./Bin/Platform/Linux/NeuroModelerConsole --check-config Bin/Configs/TestValidation/test_invalid_classes/project.ini
   ```

4. **Check test output:**
   - Tests print full STDOUT and STDERR on failure
   - Verify error patterns match actual output

## Adding new tests

To add a new test:

1. Create a test configuration in `Bin/Configs/TestValidation/`
2. Add a new `TestCase` to the `testCases` array in `Test_ConfigValidation.cpp`:

```cpp
{
    "Test name",
    "path/to/config/project.ini",
    expected_exit_code,
    should_have_errors,
    should_have_warnings,
    {"pattern1", "pattern2"},  // Expected error patterns
    {"pattern1"}                // Expected warning patterns
}
```

## Notes

- Tests require a built project
- Tests run real commands via the system shell
- On Windows uses `CreateProcess`, on Linux — `fork/exec`
- Tests check both exit code and output content
