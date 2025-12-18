# Система стилей NeuroModeler

## Обзор

Система стилей NeuroModeler обеспечивает централизованное управление визуальным оформлением приложения. Она состоит из трёх компонентов:

1. **UStyleManager** — синглтон для доступа к стилям из кода
2. **default.qss** — стили Qt виджетов (QSS)
3. **theme.json** — цвета для кастомной отрисовки (QPainter)

## Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.cpp                                  │
│  UStyleManager::instance()->loadTheme("Styles/theme.json")      │
│  UStyleManager::instance()->loadStyleSheet("Styles/default.qss")│
│  UStyleManager::instance()->applyGlobalStyleSheet(&app)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UStyleManager                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  theme.json     │  │  default.qss    │  │   Геттеры       │  │
│  │  (QPainter)     │  │  (Qt widgets)   │  │   цветов        │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼─────────────────────┼───────────────────┼───────────┘
            │                     │                   │
            ▼                     ▼                   ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│ UModernDiagram    │  │ QTreeWidget       │  │ UDrawEngineImage  │
│ Widget            │  │ QDockWidget       │  │ Widget            │
│ (NodeItem::paint) │  │ QPushButton ...   │  │ (paintDragLine)   │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

## Расположение файлов

| Файл | Расположение (исходники) | Расположение (runtime) |
|------|--------------------------|------------------------|
| UStyleManager.h | `Rdk/GUI/Qt/UStyleManager.h` | — |
| UStyleManager.cpp | `Rdk/GUI/Qt/UStyleManager.cpp` | — |
| default.qss | `Rdk/GUI/Qt/Styles/default.qss` | `Bin/Styles/default.qss` |
| theme.json | `Rdk/GUI/Qt/Styles/theme.json` | `Bin/Styles/theme.json` |

При сборке файлы стилей автоматически копируются из `Rdk/GUI/Qt/Styles/` в `Bin/Styles/`.

---

## UStyleManager API

### Инициализация

```cpp
#include "UStyleManager.h"

// Получение экземпляра синглтона
UStyleManager* style = UStyleManager::instance();

// Загрузка темы (цвета для QPainter)
style->loadTheme("Styles/theme.json");

// Загрузка QSS стилей
style->loadStyleSheet("Styles/default.qss");

// Применение QSS ко всему приложению
style->applyGlobalStyleSheet(qApp);
```

### Геттеры цветов узлов (NodeItem)

| Метод | Описание | По умолчанию |
|-------|----------|--------------|
| `getNodeFillColor()` | Цвет заливки узла | #F5F5F5 |
| `getNodeFillSelectedColor()` | Цвет заливки выделенного узла | #DCF0FF |
| `getNodeBorderColor()` | Цвет рамки узла | #4678C8 |
| `getNodeBorderWidth()` | Толщина рамки | 1.5 |
| `getNodeCornerRadius()` | Радиус скругления углов | 6.0 |

### Геттеры цветов портов

| Метод | Описание | По умолчанию |
|-------|----------|--------------|
| `getPortInputColor()` | Цвет входного порта | #329632 |
| `getPortInputHoverColor()` | Цвет входного порта при наведении | #64C864 |
| `getPortOutputColor()` | Цвет выходного порта | #3264C8 |
| `getPortOutputHoverColor()` | Цвет выходного порта при наведении | #6496FF |
| `getPortRadius()` | Радиус порта | 4.0 |
| `getPortHoverRadius()` | Радиус порта при наведении | 5.0 |

### Геттеры цветов связей (LinkItem)

| Метод | Описание | По умолчанию |
|-------|----------|--------------|
| `getLinkColor()` | Цвет постоянной связи | #5078C8 |
| `getLinkTempColor()` | Цвет временной связи | #78A0DC |
| `getLinkWidth()` | Толщина линии связи | 2.0 |

### Геттеры для drag & drop

| Метод | Описание | По умолчанию |
|-------|----------|--------------|
| `getDragLineColor()` | Цвет линии при перетаскивании | rgba(100,100,255,200) |
| `getPortHighlightColor()` | Цвет подсветки целевого порта | rgba(0,200,0,150) |

### Общие цвета

| Метод | Описание | По умолчанию |
|-------|----------|--------------|
| `getTextColor()` | Основной цвет текста | #000000 |
| `getTextSecondaryColor()` | Вторичный цвет текста | #646464 |
| `getBackgroundColor()` | Цвет фона | #FFFFFF |
| `getBackgroundAltColor()` | Альтернативный цвет фона | #F5F5F5 |
| `getAccentColor()` | Акцентный цвет | #4678C8 |
| `getSelectionColor()` | Цвет выделения | #E0E0E0 |

### Цвета графиков (QChart, UWatchChart)

| Метод | Описание | По умолчанию |
|-------|----------|--------------|
| `getChartBackgroundColor()` | Фон графика | #FFFFFF |
| `getChartAxisColor()` | Цвет осей | #333333 |
| `getChartGridColor()` | Цвет сетки | #E0E0E0 |
| `getChartTitleColor()` | Цвет заголовка | #333333 |
| `getChartLabelColor()` | Цвет подписей | #666666 |
| `getChartSeriesColors()` | Массив цветов серий | 15 цветов |
| `getChartSeriesColor(int)` | Цвет серии по индексу (циклически) | — |
| `getChartSeriesColorCount()` | Количество цветов серий | 15 |

### Цвета для отключенных элементов

| Метод | Описание | По умолчанию |
|-------|----------|--------------|
| `getDisabledTextColor()` | Цвет текста для неактивных элементов | #999999 |

### Специальные методы

```cpp
// Получить stylesheet для QTreeWidget (списка портов)
QString treeStyle = style->getTreeWidgetStyleSheet();
m_portListWidget->setStyleSheet(treeStyle);

// Получить полный QSS stylesheet
QString fullStyle = style->getStyleSheet();
```

---

## Формат theme.json

```json
{
  "name": "Default Theme",
  "description": "Описание темы",
  
  "node": {
    "fill": "#F5F5F5",
    "fillSelected": "#DCF0FF",
    "border": "#4678C8",
    "borderWidth": 1.5,
    "cornerRadius": 6.0
  },
  
  "port": {
    "inputNormal": "#329632",
    "inputHover": "#64C864",
    "outputNormal": "#3264C8",
    "outputHover": "#6496FF",
    "radius": 4.0,
    "hoverRadius": 5.0
  },
  
  "link": {
    "solid": "#5078C8",
    "dashed": "#78A0DC",
    "width": 2.0
  },
  
  "drag": {
    "lineColor": "#6464FFC8",
    "portHighlight": "#00C80096"
  },
  
  "text": {
    "primary": "#000000",
    "secondary": "#646464"
  },
  
  "general": {
    "background": "#FFFFFF",
    "backgroundAlt": "#F5F5F5",
    "accent": "#4678C8",
    "selection": "#E0E0E0"
  },
  
  "chart": {
    "background": "#FFFFFF",
    "axis": "#333333",
    "grid": "#E0E0E0",
    "title": "#333333",
    "label": "#666666",
    "seriesColors": [
      "#E63946", "#8B0000", "#F4D35E", "#DAA520",
      "#2A9D8F", "#006400", "#00CED1", "#008B8B",
      "#4678C8", "#00008B", "#E040FB", "#8B008B",
      "#808080", "#404040", "#000000"
    ]
  },
  
  "disabled": {
    "text": "#999999"
  }
}
```

### Формат цветов

- **HEX**: `"#RRGGBB"` или `"#RRGGBBAA"` (с альфа-каналом)
- Примеры:
  - `"#FF0000"` — красный
  - `"#00FF0080"` — зелёный с 50% прозрачностью

---

## Формат default.qss

QSS (Qt Style Sheets) — CSS-подобный синтаксис для стилизации Qt виджетов.

### Основные селекторы

```css
/* Все виджеты типа QPushButton */
QPushButton {
    background-color: #F5F5F5;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 6px 16px;
}

/* Состояние при наведении */
QPushButton:hover {
    background-color: #DCF0FF;
    border-color: #4678C8;
}

/* Состояние при нажатии */
QPushButton:pressed {
    background-color: #4678C8;
    color: #FFFFFF;
}

/* Отключённое состояние */
QPushButton:disabled {
    color: #AAAAAA;
}
```

### Виджеты со стилями в default.qss

- **Меню**: QMenuBar, QMenu
- **Панели**: QToolBar, QDockWidget, QStatusBar
- **Вкладки**: QTabWidget, QTabBar
- **Списки**: QTreeWidget, QTreeView, QTableWidget, QTableView, QListWidget, QListView
- **Поля ввода**: QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox
- **Кнопки**: QPushButton, QToolButton, QCheckBox, QRadioButton
- **Прочее**: QScrollBar, QSlider, QProgressBar, QGroupBox, QSplitter, QToolTip

---

## Использование в коде

### Пример: Кастомная отрисовка узла

```cpp
#include "UStyleManager.h"

void NodeItem::paint(QPainter *painter, ...)
{
    UStyleManager* style = UStyleManager::instance();
    
    // Цвет заливки зависит от состояния выделения
    QColor fill = isSelected() 
        ? style->getNodeFillSelectedColor() 
        : style->getNodeFillColor();
    
    // Рисуем узел
    painter->setPen(QPen(style->getNodeBorderColor(), 
                         style->getNodeBorderWidth()));
    painter->setBrush(fill);
    painter->drawRoundedRect(rect(), 
                             style->getNodeCornerRadius(), 
                             style->getNodeCornerRadius());
    
    // Рисуем порты
    for (const Port& p : inputs) {
        bool isHovered = (m_hoveredPort == &p);
        QColor portColor = isHovered 
            ? style->getPortInputHoverColor() 
            : style->getPortInputColor();
        double portSize = isHovered 
            ? style->getPortHoverRadius() 
            : style->getPortRadius();
        painter->setPen(QPen(portColor, isHovered ? 2.0 : 1.0));
        painter->drawEllipse(p.pos, portSize, portSize);
    }
}
```

### Пример: Создание связи

```cpp
#include "UStyleManager.h"

LinkItem::LinkItem(NodeItem* src, NodeItem* dst, ...)
{
    UStyleManager* style = UStyleManager::instance();
    setPen(QPen(style->getLinkColor(), 
                style->getLinkWidth(), 
                Qt::SolidLine, Qt::RoundCap, Qt::RoundJoin));
}

// Временная связь (при перетаскивании)
LinkItem::LinkItem(NodeItem* src, const QPointF& tempEnd, ...)
{
    UStyleManager* style = UStyleManager::instance();
    setPen(QPen(style->getLinkTempColor(), 
                style->getLinkWidth(), 
                Qt::DashLine, Qt::RoundCap, Qt::RoundJoin));
}
```

### Пример: Стилизация QTreeWidget

```cpp
#include "UStyleManager.h"

// Применение стиля к виджету списка портов
m_portListWidget = new QTreeWidget();
m_portListWidget->setStyleSheet(
    UStyleManager::instance()->getTreeWidgetStyleSheet()
);
```

---

## Создание новой темы

### 1. Создайте файл темы

Скопируйте `theme.json` и измените цвета:

```json
// Rdk/GUI/Qt/Styles/dark-theme.json
{
  "name": "Dark Theme",
  
  "node": {
    "fill": "#2D2D2D",
    "fillSelected": "#3D5A80",
    "border": "#5A9BD5"
  },
  
  "text": {
    "primary": "#FFFFFF",
    "secondary": "#AAAAAA"
  },
  
  "general": {
    "background": "#1E1E1E",
    "backgroundAlt": "#2D2D2D",
    "accent": "#5A9BD5",
    "selection": "#3D5A80"
  }
}
```

### 2. Создайте QSS файл (опционально)

```css
/* Rdk/GUI/Qt/Styles/dark.qss */
QWidget {
    background-color: #1E1E1E;
    color: #FFFFFF;
}

QPushButton {
    background-color: #2D2D2D;
    border: 1px solid #5A9BD5;
}
/* ... */
```

### 3. Загрузите тему в приложении

```cpp
UStyleManager* style = UStyleManager::instance();
style->loadTheme("Styles/dark-theme.json");
style->loadStyleSheet("Styles/dark.qss");
style->applyGlobalStyleSheet(qApp);
```

---

## Цветовая палитра по умолчанию

### Основные цвета

| Название | HEX | Использование |
|----------|-----|---------------|
| Accent Blue | #4678C8 | Рамки узлов, акценты, выделение |
| Light Blue | #DCF0FF | Фон выделенного узла, hover |
| Light Gray | #F5F5F5 | Фон узлов, альтернативный фон |
| White | #FFFFFF | Основной фон |
| Border Gray | #E0E0E0 | Границы виджетов |
| Selection Gray | #E0E0E0 | Выделение в списках |

### Цвета портов

| Тип | Обычный | Hover |
|-----|---------|-------|
| Input (зелёный) | #329632 | #64C864 |
| Output (синий) | #3264C8 | #6496FF |

### Цвета связей

| Тип | Цвет |
|-----|------|
| Постоянная связь | #5078C8 |
| Временная связь | #78A0DC |

---

## Обновление CMakeLists.txt

При добавлении новых файлов стилей обновите `App/NeuroModeler/CMakeLists.txt`:

```cmake
# Copy style files to output directory
set(STYLES_SOURCE_DIR "${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Styles")
set(STYLES_DEST_DIR "${CMAKE_SOURCE_DIR}/Bin/Styles")

add_custom_command(TARGET NeuroModeler POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${STYLES_DEST_DIR}"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${STYLES_SOURCE_DIR}/default.qss"
        "${STYLES_DEST_DIR}/default.qss"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${STYLES_SOURCE_DIR}/theme.json"
        "${STYLES_DEST_DIR}/theme.json"
    # Добавьте новые файлы здесь:
    # COMMAND ${CMAKE_COMMAND} -E copy_if_different
    #     "${STYLES_SOURCE_DIR}/dark.qss"
    #     "${STYLES_DEST_DIR}/dark.qss"
    COMMENT "Copying style files to Bin/Styles/"
)
```

---

## Связанные файлы

- `Rdk/GUI/Qt/UStyleManager.h` — заголовок синглтона
- `Rdk/GUI/Qt/UStyleManager.cpp` — реализация
- `Rdk/GUI/Qt/Styles/default.qss` — базовые QSS стили
- `Rdk/GUI/Qt/Styles/theme.json` — цвета для QPainter
- `Rdk/GUI/Qt/UModernDiagramWidget.cpp` — использует UStyleManager для отрисовки
- `Rdk/GUI/Qt/UDrawEngineImageWidget.cpp` — использует UStyleManager для drag-линии
- `App/NeuroModeler/main.cpp` — инициализация стилей
- `App/NeuroModeler/CMakeLists.txt` — копирование файлов стилей

