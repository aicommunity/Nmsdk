# Быстрый старт: Тесты валидации конфигураций

## RU

## Минимальные шаги для запуска

### 1. Сборка проекта
```bash
cd /path/to/Nmsdk
mkdir -p build && cd build
cmake ..
cmake --build . --target NeuroModelerConsole Test_ConfigValidation
```

### 2. Запуск тестов
```bash
# Через CTest
ctest -R ConfigValidationTests -V

# Или напрямую
./Tests/Integration/ConfigValidation/Test_ConfigValidation
```

## Что проверяется

✅ Валидные конфигурации  
✅ Отсутствующие файлы  
✅ Невалидный XML  
✅ Пустые модели  
✅ Несуществующие классы компонентов  
✅ Неправильные связи между компонентами  

## Быстрая проверка вручную

```bash
# Проверка несуществующих классов
./Bin/Platform/Linux/NeuroModelerConsole --check-config \
  Bin/Configs/TestValidation/test_invalid_classes/project.ini

# Проверка неправильных связей
./Bin/Platform/Linux/NeuroModelerConsole --check-config \
  Bin/Configs/TestValidation/test_invalid_links/project.ini
```

## Документация

- **Подробная инструкция:** `README.md`
- **Руководство по запуску:** `RUN_TESTS.md`
- **Общая документация:** `Docs/Testing/ConfigValidation-Tests.md`

---

## EN

## Minimal steps to run

### 1. Build the project
```bash
cd /path/to/Nmsdk
mkdir -p build && cd build
cmake ..
cmake --build . --target NeuroModelerConsole Test_ConfigValidation
```

### 2. Run tests
```bash
# Via CTest
ctest -R ConfigValidationTests -V

# Or directly
./Tests/Integration/ConfigValidation/Test_ConfigValidation
```

## What is checked

✅ Valid configurations  
✅ Missing files  
✅ Invalid XML  
✅ Empty models  
✅ Nonexistent component classes  
✅ Invalid links between components

## Quick manual check

```bash
# Check nonexistent classes
./Bin/Platform/Linux/NeuroModelerConsole --check-config \
  Bin/Configs/TestValidation/test_invalid_classes/project.ini

# Check invalid links
./Bin/Platform/Linux/NeuroModelerConsole --check-config \
  Bin/Configs/TestValidation/test_invalid_links/project.ini
```

## Documentation

- **Detailed instructions:** `README.md`
- **Run guide:** `RUN_TESTS.md`
- **General documentation:** `Docs/Testing/ConfigValidation-Tests.md`
