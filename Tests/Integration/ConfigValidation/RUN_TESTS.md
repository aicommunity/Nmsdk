# Инструкция по запуску тестов валидации конфигураций

## Рекомендуемые режимы запуска

### 1) Быстрый non-interactive (по умолчанию, без GUI-окон)

Используйте этот режим в CI и для ежедневной проверки, чтобы тесты не открывали окна и не требовали действий пользователя.

```bash
cd /path/to/Nmsdk
mkdir -p build/Debug
cd build/Debug
cmake /path/to/Nmsdk \
  -DCMAKE_BUILD_TYPE=Debug \
  -DBUILD_TESTS=ON \
  -DBUILD_TESTING=ON \
  -DRDK_BUILD_LEGACY_ENGINE_UNIT_TESTS=ON \
  -DNMSDK_ENABLE_INTERACTIVE_GUI_TESTS=OFF
cmake --build . --parallel
ctest --output-on-failure -j8
```

### 2) Полный прогон с GUI-интеграцией (manual mode)

Включайте только при необходимости проверки GUI-сценариев. Возможны окна/нестабильность в headless-окружении.

```bash
cd /path/to/Nmsdk/build/Debug
cmake /path/to/Nmsdk -DNMSDK_ENABLE_INTERACTIVE_GUI_TESTS=ON
cmake --build . --parallel
ctest --output-on-failure -R "MenuBarTest|QMessageBox|PluginLoadingTest|UModernDiagramWidgetMovementTest"
```

Примечание: GUI-тесты могут требовать графической сессии и/или ручного взаимодействия.

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
- Exit code: **2**
- Должен содержать: `Configuration is VALID`

### test_invalid_classes
- Exit code: **1**
- Должен содержать: `Configuration is INVALID`

### test_invalid_links
- Exit code: **2**
- Должен содержать: `Configuration is VALID`

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
