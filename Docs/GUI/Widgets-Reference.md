# Справочник виджетов (Widgets Reference)

## RU

### Обзор

Описание основных виджетов GUI приложения Nmsdk.

### Основные виджеты

#### UModernDiagramWidget

Визуальный редактор диаграмм компонентов.

**Основные функции:**
- Создание и редактирование компонентов
- Соединение компонентов
- Визуализация сетей компонентов
- Drag & Drop операции

`UModernDiagramWidget` использует архитектуру Qt Graphics Framework: `UModernDiagramScene` (QGraphicsScene) содержит элементы (`UModernDiagramNodeItem`, `UModernDiagramLinkItem`), а `UModernDiagramView` (QGraphicsView) отображает сцену. Виджет управляет кэшированием (`UModernDiagramCacheManager`), координатами (`UModernDiagramCoordinateManager`), viewport (`UModernDiagramViewportManager`) и контекстным меню (`UModernDiagramContextMenu`).

**Архитектура виджета:**

```mermaid
classDiagram
    class UModernDiagramWidget {
        +SetApplication()
        +SetComponentName()
        +Reload()
        +updateScheme()
    }
    
    class UModernDiagramScene {
        +NodeItems
        +LinkItems
        +addNode()
        +addLink()
    }
    
    class UModernDiagramView {
        +setScene()
        +viewport()
    }
    
    class UModernDiagramNodeItem {
        +InputPorts
        +OutputPorts
        +paint()
    }
    
    class UModernDiagramLinkItem {
        +SourcePort
        +TargetPort
        +paint()
    }
    
    class UModernDiagramPortManager {
        +Ports
        +ConnectPorts()
    }
    
    UModernDiagramWidget --> UModernDiagramScene
    UModernDiagramWidget --> UModernDiagramView
    UModernDiagramScene --> UModernDiagramNodeItem
    UModernDiagramScene --> UModernDiagramLinkItem
    UModernDiagramNodeItem --> UModernDiagramPortManager
```

**Взаимодействие с движком:**

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant DiagramWidget as UModernDiagramWidget
    participant Engine as UEngine
    participant Component as UComponent
    
    User->>DiagramWidget: Добавить компонент
    DiagramWidget->>Engine: CreateComponent()
    Engine->>Component: Создание экземпляра
    Component-->>Engine: Готов
    Engine-->>DiagramWidget: Компонент создан
    DiagramWidget->>DiagramWidget: Отображение компонента
    
    User->>DiagramWidget: Соединить компоненты
    DiagramWidget->>Engine: ConnectProperties()
    Engine->>Component: Установка соединения
    Component-->>DiagramWidget: Соединение установлено
```

#### UDrawEngineImageWidget

Виджет для отображения изображений из компонентов.

Использует `UDrawEngine` для отрисовки схемы компонентов в растровом формате. Работает совместно с `UModernDiagramWidget` в `UDrawEngineWidget`, предоставляя альтернативный способ визуализации (legacy режим).

#### UGEngineControlWidget

Виджет управления движком выполнения.

**Основные функции:**
- Запуск/остановка выполнения
- Управление шагами времени
- Мониторинг состояния

`UGEngineControlWidget` является главным окном приложения (`UVisualControllerMainWidget`) и содержит все основные виджеты: `UModernDiagramWidget`, `UComponentsListWidget`, `UComponentPropertyChanger`, `ULoggerWidget`, `UGraphWidget` и др. Он управляет жизненным циклом приложения и координирует взаимодействие между виджетами.

**Взаимодействие с движком:**

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant ControlWidget as UGEngineControlWidget
    participant EngineControl as UEngineControl
    participant Engine as UEngine
    participant Environment as UEnvironment
    
    User->>ControlWidget: Нажать Start
    ControlWidget->>EngineControl: Start()
    EngineControl->>Engine: StartExecution()
    Engine->>Environment: Start()
    Environment->>Environment: Инициализация выполнения
    
    loop Каждый шаг времени
        Environment->>Environment: ExecuteStep()
        Environment-->>ControlWidget: Обновление статуса
    end
    
    User->>ControlWidget: Нажать Stop
    ControlWidget->>EngineControl: Stop()
    EngineControl->>Engine: StopExecution()
    Engine->>Environment: Stop()
```

#### UComponentPropertyChanger

Редактор свойств компонентов.

**Основные функции:**
- Редактирование параметров компонентов
- Настройка входов и выходов
- Валидация значений

`UComponentPropertyChanger` отображает свойства выбранного компонента в виде дерева (`QTreeWidget`) и позволяет редактировать их значения. Автоматически обновляется при изменении выбранного компонента в диаграмме или списке компонентов.

#### ULoggerWidget

Окно логов для мониторинга выполнения.

**Основные функции:**
- Отображение логов выполнения
- Фильтрация по уровням
- Поиск в логах

#### UGraphWidget

Виджет для визуализации графиков данных компонентов.

**Основные функции:**
- Отображение временных рядов
- Настройка осей и масштаба
- Экспорт графиков

**Процесс обновления интерфейса:**

```mermaid
flowchart TB
    Timer[QTimer<br/>UEngineControlQt] --> Update[AUpdateInterface]
    Update --> DiagramWidget[UModernDiagramWidget<br/>Reload]
    Update --> DrawWidget[UDrawEngineWidget<br/>AUpdateInterface]
    Update --> PropertyWidget[UComponentPropertyChanger<br/>Update]
    Update --> GraphWidget[UGraphWidget<br/>Update]
    
    DiagramWidget --> Scene[UModernDiagramScene<br/>Обновление узлов]
    DrawWidget --> DrawEngine[UDrawEngine<br/>Draw]
    
    Scene --> App[UApplication<br/>GetEngine]
    DrawEngine --> App
    App --> Engine[UEngine<br/>GetComponent]
```

`UEngineControlQt` запускает таймер (интервал 16 мс для режима 0 или `MTUpdateInterfaceInterval` для режима 1), который вызывает `AUpdateInterface()` у всех виджетов, наследующих `UVisualControllerWidget`. Виджеты обновляют своё состояние, читая данные из `UApplication` и `UEngine`.

### См. также

- [GUI Overview](Overview.md)
- [Bin/Help](../../Bin/Help/) - пользовательская справка

---

## EN

### Overview

Description of main widgets in Nmsdk GUI application.

### Main Widgets

#### UModernDiagramWidget

Visual diagram editor for components.

`UModernDiagramWidget` uses Qt Graphics Framework architecture: `UModernDiagramScene` (QGraphicsScene) contains items (`UModernDiagramNodeItem`, `UModernDiagramLinkItem`), and `UModernDiagramView` (QGraphicsView) displays the scene. The widget manages caching (`UModernDiagramCacheManager`), coordinates (`UModernDiagramCoordinateManager`), viewport (`UModernDiagramViewportManager`), and context menu (`UModernDiagramContextMenu`).

#### UDrawEngineImageWidget

Widget for displaying images from components.

Uses `UDrawEngine` to render component diagrams in bitmap format. Works together with `UModernDiagramWidget` in `UDrawEngineWidget`, providing an alternative visualization method (legacy mode).

#### UGEngineControlWidget

Widget for controlling execution engine.

`UGEngineControlWidget` is the main application window (`UVisualControllerMainWidget`) and contains all main widgets: `UModernDiagramWidget`, `UComponentsListWidget`, `UComponentPropertyChanger`, `ULoggerWidget`, `UGraphWidget`, etc. It manages the application lifecycle and coordinates interaction between widgets.

#### UComponentPropertyChanger

Component property editor.

`UComponentPropertyChanger` displays properties of the selected component as a tree (`QTreeWidget`) and allows editing their values. Automatically updates when the selected component changes in the diagram or component list.

#### ULoggerWidget

Log window for execution monitoring.

#### UGraphWidget

Widget for visualizing component data graphs.

**Interface update process:**

`UEngineControlQt` starts a timer (16 ms interval for mode 0 or `MTUpdateInterfaceInterval` for mode 1), which calls `AUpdateInterface()` on all widgets inheriting `UVisualControllerWidget`. Widgets update their state by reading data from `UApplication` and `UEngine`.

### See Also

- [GUI Overview](Overview.md)
- [Bin/Help](../../Bin/Help/) - user help
