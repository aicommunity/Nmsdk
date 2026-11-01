# Тесты производительности GetData()

## Быстрый старт

### Запуск тестов

1. Откройте **Visual Studio Developer Command Prompt**
2. Перейдите в директорию проекта:
   ```cmd
   cd E:\Science-Repo\nmsdk-git
   ```
3. Запустите скрипт:
   ```cmd
   run-performance-tests.bat
   ```

Результаты будут сохранены в файл с временной меткой в этой директории.

## Описание тестов

Все тесты находятся в `Rdk/Tests/Unit/Engine/UProperty/Test_UProperty_Performance.cpp`.

### Основные тесты:

1. **GetDataUnconnected** - базовая производительность GetData()
2. **MultipleGetDataCalls** - эффект кэширования при множественных вызовах
3. **GetDataInLoop** - эффект кэширования в циклах
4. **GetDataDifferentTypes** - производительность для разных типов

## Интерпретация результатов

### Ключевые метрики:

- **GetData() unconnected**: должно быть < 1000 ns, ожидается 30-50 ns после оптимизации
- **MultipleGetDataCalls улучшение**: ожидается 60-80%
- **GetDataInLoop улучшение**: ожидается 98-99% для больших циклов

## Документация

- `GetData_Performance_Report.md` - полный отчет с ожидаемыми результатами
- `GetData_Performance_Report_Template.md` - шаблон для заполнения фактическими результатами

