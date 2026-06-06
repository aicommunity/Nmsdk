# Система стилей (Style System)

## RU

### Обзор

Система стилей NeuroModeler обеспечивает централизованное управление визуальным оформлением приложения с поддержкой переключения тем.

### Компоненты системы

1. **UStyleManager** - синглтон для доступа к стилям из кода
2. **default.qss** - светлая тема Qt виджетов (QSS)
3. **dark.qss** - тёмная тема Qt виджетов (QSS)
4. **theme.json** - цвета светлой темы для кастомной отрисовки (QPainter)
5. **dark-theme.json** - цвета тёмной темы для кастомной отрисовки

**Архитектура системы стилей:**

```mermaid
classDiagram
    class UStyleManager {
        <<singleton>>
        +instance()
        +loadTheme()
        +loadStyleSheet()
        +switchTheme()
        +getNodeFillColor()
        +getPortInputColor()
        +getLinkColor()
    }
    
    class QApplication {
        +setStyleSheet()
    }
    
    class UModernDiagramWidget {
        +updateTheme()
    }
    
    class UModernDiagramNodeItem {
        +paint()
    }
    
    UStyleManager --> QApplication
    UModernDiagramWidget --> UStyleManager
    UModernDiagramNodeItem --> UStyleManager
```

**Процесс применения стилей:**

```mermaid
flowchart TB
    Start[Запуск приложения] --> Load[UStyleManager::loadTheme]
    Load --> Parse[Парсинг theme.json]
    Parse --> QSS[Загрузка .qss файла]
    QSS --> Apply[applyGlobalStyleSheet]
    Apply --> Widgets[Применение к виджетам]
    
    Switch[Переключение темы] --> Reload[switchTheme]
    Reload --> Parse
    Reload --> Invalidate[Инвалидация кэша]
    Invalidate --> Repaint[Перерисовка виджетов]
```

### Поддерживаемые темы

- **Modern Light** - светлая профессиональная тема с градиентами
- **Modern Dark** - тёмная тема в стиле современных IDE

### Использование

```cpp
// Получение экземпляра синглтона
UStyleManager* style = UStyleManager::instance();

// Загрузка темы
style->loadTheme("Styles/theme.json");

// Загрузка QSS стилей
style->loadStyleSheet("Styles/default.qss");

// Применение стилей
style->applyGlobalStyleSheet(qApp);

// Переключение темы
style->switchTheme("Modern Dark", qApp);
```

`UStyleManager` загружает цвета из JSON файлов (`theme.json`, `dark-theme.json`) и применяет QSS стили к `QApplication`. Виджеты получают цвета через методы `getNodeFillColor()`, `getPortInputColor()` и т.д. для кастомной отрисовки через `QPainter`. При переключении темы виджеты вызывают `updateTheme()` для инвалидации кэша и перерисовки.

### Расположение файлов

- Исходники: `Rdk/GUI/Qt/Styles/`
- Runtime: `Bin/Styles/`

### См. также

- [Reports/29-StyleSystem-Documentation.md](../../Reports/29-StyleSystem-Documentation.md) - детальная документация
- [GUI Overview](Overview.md)

---

## EN

### Overview

The NeuroModeler style system provides centralized management of application visual styling with theme switching support.

### System Components

1. **UStyleManager** - singleton for accessing styles from code
2. **default.qss** - light theme for Qt widgets (QSS)
3. **dark.qss** - dark theme for Qt widgets (QSS)
4. **theme.json** - light theme colors for custom rendering (QPainter)
5. **dark-theme.json** - dark theme colors for custom rendering

### Supported Themes

- **Modern Light** - light professional theme with gradients
- **Modern Dark** - dark theme in modern IDE style

### Usage

`UStyleManager` loads colors from JSON files (`theme.json`, `dark-theme.json`) and applies QSS styles to `QApplication`. Widgets get colors through methods like `getNodeFillColor()`, `getPortInputColor()`, etc. for custom rendering via `QPainter`. When switching themes, widgets call `updateTheme()` to invalidate cache and repaint.

### File Locations

- Sources: `Rdk/GUI/Qt/Styles/`
- Runtime: `Bin/Styles/`

### See Also

- [Reports/29-StyleSystem-Documentation.md](../../Reports/29-StyleSystem-Documentation.md) - detailed documentation
- [GUI Overview](Overview.md)

```mermaid
classDiagram
    class UStyleManager {
        <<singleton>>
        +instance()
        +loadTheme()
        +loadStyleSheet()
        +switchTheme()
        +getNodeFillColor()
        +getPortInputColor()
        +getLinkColor()
    }
    
    class QApplication {
        +setStyleSheet()
    }
    
    class UModernDiagramWidget {
        +updateTheme()
    }
    
    class UModernDiagramNodeItem {
        +paint()
    }
    
    UStyleManager --> QApplication
    UModernDiagramWidget --> UStyleManager
    UModernDiagramNodeItem --> UStyleManager
```

```mermaid
flowchart TB
    Start[Запуск приложения] --> Load[UStyleManager::loadTheme]
    Load --> Parse[Парсинг theme.json]
    Parse --> QSS[Загрузка .qss файла]
    QSS --> Apply[applyGlobalStyleSheet]
    Apply --> Widgets[Применение к виджетам]
    
    Switch[Переключение темы] --> Reload[switchTheme]
    Reload --> Parse
    Reload --> Invalidate[Инвалидация кэша]
    Invalidate --> Repaint[Перерисовка виджетов]
```
