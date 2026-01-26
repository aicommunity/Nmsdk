# Инструкция по запуску тестов валидации конфигураций

## Быстрый старт

### 1. Убедитесь, что проект собран

```bash
cd /path/to/Nmsdk
mkdir -p build
cd build
cmake ..
cmake --build . --target NeuroModelerConsole
```

### 2. Соберите тесты

```bash
cd build
cmake --build . --target Test_ConfigValidation
```

### 3. Запустите тесты

**Через CTest (рекомендуется):**
```bash
cd build
ctest -R ConfigValidationTests -V
```

**Напрямую:**
```bash
cd build/Tests/Integration/ConfigValidation
./Test_ConfigValidation
```

**На Windows:**
```cmd
cd build\Tests\Integration\ConfigValidation
Test_ConfigValidation.exe
```

## Ручная проверка отдельных тестов

Для проверки конкретной конфигурации вручную:

```bash
# Валидная конфигурация
./Bin/Platform/Linux/NeuroModelerConsole --check-config Bin/Configs/TestValidation/test_valid/project.ini

# Несуществующие классы
./Bin/Platform/Linux/NeuroModelerConsole --check-config Bin/Configs/TestValidation/test_invalid_classes/project.ini

# Неправильные связи
./Bin/Platform/Linux/NeuroModelerConsole --check-config Bin/Configs/TestValidation/test_invalid_links/project.ini
```

## Ожидаемые результаты

### test_valid
- Exit code: **0**
- Ошибок: **0**
- Предупреждений: **0**

### test_invalid_classes
- Exit code: **1**
- Ошибок: **≥2** (для каждого несуществующего класса)
- Должны содержать: `NonExistentClass123`, `FakeComponentClass`

### test_invalid_links
- Exit code: **1**
- Ошибок: **≥4** (для каждой неправильной связи)
- Должны содержать: `NonExistentGenerator`, `NonExistentNeuron`, `NonExistentOutput`, `NonExistentInput`

## Устранение проблем

### Ошибка: "NeuroModelerConsole not found"

**Решение:**
```bash
# Убедитесь, что файл существует
ls -la Bin/Platform/Linux/NeuroModelerConsole

# Если нет, пересоберите проект
cd build
cmake --build . --target NeuroModelerConsole
```

### Ошибка: "Test configs directory not found"

**Решение:**
```bash
# Проверьте наличие директории
ls -la Bin/Configs/TestValidation/

# Если нет, создайте тестовые конфигурации
# (они должны быть в репозитории)
```

### Тесты не проходят

1. Запустите валидацию вручную для проблемной конфигурации
2. Проверьте фактический вывод
3. Сравните с ожидаемым результатом
4. При необходимости обновите паттерны в `Test_ConfigValidation.cpp`

## Пример успешного запуска

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

## Дополнительная информация

- Подробная документация: `Tests/Integration/ConfigValidation/README.md`
- Общая документация: `Docs/Testing/ConfigValidation-Tests.md`
