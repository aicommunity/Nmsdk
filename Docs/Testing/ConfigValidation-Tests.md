# Тесты валидации конфигураций

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
