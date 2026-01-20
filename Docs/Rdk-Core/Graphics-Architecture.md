# Архитектура графики (Graphics Architecture)

## RU

### Обзор

Модуль `Rdk/Core/Graphics` предоставляет систему графики для визуализации компонентов и данных.

### Основные компоненты

#### UGraphics

Основной класс графики, предоставляющий абстрактный интерфейс для работы с графикой.

#### UAGraphics

Абстрактная графика - базовый класс для графических операций.

#### UDrawEngine

Движок отрисовки для визуализации компонентов и их соединений.

**Основные функции:**
- Отрисовка компонентов
- Отрисовка соединений между компонентами
- Управление координатами и масштабированием

#### UBitmap

Растровое изображение для работы с пиксельными данными.

**Основные функции:**
- Загрузка/сохранение изображений
- Обработка пиксельных данных
- Конвертация форматов

#### UBitmapVector

Вектор растровых изображений для работы с последовательностями изображений.

#### UFont

Работа со шрифтами для текстовой визуализации.

### Сериализация графики

#### UGraphicsXMLSerialize

XML сериализация графических данных.

#### UGraphicsBinarySerialize

Бинарная сериализация графических данных для эффективного хранения.

#### UGraphicsIO

Ввод-вывод графических данных.

### Интеграция с GUI

Графическая система интегрируется с GUI через виджеты:

- `UModernDiagramWidget` - виджет для визуализации диаграмм компонентов
- `UDrawEngineImageWidget` - виджет для отображения изображений

### См. также

- [GUI Overview](../GUI/Overview.md)
- [Style System](../GUI/Style-System.md)
- [Rdk Core Overview](Overview.md)

---

## EN

### Overview

The `Rdk/Core/Graphics` module provides a graphics system for visualizing components and data.

### Main Components

#### UGraphics

Main graphics class providing abstract interface for graphics operations.

#### UAGraphics

Abstract graphics - base class for graphics operations.

#### UDrawEngine

Drawing engine for visualizing components and their connections.

#### UBitmap

Bitmap image for working with pixel data.

#### UBitmapVector

Vector of bitmap images for working with image sequences.

#### UFont

Font handling for text visualization.

### Graphics Serialization

#### UGraphicsXMLSerialize

XML serialization of graphics data.

#### UGraphicsBinarySerialize

Binary serialization of graphics data for efficient storage.

#### UGraphicsIO

Graphics data input/output.

### GUI Integration

The graphics system integrates with GUI through widgets.

### See Also

- [GUI Overview](../GUI/Overview.md)
- [Style System](../GUI/Style-System.md)
- [Rdk Core Overview](Overview.md)
