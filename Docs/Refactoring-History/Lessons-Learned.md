# Извлеченные уроки (Lessons Learned)

## RU

### Обзор

Важные выводы и практики, извлеченные в процессе разработки и рефакторинга проекта Nmsdk.

### Основные уроки

1. **Оптимизация доступа к свойствам** - прямой доступ к свойствам значительно улучшает производительность
2. **Кэширование активных компонентов** - кэширование списка активных компонентов ускоряет выполнение
3. **Обработка исключений** - правильная обработка исключений критична для стабильности
4. **Кроссплатформенность** - использование абстракций упрощает поддержку разных платформ

### Детальные отчеты

- [Reports/35-37](../../Reports/) - отчеты об инцидентах и исправлениях
- [Reports/37](../../Reports/37-Lessons-Learned-QMessageBox-Crash.md) - уроки из инцидента с QMessageBox

### См. также

- [Refactoring Timeline](Refactoring-Timeline.md) - хронология рефакторинга

---

## EN

### Overview

Important insights and practices learned during the development and refactoring of the Nmsdk project.

### Main Lessons

1. **Property Access Optimization** - direct property access significantly improves performance
2. **Active Component Caching** - caching the list of active components speeds up execution
3. **Exception Handling** - proper exception handling is critical for stability
4. **Cross-Platform Support** - using abstractions simplifies support for different platforms

### Detailed Reports

- [Reports/35-37](../../Reports/) - incident and fix reports
- [Reports/37](../../Reports/37-Lessons-Learned-QMessageBox-Crash.md) - lessons from QMessageBox incident

### See Also

- [Refactoring Timeline](Refactoring-Timeline.md) - refactoring timeline
