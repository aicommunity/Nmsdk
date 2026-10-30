# Сводка: Интеграционные тесты валидации конфигураций

## RU

## ✅ Созданные файлы

### Тесты
- ✅ `Test_ConfigValidation.cpp` - основной файл интеграционных тестов
- ✅ `CMakeLists.txt` - настройка сборки через CMake
- ✅ `README.md` - полная документация
- ✅ `RUN_TESTS.md` - инструкция по запуску
- ✅ `QUICK_START.md` - быстрый старт
- ✅ `INDEX.md` - индекс документации

### Тестовые конфигурации
- ✅ `test_valid/` - валидная конфигурация
- ✅ `test_missing_model/` - отсутствующий файл модели
- ✅ `test_missing_parameters/` - отсутствующий файл параметров
- ✅ `test_invalid_xml/` - невалидный XML
- ✅ `test_empty_model/` - пустая модель
- ✅ `test_invalid_classes/` - несуществующие классы компонентов
- ✅ `test_invalid_links/` - неправильные связи

### Документация
- ✅ `Bin/Configs/TestValidation/README.md` - описание тестовых конфигураций
- ✅ `Docs/Testing/ConfigValidation-Tests.md` - общая документация

## 🎯 Функциональность тестов

Тесты проверяют:
1. ✅ Валидные конфигурации (exit code 0)
2. ✅ Отсутствующие файлы (exit code 1, ошибки)
3. ✅ Невалидный XML (exit code 1, ошибки парсинга)
4. ✅ Пустые модели (exit code 1, предупреждения)
5. ✅ Несуществующие классы компонентов (exit code 1, ошибки классов)
6. ✅ Неправильные связи (exit code 1, ошибки связей)

## 📋 Тестовые данные

### test_invalid_classes
**Файл:** `InvalidClassesModel.xml`

**Содержит:**
- `NonExistentComponent1` с классом `NonExistentClass123`
- `NonExistentComponent2` с классом `FakeComponentClass`
- `ValidComponent` с классом `NPGenerator` (валидный)

### test_invalid_links
**Файл:** `InvalidLinksModel.xml`

**Содержит 5 связей:**
1. Правильная: `Generator1.Output` -> `Neuron1.Soma1.ExcSynapse1.Input`
2. Неправильная: `NonExistentGenerator.Output` -> `Neuron1.Soma1.ExcSynapse1.Input`
3. Неправильная: `Generator1.Output` -> `NonExistentNeuron.Soma1.ExcSynapse1.Input`
4. Неправильная: `Generator1.NonExistentOutput` -> `Neuron1.Soma1.ExcSynapse1.Input`
5. Неправильная: `Generator1.Output` -> `Neuron1.Soma1.ExcSynapse1.NonExistentInput`

## 🚀 Быстрый запуск

```bash
# 1. Сборка
cd build
cmake --build . --target Test_ConfigValidation

# 2. Запуск
ctest -R ConfigValidationTests -V
# или
./Tests/Integration/ConfigValidation/Test_ConfigValidation
```

## 📚 Документация

- **Быстрый старт:** `QUICK_START.md`
- **Полная документация:** `README.md`
- **Инструкция по запуску:** `RUN_TESTS.md`
- **Индекс:** `INDEX.md`

## ✨ Особенности реализации

1. **Кроссплатформенность:** Поддержка Windows и Linux
2. **Автоматический поиск:** Автоматически находит `NeuroModelerConsole` и тестовые конфигурации
3. **Проверка паттернов:** Проверяет не только exit code, но и содержимое вывода
4. **Интеграция с CTest:** Тесты регистрируются в CTest для CI/CD

## 🔍 Проверка вручную

```bash
# Несуществующие классы
./Bin/Platform/Linux/NeuroModelerConsole --check-config \
  Bin/Configs/TestValidation/test_invalid_classes/project.ini

# Неправильные связи
./Bin/Platform/Linux/NeuroModelerConsole --check-config \
  Bin/Configs/TestValidation/test_invalid_links/project.ini
```

## 📝 Примечания

- Все тестовые конфигурации используют формально валидный XML
- Тесты проверяют семантическую валидность (существование классов, компонентов, портов)
- Функциональность валидации может требовать доработки для полного обнаружения всех ошибок

---

## EN

## ✅ Created files

### Tests
- ✅ `Test_ConfigValidation.cpp` — main integration test file
- ✅ `CMakeLists.txt` — CMake build setup
- ✅ `README.md` — full documentation
- ✅ `RUN_TESTS.md` — run instructions
- ✅ `QUICK_START.md` — quick start
- ✅ `INDEX.md` — documentation index

### Test configurations
- ✅ `test_valid/` — valid configuration
- ✅ `test_missing_model/` — missing model file
- ✅ `test_missing_parameters/` — missing parameters file
- ✅ `test_invalid_xml/` — invalid XML
- ✅ `test_empty_model/` — empty model
- ✅ `test_invalid_classes/` — nonexistent component classes
- ✅ `test_invalid_links/` — invalid links

### Documentation
- ✅ `Bin/Configs/TestValidation/README.md` — test configuration description
- ✅ `Docs/Testing/ConfigValidation-Tests.md` — general documentation

## 🎯 Test functionality

Tests verify:
1. ✅ Valid configurations (exit code 0)
2. ✅ Missing files (exit code 1, errors)
3. ✅ Invalid XML (exit code 1, parsing errors)
4. ✅ Empty models (exit code 1, warnings)
5. ✅ Nonexistent component classes (exit code 1, class errors)
6. ✅ Invalid links (exit code 1, link errors)

## 📋 Test data

### test_invalid_classes
**File:** `InvalidClassesModel.xml`

**Contains:**
- `NonExistentComponent1` with class `NonExistentClass123`
- `NonExistentComponent2` with class `FakeComponentClass`
- `ValidComponent` with class `NPGenerator` (valid)

### test_invalid_links
**File:** `InvalidLinksModel.xml`

**Contains 5 links:**
1. Valid: `Generator1.Output` -> `Neuron1.Soma1.ExcSynapse1.Input`
2. Invalid: `NonExistentGenerator.Output` -> `Neuron1.Soma1.ExcSynapse1.Input`
3. Invalid: `Generator1.Output` -> `NonExistentNeuron.Soma1.ExcSynapse1.Input`
4. Invalid: `Generator1.NonExistentOutput` -> `Neuron1.Soma1.ExcSynapse1.Input`
5. Invalid: `Generator1.Output` -> `Neuron1.Soma1.ExcSynapse1.NonExistentInput`

## 🚀 Quick run

```bash
# 1. Build
cd build
cmake --build . --target Test_ConfigValidation

# 2. Run
ctest -R ConfigValidationTests -V
# or
./Tests/Integration/ConfigValidation/Test_ConfigValidation
```

## 📚 Documentation

- **Quick start:** `QUICK_START.md`
- **Full documentation:** `README.md`
- **Run instructions:** `RUN_TESTS.md`
- **Index:** `INDEX.md`

## ✨ Implementation notes

1. **Cross-platform:** Windows and Linux support
2. **Auto-discovery:** Automatically finds `NeuroModelerConsole` and test configurations
3. **Pattern checks:** Verifies exit code and output content
4. **CTest integration:** Tests registered in CTest for CI/CD

## 🔍 Manual verification

```bash
# Nonexistent classes
./Bin/Platform/Linux/NeuroModelerConsole --check-config \
  Bin/Configs/TestValidation/test_invalid_classes/project.ini

# Invalid links
./Bin/Platform/Linux/NeuroModelerConsole --check-config \
  Bin/Configs/TestValidation/test_invalid_links/project.ini
```

## 📝 Notes

- All test configurations use formally valid XML
- Tests check semantic validity (existence of classes, components, ports)
- Validation may need further work to detect all errors fully
