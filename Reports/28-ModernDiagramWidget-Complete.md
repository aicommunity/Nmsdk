# Modern Diagram Widget - Полная документация

## Обзор

`UModernDiagramWidget` - современный виджет для визуализации диаграмм компонентов, построенный на основе Qt `QGraphicsView`/`QGraphicsScene`. Предназначен для параллельной работы с классическим виджетом `UDrawEngineImageWidget` и предоставляет улучшенный пользовательский интерфейс с поддержкой drag & drop, масштабирования и интерактивного управления компонентами.

## Архитектура

### Основные компоненты

1. **UModernDiagramWidget** (`Rdk/GUI/Qt/UModernDiagramWidget.h/.cpp`)
   - Главный виджет-контейнер
   - Управляет сценой, основным видом и миникартой
   - Обрабатывает координаты и взаимодействие с ядром

2. **ModernScene** (внутренний класс)
   - Наследник `QGraphicsScene`
   - Обрабатывает события мыши (клики, двойные клики, drag & drop)
   - Управляет созданием временных связей

3. **ModernGraphicsView** (внутренний класс)
   - Наследник `QGraphicsView`
   - Обрабатывает масштабирование колесом мыши
   - Отображает сцену с поддержкой скроллбаров

4. **NodeItem** (внутренний класс)
   - Наследник `QGraphicsRectItem`
   - Представляет компонент на диаграмме
   - Отображает имя, класс и порты (входы/выходы)
   - Поддерживает перемещение и выделение

5. **LinkItem** (внутренний класс)
   - Наследник `QGraphicsPathItem`
   - Представляет связь между компонентами
   - Динамически обновляет путь при перемещении узлов
   - Поддерживает временные связи при drag & drop

## Функциональность

### Отображение компонентов

- Компоненты отображаются как прямоугольные узлы с закругленными углами
- Каждый узел показывает:
  - Имя компонента
  - Класс компонента
  - Входные порты (зеленые кружки слева)
  - Выходные порты (синие кружки справа)
- Размер узла: 120x60 пикселей
- Цвета:
  - Обычное состояние: светло-серый фон (#F5F5F5)
  - Выделенное состояние: светло-голубой фон (#DCF0FF)
  - Граница: синий (#4678C8)

### Навигация по вложенным компонентам

- **Вход внутрь компонента**: двойной клик левой кнопкой мыши по узлу
  - Добавляет имя узла к пути `m_componentName`
  - Перезагружает диаграмму с содержимым выбранного компонента
  - Испускает сигнал `componentDoubleClicked(QString)`

- **Выход на уровень выше**: двойной клик правой кнопкой мыши по холсту
  - Удаляет последний сегмент из пути `m_componentName`
  - Перезагружает диаграмму с родительским компонентом
  - Испускает сигнал `componentStapBack()`

### Создание связей (Drag & Drop)

- **Начало создания связи**: клик левой кнопкой мыши на выходной порт
  - Создается временная пунктирная линия от порта к курсору
  - Выбор компонентов отключается во время перетаскивания

- **Завершение создания связи**: отпускание кнопки мыши на входном порте
  - Создается постоянная связь между узлами
  - Вызывается `Model_CreateLinkByName()` для создания связи в ядре
  - Временная линия удаляется

- **Отмена**: отпускание кнопки мыши не на порте
  - Временная линия удаляется
  - Операция отменяется

### Выделение и перемещение

- **Выделение**: клик левой кнопкой мыши по узлу
  - Узел выделяется визуально
  - Испускается сигнал `componentSelected(QString)`
  - Поддерживается множественное выделение через rubber-band (перетаскивание с зажатой левой кнопкой)

- **Перемещение**: перетаскивание выделенных узлов
  - Координаты автоматически сохраняются в ядро через `saveCoord()`
  - Связи автоматически обновляются при перемещении узлов
  - Координаты нормализуются для обеспечения положительных значений в ядре

### Удаление компонентов

- **Удаление**: клавиша `Delete` при выделенных узлах
  - Вызывается `Model_DelComponent()` для каждого выделенного компонента
  - Диаграмма перезагружается
  - Испускается сигнал `updateComponentsList()`

### Контекстное меню

Контекстное меню открывается правым кликом по компоненту и содержит следующие действия:

#### Управление связями
- **View/Break link** - просмотр/разрыв связи (испускает `viewLinks(QString)`)
- **Create link** - начало создания связи между компонентами
- **Finish link** / **Cancel link** - завершение/отмена создания связи
- **Switch link** - переключение связи между компонентами
- **Finish switching** / **Cancel switching** - завершение/отмена переключения
- **Quick Link...** - быстрое создание связи через диалог `UQuickLinkDialog`

#### Управление компонентами
- **Start moving** - начало перемещения компонента
- **Finish moving** / **Cancel moving** - завершение/отмена перемещения
- **Rename** - переименование компонента (через `QInputDialog`)
- **Delete** - удаление компонента (с подтверждением, если не зажат Shift)
- **Clone** - клонирование компонента

#### Информация
- **Class Description** - открытие окна с описанием класса компонента
- **Copy name to Clipboard** - копирование имени компонента
- **Copy long name to Clipboard** - копирование полного имени компонента
- **Copy class to Clipboard** - копирование класса компонента
- **Copy component XML description** - копирование XML описания компонента

#### Операции с компонентом
- **Reset** - сброс состояния компонента (`Env_Reset()`)
- **Calculate** - вычисление компонента (`Env_Calculate()`)
- **Default** - сброс параметров компонента к значениям по умолчанию
- **GUI (not implemented)** - GUI компонента (не реализовано)

### Масштабирование

- **Масштабирование колесом мыши**: прокрутка колеса вверх/вниз
  - Коэффициент масштабирования: 1.15x при прокрутке вверх, 0.87x при прокрутке вниз
  - Масштабирование применяется к виду, не к сцене

- **Автоматическая подгонка**: метод `FitToView()`
  - Автоматически подгоняет вид под все элементы сцены
  - Добавляет отступы 40 пикселей со всех сторон

### Системы координат и преобразования

Виджет использует три системы координат для корректной работы с компонентами на разных уровнях вложенности:

#### 1. Координаты ядра (Kernel Coordinates)

**Определение**: Абсолютные координаты компонентов, хранящиеся в ядре системы через параметр `Coord`.

**Характеристики**:
- Единицы измерения: логические единицы ядра (не пиксели)
- Начало координат: (0, 0) в верхнем левом углу корневого компонента
- Диапазон: неотрицательные значения (x ≥ 0, y ≥ 0)
- Хранение: параметр компонента `Coord` в формате XML или plain text

**Формат хранения**:
```xml
<Coord>
  <MVector Type="MVector" Size="3">
    <Item>4.7</Item>  <!-- x -->
    <Item>0.67</Item> <!-- y -->
    <Item>0.0</Item>  <!-- z (не используется) -->
  </MVector>
</Coord>
```

Или в plain формате (fallback):
```
"4.7 0.67 0.0"
```

#### 2. Координаты сцены (Scene Coordinates)

**Определение**: Координаты в системе координат `QGraphicsScene`, используемые для отображения компонентов.

**Характеристики**:
- Единицы измерения: пиксели
- Начало координат: (0, 0) в верхнем левом углу сцены
- Диапазон: любые значения (могут быть отрицательными)
- Масштаб: `m_coordScale = 30.0` (синхронизирован с `UDrawEngine::ZoomCoeff`)

**Формула преобразования из ядра в сцену**:
```
sceneX = kernelX * m_coordScale
sceneY = kernelY * m_coordScale
```

**Реализация**:
```cpp
QPointF scenePosFromKernel(const QPointF& kernel) const
{
    return kernel * m_coordScale;  // m_coordScale = 30.0
}
```

**Формула преобразования из сцены в ядро**:
```
kernelX = sceneX / m_coordScale
kernelY = sceneY / m_coordScale
```

**Реализация**:
```cpp
QPointF kernelPosFromScene(const QPointF& scene) const
{
    return scene / m_coordScale;  // m_coordScale = 30.0
}
```

#### 3. Нормализованные координаты сцены (Normalized Scene Coordinates)

**Определение**: Координаты сцены, сдвинутые так, чтобы самый левый верхний компонент находился в позиции (0, 0) для удобства визуализации.

**Характеристики**:
- Единицы измерения: пиксели
- Начало координат: (0, 0) соответствует позиции самого левого верхнего компонента
- Использование: только для визуального отображения, не сохраняется в ядре
- Смещение нормализации: `m_normalizationOffset` (пересчитывается при каждой загрузке сцены)

**Вычисление смещения нормализации**:

1. При загрузке сцены (`buildScene()`) находятся минимальные координаты ядра среди всех компонентов:
```cpp
QPointF minKernel(0, 0);
for (каждый компонент) {
    QPointF kernelPos = loadCoord(component);
    if (kernelPos.x() < minKernel.x()) minKernel.setX(kernelPos.x());
    if (kernelPos.y() < minKernel.y()) minKernel.setY(kernelPos.y());
}
```

2. Минимальные координаты ядра преобразуются в координаты сцены:
```cpp
QPointF minScenePos = scenePosFromKernel(minKernel);
// minScenePos = minKernel * 30.0
```

3. Смещение нормализации сохраняется:
```cpp
m_normalizationOffset = minScenePos;
```

**Формула нормализации (при загрузке)**:
```
normalizedScenePos = absoluteScenePos - m_normalizationOffset
```

**Реализация при загрузке**:
```cpp
QPointF absoluteScenePos = scenePosFromKernel(kernelPos);
QPointF normalizedScenePos = absoluteScenePos - minScenePos;
node->setPos(normalizedScenePos);  // Узел позиционируется в нормализованных координатах
```

**Формула денормализации (при сохранении)**:
```
absoluteScenePos = normalizedScenePos + m_normalizationOffset
```

**Реализация при сохранении**:
```cpp
QPointF normalizedPos = node->scenePos();  // Позиция узла в нормализованных координатах
QPointF absoluteScenePos = normalizedPos + m_normalizationOffset;
saveCoord(fullName, absoluteScenePos);  // Сохраняем абсолютные координаты
```

#### Процесс загрузки координат

**Метод**: `loadCoord(const QString& fullName, QPointF& outPos)`

**Алгоритм**:
1. Чтение параметра `Coord` из ядра через `Model_GetComponentParameterValue()`
2. Парсинг координат:
   - Попытка парсинга plain формата `"x y z"` (fallback)
   - Если не удалось, парсинг XML формата через `USerStorageXML`
3. Возврат координат ядра (не преобразованных в сцену)

**Пример логирования**:
```
[ModernDiagram] load coord (plain) PNeuronS1D1Syn1.Dendrite1_1 kernel=(4.700000,0.670000)
```

#### Процесс сохранения координат

**Метод**: `saveCoord(const QString& fullName, const QPointF& scenePos)`

**Алгоритм**:
1. Преобразование координат сцены в координаты ядра:
   ```cpp
   QPointF kernelPos = kernelPosFromScene(scenePos);
   ```
2. Нормализация: гарантирование неотрицательных значений:
   ```cpp
   if (kernelPos.x() < 0) kernelPos.setX(0);
   if (kernelPos.y() < 0) kernelPos.setY(0);
   ```
3. Сериализация в XML формат:
   ```cpp
   RDK::USerStorageXML xml;
   xml.Create("Coord");
   RDK::MVector<double,3> posVec;
   posVec[0] = kernelPos.x();
   posVec[1] = kernelPos.y();
   posVec[2] = 0.0;
   xml << posVec;
   ```
4. Сохранение в ядро через `Model_SetComponentParameterValue()`

**Пример логирования**:
```
[ModernDiagram] save coord PNeuronS1D1Syn1.Dendrite1_1 kernel=(4.700000,0.670000)
```

#### Процесс перемещения компонента

**Событие**: `NodeItem::itemChange(ItemPositionHasChanged, ...)`

**Алгоритм**:
1. Получение нормализованной позиции узла:
   ```cpp
   QPointF normalizedPos = scenePos();  // Позиция в нормализованных координатах
   ```
2. Денормализация для получения абсолютных координат сцены:
   ```cpp
   QPointF absoluteScenePos = normalizedPos + m_normalizationOffset;
   ```
3. Сохранение абсолютных координат в ядро:
   ```cpp
   saveCoord(fullName, absoluteScenePos);
   ```

**Пример логирования**:
```
[ModernDiagram] item move PNeuronS1D1Syn1.Dendrite1_1 
  scenePos=(141.000000,20.100000) 
  offset=(0.000000,0.000000) 
  absoluteScene=(141.000000,20.100000)
```

#### Процесс добавления нового компонента

**Событие**: `ModernGraphicsView::dropEvent()`

**Алгоритм**:
1. Получение позиции drop в координатах сцены:
   ```cpp
   QPointF scenePos = mapToScene(event->pos());
   ```
2. Денормализация с учетом текущего смещения:
   ```cpp
   QPointF absoluteScenePos = scenePos + m_normalizationOffset;
   ```
3. Сохранение координат нового компонента:
   ```cpp
   saveCoord(fullName, absoluteScenePos);
   ```
4. Перезагрузка сцены для обновления всех компонентов

#### Важные особенности

1. **Абсолютность координат ядра**: Координаты в ядре всегда абсолютные и не зависят от уровня вложенности компонента. Это обеспечивает стабильность позиций при навигации между уровнями.

2. **Визуальная нормализация**: Нормализация применяется только для визуального отображения, чтобы самый левый верхний компонент всегда был в позиции (0, 0) на экране. Это не влияет на координаты, хранящиеся в ядре.

3. **Пересчет смещения**: `m_normalizationOffset` пересчитывается при каждой загрузке сцены (`buildScene()`) на основе минимальных координат всех видимых компонентов. Это позволяет корректно отображать компоненты при входе/выходе из вложенных компонентов.

4. **Синхронизация масштаба**: `m_coordScale = 30.0` синхронизирован с `UDrawEngine::ZoomCoeff`, что обеспечивает приблизительно 1:1 соответствие расстояний между компонентами в старом и новом виджетах.

5. **Совместимость форматов**: Поддержка как XML, так и plain формата координат обеспечивает совместимость с различными версиями ядра.

#### Диаграмма преобразований

```
┌─────────────────┐
│ Kernel Coords   │  (абсолютные, логические единицы)
│ (4.7, 0.67)     │
└────────┬────────┘
         │ * m_coordScale (30.0)
         ▼
┌─────────────────┐
│ Scene Coords    │  (абсолютные, пиксели)
│ (141.0, 20.1)   │
└────────┬────────┘
         │ - m_normalizationOffset
         ▼
┌─────────────────┐
│ Normalized      │  (относительные, пиксели)
│ Scene Coords    │  (для отображения)
│ (141.0, 20.1)   │
└─────────────────┘
```

**Обратное преобразование (при сохранении)**:
```
Normalized Scene Coords (141.0, 20.1)
  + m_normalizationOffset (0.0, 0.0)
  = Absolute Scene Coords (141.0, 20.1)
  / m_coordScale (30.0)
  = Kernel Coords (4.7, 0.67)
```

### Отображение связей

- **Чтение связей**: метод `buildLinks()`
  - Получает список связей через `Model_GetComponentInternalLinks()`
  - Парсит XML формат `UStringLinksList`
  - Резолвит имена компонентов (поддерживает вложенные компоненты)
  - Создает `LinkItem` для каждой связи

- **Резолв узлов**: функция `resolveNode()`
  - Сначала ищет точное совпадение имени
  - Затем пытается найти по `Id` (убирая вложенность после первой точки)
  - Поддерживает префикс модели для вложенных компонентов

- **Визуализация связей**:
  - Связи отображаются как кривые Безье между портами узлов
  - Цвет: синий (#5078C8), толщина: 2 пикселя
  - Связи автоматически обновляются при перемещении узлов

## Интеграция с системой

### Сигналы

Виджет испускает следующие сигналы для взаимодействия с другими компонентами:

- `componentSelected(QString name)` - компонент выбран (одиночный клик)
- `componentDoubleClicked(QString name)` - двойной клик по компоненту
- `componentStapBack()` - выход на уровень выше
- `updateComponentsList()` - обновление списка компонентов
- `viewLinks(QString componentName)` - просмотр/разрыв связи
- `createLinks(QString firstComponentName, QString secondComponentName)` - создание связи
- `switchLinks(QString firstComponentName, QString secondComponentName)` - переключение связи

### Слоты

Виджет предоставляет следующие слоты для обработки внешних событий:

- `componentDoubleClick(QString name)` - обработка двойного клика из списка компонентов
- `componentSingleClick(QString name)` - обработка одиночного клика из списка компонентов
- `updateScheme(bool reloadXml)` - обновление схемы
- `selectComponent(QString name)` - программный выбор компонента
- `Reload()` - перезагрузка диаграммы
- `FitToView()` - установка масштаба по содержимому

### Подключение в UDrawEngineWidget

Виджет интегрирован в `UDrawEngineWidget` через вкладки:

```cpp
// Создание современной диаграммы
modernScheme = new UModernDiagramWidget(ui->modernContainer);
modernScheme->SetApplication(app);
modernScheme->SetComponentName("");

// Подключение сигналов
connect(modernScheme, SIGNAL(componentSelected(QString)), 
        this, SIGNAL(componentSelectedFromScheme(QString)));
connect(modernScheme, SIGNAL(componentDoubleClicked(QString)), 
        this, SIGNAL(componentDoubleClickFromScheme(QString)));
connect(modernScheme, SIGNAL(componentStapBack()), 
        this, SIGNAL(componentStapBackFromScheme()));
connect(modernScheme, SIGNAL(updateComponentsList()), 
        this, SIGNAL(updateComponentsListFromScheme()));
connect(modernScheme, SIGNAL(viewLinks(QString)), 
        this, SIGNAL(viewLinksFromScheme(QString)));
connect(modernScheme, SIGNAL(createLinks(QString,QString)), 
        this, SIGNAL(createLinksFromScheme(QString,QString)));
connect(modernScheme, SIGNAL(switchLinks(QString,QString)), 
        this, SIGNAL(switchLinksFromScheme(QString,QString)));
```

## Технические детали

### Зависимости

- Qt5/Qt6: `QGraphicsView`, `QGraphicsScene`, `QGraphicsItem`, `QMenu`, `QAction`
- RDK Core: `UApplication`, `UNet`, `UStorage`, `UEngine`
- RDK Graphics: `UClassDescriptionDisplay`
- RDK GUI: `UQuickLinkDialog`

### Файлы

- `Rdk/GUI/Qt/UModernDiagramWidget.h` - заголовочный файл
- `Rdk/GUI/Qt/UModernDiagramWidget.cpp` - реализация
- Интеграция в `Rdk/GUI/Qt/UDrawEngineWidget.h/.cpp`

### Логирование

Виджет использует `MLog_LogMessageEx()` для отладочного логирования:
- Чтение координат: `[ModernDiagram] load coord (plain) <name> kernel=(x,y)`
- Сохранение координат: `[ModernDiagram] save coord <name> kernel=(x,y)`
- Чтение связей: `[ModernDiagram] links xml bytes=...`, `[ModernDiagram] links parsed count=...`
- Создание связей: `[ModernDiagram] link add <src> -> <dst>`

## Отличия от классического виджета

1. **Архитектура**: Использует `QGraphicsView`/`QGraphicsScene` вместо кастомной отрисовки
2. **Интерактивность**: Поддержка drag & drop для создания связей, rubber-band выделения
3. **Масштабирование**: Плавное масштабирование колесом мыши
4. **Визуализация**: Современный дизайн с закругленными углами и цветовым кодированием
5. **Производительность**: Использует аппаратное ускорение Qt для отрисовки

## Известные ограничения

1. Миникарта скрыта (может быть включена в будущем)
2. Некоторые действия контекстного меню требуют дополнительной реализации (например, GUI компонента)
3. Сигналы `viewLinks`, `createLinks`, `switchLinks` требуют обработки в `UGEngineControlWidget`

## Будущие улучшения

1. Включение миникарты при необходимости
2. Поддержка групповых операций (копирование, вставка)
3. Улучшенная визуализация портов с именами
4. Поддержка редактирования связей через контекстное меню
5. Экспорт диаграммы в изображение

