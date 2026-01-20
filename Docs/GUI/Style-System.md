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

### File Locations

- Sources: `Rdk/GUI/Qt/Styles/`
- Runtime: `Bin/Styles/`

### See Also

- [Reports/29-StyleSystem-Documentation.md](../../Reports/29-StyleSystem-Documentation.md) - detailed documentation
- [GUI Overview](Overview.md)
