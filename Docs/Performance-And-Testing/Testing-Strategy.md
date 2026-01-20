# Стратегия тестирования (Testing Strategy)

## RU

### Обзор

Стратегия тестирования проекта Nmsdk включает юнит-тесты и интеграционные тесты.

### Типы тестов

#### Юнит-тесты

Тесты отдельных компонентов и модулей:
- Тесты компонентов (`Rdk/Tests/Unit/Engine/UComponent/`)
- Тесты свойств (`Rdk/Tests/Unit/Engine/UProperty/`)
- Тесты контейнеров (`Rdk/Tests/Unit/Engine/UContainer/`)
- Тесты хранилища (`Rdk/Tests/Unit/Engine/UStorage/`)

#### Интеграционные тесты

Тесты взаимодействия между модулями:
- Тесты приложения (`Rdk/Tests/Integration/Application/`)
- Тесты ядра (`Rdk/Tests/Integration/Core/`)

### Запуск тестов

```bash
cd build
ctest
# или
cmake --build . --target test
```

### См. также

- [Rdk/Tests/](../../Rdk/Tests/) - исходный код тестов
- [Reports/33-34](../../Reports/) - результаты тестирования

---

## EN

### Overview

The Nmsdk project testing strategy includes unit tests and integration tests.

### Test Types

#### Unit Tests

Tests of individual components and modules.

#### Integration Tests

Tests of interaction between modules.

### Running Tests

### See Also

- [Rdk/Tests/](../../Rdk/Tests/) - test source code
- [Reports/33-34](../../Reports/) - test results
