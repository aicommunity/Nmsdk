# Интеграционные тесты валидации конфигураций

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
