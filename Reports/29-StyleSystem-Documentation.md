> **Historical report.** See [Docs/Overview/](../Docs/Overview/) for current documentation.

# Система стилей NeuroModeler (v2.0 - Modern UI)

## Обзор

Система стилей NeuroModeler обеспечивает централизованное управление визуальным оформлением приложения с поддержкой переключения тем. Она состоит из следующих компонентов:

1. **UStyleManager** — синглтон для доступа к стилям из кода
2. **default.qss** — светлая тема Qt виджетов (QSS)
3. **dark.qss** — тёмная тема Qt виджетов (QSS)
4. **theme.json** — цвета светлой темы для кастомной отрисовки (QPainter)
5. **dark-theme.json** — цвета тёмной темы для кастомной отрисовки

## Поддерживаемые темы

| Тема | QSS файл | JSON файл | Описание |
|------|----------|-----------|----------|
| Modern Light | default.qss | theme.json | Светлая профессиональная тема с градиентами |
| Modern Dark | dark.qss | dark-theme.json | Тёмная тема в стиле современных IDE |

### Переключение тем

В меню **Window → Theme** доступен выбор темы. Переключение применяется мгновенно ко всем виджетам.

```cpp
// Программное переключение темы
UStyleManager::instance()->switchTheme("Modern Dark", qApp);
```

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
│  │  + градиенты    │  │  + тёмная тема  │  │   + эффекты     │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼─────────────────────┼───────────────────┼───────────┘
            │                     │                   │
            ▼                     ▼                   ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│ UModernDiagram    │  │ QTreeWidget       │  │ UDrawEngineImage  │
│ Widget (градиенты,│  │ QDockWidget       │  │ Widget            │
│ тени, свечение)   │  │ QPushButton ...   │  │ (paintDragLine)   │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

## Расположение файлов

| Файл | Расположение (исходники) | Расположение (runtime) |
|------|--------------------------|------------------------|
| UStyleManager.h | `Rdk/GUI/Qt/UStyleManager.h` | — |
| UStyleManager.cpp | `Rdk/GUI/Qt/UStyleManager.cpp` | — |
| default.qss | `Rdk/GUI/Qt/Styles/default.qss` | `Bin/Styles/default.qss` |
| dark.qss | `Rdk/GUI/Qt/Styles/dark.qss` | `Bin/Styles/dark.qss` |
| theme.json | `Rdk/GUI/Qt/Styles/theme.json` | `Bin/Styles/theme.json` |
| dark-theme.json | `Rdk/GUI/Qt/Styles/dark-theme.json` | `Bin/Styles/dark-theme.json` |

При сборке все файлы стилей автоматически копируются из `Rdk/GUI/Qt/Styles/` в `Bin/Styles/`.

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

// Переключение темы
style->switchTheme("Modern Dark", qApp);

// Получение списка доступных тем
QStringList themes = style->getAvailableThemes();
// ["Modern Light", "Modern Dark"]
```

### Геттеры цветов узлов (NodeItem)

| Метод | Описание | Light | Dark |
|-------|----------|-------|------|
| `getNodeFillColor()` | Цвет заливки узла | #FFFFFF | #282C34 |
| `getNodeFillSelectedColor()` | Цвет заливки выделенного узла | #DBEAFE | #2C313A |
| `getNodeBorderColor()` | Цвет рамки узла | #5B8DEF | #61AFEF |
| `getNodeBorderWidth()` | Толщина рамки | 2.0 | 2.0 |
| `getNodeCornerRadius()` | Радиус скругления углов | 10.0 | 10.0 |

### Геттеры градиентов

| Метод | Описание |
|-------|----------|
| `getNodeGradient(QRectF)` | Градиент для заливки узла |
| `getButtonGradient(QRectF)` | Градиент для кнопок |
| `getDockTitleGradient(QRectF)` | Градиент для заголовков dock-виджетов |
| `getHeaderGradient(QRectF)` | Градиент для заголовков таблиц |
| `getNodeGradientTop()` | Верхний цвет градиента узла |
| `getNodeGradientBottom()` | Нижний цвет градиента узла |

### Геттеры эффектов (тени, свечение)

| Метод | Описание | Light | Dark |
|-------|----------|-------|------|
| `getShadowColor()` | Цвет тени | #0000001A | #00000040 |
| `getShadowBlur()` | Радиус размытия тени | 12.0 | 16.0 |
| `getShadowOffsetX()` | Смещение тени по X | 0.0 | 0.0 |
| `getShadowOffsetY()` | Смещение тени по Y | 4.0 | 6.0 |
| `getGlowColor()` | Цвет свечения | #5B8DEF40 | #61AFEF30 |
| `getGlowRadius()` | Радиус свечения | 6.0 | 8.0 |

### Геттеры цветов портов

| Метод | Описание | Light | Dark |
|-------|----------|-------|------|
| `getPortInputColor()` | Цвет входного порта | #10B981 | #98C379 |
| `getPortInputHoverColor()` | Цвет входного порта при наведении | #34D399 | #B5D99C |
| `getPortOutputColor()` | Цвет выходного порта | #5B8DEF | #61AFEF |
| `getPortOutputHoverColor()` | Цвет выходного порта при наведении | #93C5FD | #7EC0F3 |
| `getPortRadius()` | Радиус порта | 5.0 | 5.0 |
| `getPortHoverRadius()` | Радиус порта при наведении | 7.0 | 7.0 |

### Геттеры цветов связей (LinkItem)

| Метод | Описание | Light | Dark |
|-------|----------|-------|------|
| `getLinkColor()` | Цвет постоянной связи | #5B8DEF | #61AFEF |
| `getLinkTempColor()` | Цвет временной связи | #93C5FD | #7EC0F3 |
| `getLinkWidth()` | Толщина линии связи | 2.5 | 2.5 |

### Цвета статусов

| Метод | Описание | Light | Dark |
|-------|----------|-------|------|
| `getSuccessColor()` | Цвет успеха | #10B981 | #98C379 |
| `getWarningColor()` | Цвет предупреждения | #F59E0B | #E5C07B |
| `getErrorColor()` | Цвет ошибки | #EF4444 | #E06C75 |
| `getInfoColor()` | Цвет информации | #5B8DEF | #61AFEF |

### Общие цвета

| Метод | Описание | Light | Dark |
|-------|----------|-------|------|
| `getTextColor()` | Основной цвет текста | #1F2937 | #ABB2BF |
| `getTextSecondaryColor()` | Вторичный цвет текста | #6B7280 | #5C6370 |
| `getBackgroundColor()` | Цвет фона | #F8FAFC | #21252B |
| `getBackgroundAltColor()` | Альтернативный цвет фона | #FFFFFF | #282C34 |
| `getAccentColor()` | Акцентный цвет | #5B8DEF | #61AFEF |
| `getSelectionColor()` | Цвет выделения | #DBEAFE | #2C313A |
| `getDisabledTextColor()` | Цвет неактивного текста | #9CA3AF | #5C6370 |

### Информация о теме

```cpp
QString themeName = style->getThemeName();
// "Modern Light" или "Modern Dark"
```

---

## Формат theme.json (v2.0)

```json
{
  "name": "Modern Light",
  "description": "Clean, professional light theme with subtle gradients",
  
  "node": {
    "fill": "#FFFFFF",
    "fillSelected": "#DBEAFE",
    "border": "#5B8DEF",
    "borderSelected": "#3B82F6",
    "borderWidth": 2.0,
    "cornerRadius": 10.0,
    "gradientTop": "#FFFFFF",
    "gradientBottom": "#F8FAFC"
  },
  
  "port": {
    "inputNormal": "#10B981",
    "inputHover": "#34D399",
    "outputNormal": "#5B8DEF",
    "outputHover": "#93C5FD",
    "radius": 5.0,
    "hoverRadius": 7.0
  },
  
  "link": {
    "solid": "#5B8DEF",
    "dashed": "#93C5FD",
    "width": 2.5,
    "arrowSize": 8.0
  },
  
  "drag": {
    "lineColor": "#5B8DEFC0",
    "portHighlight": "#10B98180"
  },
  
  "text": {
    "primary": "#1F2937",
    "secondary": "#6B7280",
    "accent": "#5B8DEF",
    "onAccent": "#FFFFFF"
  },
  
  "general": {
    "background": "#F8FAFC",
    "backgroundAlt": "#FFFFFF",
    "accent": "#5B8DEF",
    "accentLight": "#DBEAFE",
    "selection": "#DBEAFE",
    "border": "#E2E8F0",
    "borderFocus": "#5B8DEF"
  },
  
  "effects": {
    "shadowColor": "#0000001A",
    "shadowBlur": 12.0,
    "shadowOffsetX": 0.0,
    "shadowOffsetY": 4.0,
    "glowColor": "#5B8DEF40",
    "glowRadius": 6.0
  },
  
  "gradients": {
    "nodeTop": "#FFFFFF",
    "nodeBottom": "#F8FAFC",
    "buttonTop": "#5B8DEF",
    "buttonBottom": "#4F7BE8",
    "dockTitleTop": "#5B8DEF",
    "dockTitleBottom": "#4F7BE8",
    "headerTop": "#F8FAFC",
    "headerBottom": "#F1F5F9"
  },
  
  "chart": {
    "background": "#FFFFFF",
    "axis": "#374151",
    "grid": "#F1F5F9",
    "title": "#1F2937",
    "label": "#6B7280",
    "seriesColors": [
      "#EF4444", "#DC2626", "#F59E0B", "#D97706",
      "#10B981", "#059669", "#06B6D4", "#0891B2",
      "#5B8DEF", "#2563EB", "#8B5CF6", "#7C3AED",
      "#6B7280", "#4B5563", "#1F2937"
    ]
  },
  
  "disabled": {
    "text": "#9CA3AF",
    "background": "#F3F4F6",
    "border": "#E5E7EB"
  },
  
  "success": "#10B981",
  "warning": "#F59E0B",
  "error": "#EF4444",
  "info": "#5B8DEF"
}
```

---

## Визуальные улучшения в Modern UI v2.0

### Узлы с градиентами и тенями

```cpp
void NodeItem::paint(QPainter *painter, ...)
{
    UStyleManager* style = UStyleManager::instance();
    
    // Многослойная тень для эффекта размытия
    QColor shadowColor = style->getShadowColor();
    for (int i = 3; i >= 0; --i) {
        QColor layerColor = shadowColor;
        layerColor.setAlpha(shadowColor.alpha() * (4 - i) / 8);
        painter->setBrush(layerColor);
        painter->drawRoundedRect(shadowRect.adjusted(-i*2, -i*2, i*2, i*2), 
                                 cornerRadius + i, cornerRadius + i);
    }
    
    // Градиентный фон
    QLinearGradient gradient = style->getNodeGradient(rect());
    painter->setBrush(gradient);
    painter->drawRoundedRect(rect(), cornerRadius, cornerRadius);
    
    // Светлая линия сверху для объёма
    painter->setPen(QPen(QColor(255, 255, 255, 80), 1));
    painter->drawLine(topLine);
}
```

### Порты с эффектом свечения

```cpp
// Подсветка при hover
if (isHovered) {
    QColor glowColor = portColor;
    glowColor.setAlpha(60);
    painter->setBrush(glowColor);
    painter->drawEllipse(p.pos, portSize + 4, portSize + 4);
}
```

---

## Добавление переключателя тем в главное окно

Переключатель тем добавляется автоматически в `UGEngineControlWidget`:

```cpp
// UGEngineControlWidget.cpp
void UGEngineControlWidget::createThemeMenu()
{
    QMenu* themeMenu = new QMenu(tr("Theme"), this);
    QActionGroup* themeGroup = new QActionGroup(this);
    themeGroup->setExclusive(true);
    
    QAction* lightAction = themeMenu->addAction(tr("Light"));
    lightAction->setCheckable(true);
    lightAction->setChecked(true);
    themeGroup->addAction(lightAction);
    
    QAction* darkAction = themeMenu->addAction(tr("Dark"));
    darkAction->setCheckable(true);
    themeGroup->addAction(darkAction);
    
    connect(lightAction, &QAction::triggered, [this]() {
        switchToTheme("Modern Light");
    });
    connect(darkAction, &QAction::triggered, [this]() {
        switchToTheme("Modern Dark");
    });
    
    ui->menuWindow->addSeparator();
    ui->menuWindow->addMenu(themeMenu);
}

void UGEngineControlWidget::switchToTheme(const QString& themeName)
{
    UStyleManager* styleManager = UStyleManager::instance();
    if (styleManager->switchTheme(themeName, qApp)) {
        // Принудительное обновление всех виджетов
        for (QWidget* widget : QApplication::allWidgets()) {
            widget->style()->unpolish(widget);
            widget->style()->polish(widget);
            widget->update();
        }
    }
}
```

---

## Цветовая палитра Modern Light

| Элемент | Цвет | HEX |
|---------|------|-----|
| Accent (основной синий) | ![#5B8DEF](https://via.placeholder.com/15/5B8DEF/000000?text=+) | #5B8DEF |
| Accent Light | ![#DBEAFE](https://via.placeholder.com/15/DBEAFE/000000?text=+) | #DBEAFE |
| Background | ![#F8FAFC](https://via.placeholder.com/15/F8FAFC/000000?text=+) | #F8FAFC |
| Surface | ![#FFFFFF](https://via.placeholder.com/15/FFFFFF/000000?text=+) | #FFFFFF |
| Border | ![#E2E8F0](https://via.placeholder.com/15/E2E8F0/000000?text=+) | #E2E8F0 |
| Text Primary | ![#1F2937](https://via.placeholder.com/15/1F2937/000000?text=+) | #1F2937 |
| Text Secondary | ![#6B7280](https://via.placeholder.com/15/6B7280/000000?text=+) | #6B7280 |
| Success (зелёный) | ![#10B981](https://via.placeholder.com/15/10B981/000000?text=+) | #10B981 |
| Warning (жёлтый) | ![#F59E0B](https://via.placeholder.com/15/F59E0B/000000?text=+) | #F59E0B |
| Error (красный) | ![#EF4444](https://via.placeholder.com/15/EF4444/000000?text=+) | #EF4444 |

## Цветовая палитра Modern Dark

| Элемент | Цвет | HEX |
|---------|------|-----|
| Accent (голубой) | ![#61AFEF](https://via.placeholder.com/15/61AFEF/000000?text=+) | #61AFEF |
| Background | ![#21252B](https://via.placeholder.com/15/21252B/000000?text=+) | #21252B |
| Surface | ![#282C34](https://via.placeholder.com/15/282C34/000000?text=+) | #282C34 |
| Border | ![#3E4451](https://via.placeholder.com/15/3E4451/000000?text=+) | #3E4451 |
| Text Primary | ![#ABB2BF](https://via.placeholder.com/15/ABB2BF/000000?text=+) | #ABB2BF |
| Text Secondary | ![#5C6370](https://via.placeholder.com/15/5C6370/000000?text=+) | #5C6370 |
| Success (зелёный) | ![#98C379](https://via.placeholder.com/15/98C379/000000?text=+) | #98C379 |
| Warning (жёлтый) | ![#E5C07B](https://via.placeholder.com/15/E5C07B/000000?text=+) | #E5C07B |
| Error (красный) | ![#E06C75](https://via.placeholder.com/15/E06C75/000000?text=+) | #E06C75 |

---

## Связанные файлы

### Стили
- `Rdk/GUI/Qt/Styles/default.qss` — светлая тема QSS
- `Rdk/GUI/Qt/Styles/dark.qss` — тёмная тема QSS
- `Rdk/GUI/Qt/Styles/theme.json` — светлая тема JSON
- `Rdk/GUI/Qt/Styles/dark-theme.json` — тёмная тема JSON

### Код
- `Rdk/GUI/Qt/UStyleManager.h` — заголовок синглтона
- `Rdk/GUI/Qt/UStyleManager.cpp` — реализация
- `Rdk/GUI/Qt/UModernDiagramWidget.cpp` — использует UStyleManager для отрисовки
- `Rdk/GUI/Qt/UDrawEngineImageWidget.cpp` — использует UStyleManager для drag-линии
- `Rdk/GUI/Qt/UGEngineControlWidget.cpp` — переключатель тем
- `App/NeuroModeler/main.cpp` — инициализация стилей
- `App/NeuroModeler/CMakeLists.txt` — копирование файлов стилей
