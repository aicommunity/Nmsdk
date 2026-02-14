# Быстрый старт: Тесты валидации конфигураций

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
