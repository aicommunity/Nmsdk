# Индекс документации тестов валидации конфигураций

## RU

## Быстрый доступ

- **🚀 Быстрый старт:** [QUICK_START.md](QUICK_START.md) - минимальные шаги для запуска
- **📖 Полная документация:** [README.md](README.md) - подробное описание тестов
- **▶️ Инструкция по запуску:** [RUN_TESTS.md](RUN_TESTS.md) - детальная инструкция

## Структура файлов

```
Tests/Integration/ConfigValidation/
├── CMakeLists.txt              # Настройка сборки через CMake
├── Test_ConfigValidation.cpp   # Основной файл тестов
├── INDEX.md                    # Этот файл
├── QUICK_START.md              # Быстрый старт
├── README.md                   # Полная документация
└── RUN_TESTS.md                # Инструкция по запуску
```

## Тестовые конфигурации

Все тестовые конфигурации находятся в `Bin/Configs/TestValidation/`:

- `test_valid/` - валидная конфигурация
- `test_missing_model/` - отсутствующий файл модели
- `test_missing_parameters/` - отсутствующий файл параметров
- `test_invalid_xml/` - невалидный XML
- `test_empty_model/` - пустая модель
- `test_invalid_classes/` - несуществующие классы компонентов
- `test_invalid_links/` - неправильные связи

## Команды

### Сборка
```bash
cmake --build build --target Test_ConfigValidation
```

### Запуск
```bash
# Через CTest
ctest -R ConfigValidationTests -V

# Напрямую
./build/Tests/Integration/ConfigValidation/Test_ConfigValidation
```

### Ручная проверка
```bash
./Bin/Platform/Linux/NeuroModelerConsole --check-config \
  Bin/Configs/TestValidation/test_invalid_classes/project.ini
```

## См. также

- [Общая документация по тестированию](../../../Docs/Testing/ConfigValidation-Tests.md)
- [Документация тестовых конфигураций](../../../Bin/Configs/TestValidation/README.md)

---

## EN

## Quick access

- **🚀 Quick start:** [QUICK_START.md](QUICK_START.md) — minimal steps to run
- **📖 Full documentation:** [README.md](README.md) — detailed test description
- **▶️ Run instructions:** [RUN_TESTS.md](RUN_TESTS.md) — detailed run guide

## File structure

```
Tests/Integration/ConfigValidation/
├── CMakeLists.txt              # CMake build setup
├── Test_ConfigValidation.cpp   # Main test file
├── INDEX.md                    # This file
├── QUICK_START.md              # Quick start
├── README.md                   # Full documentation
└── RUN_TESTS.md                # Run instructions
```

## Test configurations

All test configurations are in `Bin/Configs/TestValidation/`:

- `test_valid/` — valid configuration
- `test_missing_model/` — missing model file
- `test_missing_parameters/` — missing parameters file
- `test_invalid_xml/` — invalid XML
- `test_empty_model/` — empty model
- `test_invalid_classes/` — nonexistent component classes
- `test_invalid_links/` — invalid links

## Commands

### Build
```bash
cmake --build build --target Test_ConfigValidation
```

### Run
```bash
# Via CTest
ctest -R ConfigValidationTests -V

# Directly
./build/Tests/Integration/ConfigValidation/Test_ConfigValidation
```

### Manual check
```bash
./Bin/Platform/Linux/NeuroModelerConsole --check-config \
  Bin/Configs/TestValidation/test_invalid_classes/project.ini
```

## See also

- [General testing documentation](../../../Docs/Testing/ConfigValidation-Tests.md)
- [Test configuration documentation](../../../Bin/Configs/TestValidation/README.md)
