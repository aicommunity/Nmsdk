# Валидация конфигураций (Config Validation)

## RU

### Назначение

Проверка целостности проектных конфигураций (`project.ini`, `Model_*.xml`, `Parameters_*.xml`) через `NeuroModelerConsole --check-config`.

### Документация и тесты

- [ConfigValidation-Tests.md](../Testing/ConfigValidation-Tests.md) — обзор интеграционных тестов
- [Tests/Integration/ConfigValidation/README.md](../../Tests/Integration/ConfigValidation/README.md) — детали тестового набора
- [Bin/Configs/TestValidation/](../../Bin/Configs/TestValidation/) — тестовые конфигурации

### Быстрый запуск

```bash
cmake --build build --target Test_ConfigValidation
ctest -R ConfigValidationTests -V
```

---

## EN

### Purpose

Validate project configuration files via `NeuroModelerConsole --check-config`.

### Documentation and tests

- [ConfigValidation-Tests.md](../Testing/ConfigValidation-Tests.md) — integration test overview
- [Tests/Integration/ConfigValidation/README.md](../../Tests/Integration/ConfigValidation/README.md) — test suite details
- [Bin/Configs/TestValidation/](../../Bin/Configs/TestValidation/) — fixture configs

### Quick run

```bash
cmake --build build --target Test_ConfigValidation
ctest -R ConfigValidationTests -V
```
