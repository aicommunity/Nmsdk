# Библиотеки машинного обучения

## Обзор

Проект Nmsdk включает три библиотеки для интеграции с внешними системами машинного обучения:
- **Rdk-PyMachineLearningLib** - интеграция с Python ML библиотеками
- **Rdk-TensorflowLib** - интеграция с TensorFlow
- **Rdk-DarknetLib** - интеграция с Darknet

Эти библиотеки являются опциональными и требуют наличия соответствующих внешних зависимостей.

## Rdk-PyMachineLearningLib

### Назначение

Интеграция с Python библиотеками машинного обучения через Python C API. Позволяет использовать популярные Python ML библиотеки (TensorFlow, PyTorch, scikit-learn, YOLO и др.) из C++ кода.

### Основной класс

- **PyMachineLearningLib** - главный класс библиотеки

### Компоненты

#### Базовые компоненты

##### TPyComponent
Базовый компонент для всех Python-интегрированных компонентов. Предоставляет общую функциональность для работы с Python.

##### TPythonIntegration
Интеграция с Python - основной класс для управления Python интерпретатором и выполнения Python кода.

##### TPythonIntegrationUtil
Утилиты для работы с Python интеграцией.

##### TPythonIntegrationInclude
Вспомогательные заголовки для интеграции.

#### Классификаторы

##### TPyClassifierTrainer
Тренер классификаторов через Python. Обучение классификаторов с использованием Python ML библиотек.

##### TPyUBitmapClassifier
Классификатор растровых изображений через Python.

##### TPyAggregateClassifier
Агрегированный классификатор (ансамбль классификаторов).

#### Детекторы объектов

##### TPyObjectDetector
Детектор объектов через Python.

##### TPyObjectDetectorYolo
Детектор объектов YOLO через Python.

##### TPyObjectDetectorYoloEx
Расширенный детектор YOLO.

##### TPyObjectDetectorSqueezeDet
Детектор SqueezeDet через Python.

##### TPyDetPredict
Предсказание детекции через Python.

##### TPyDetectorTrainer
Тренер детекторов через Python.

#### Сегментаторы

##### TPySegmentator
Сегментатор через Python.

##### TPySegmentatorUNet
Сегментатор U-Net через Python.

##### TPySegmentatorProtobuf
Сегментатор с использованием Protobuf.

##### TPySegmenterTrainer
Тренер сегментаторов через Python.

#### Базовые классы

##### TPyBaseTrainer
Базовый класс тренера через Python.

#### Сортировка предсказаний

##### TPyPredictSort
Сортировка предсказаний.

#### Конвертеры

##### pyboost_cv3_converter / pyboostcvconverter
Конвертеры между OpenCV и Python (используя Boost.Python).

### Использование

Библиотека загружается условно:

```cpp
#ifdef RDK_USE_PYTHON
libs_list.push_back(&RDK::PyMachineLearningLib);
#endif
```

### Зависимости

- **rdk.static.qt** - ядро Rdk
- **Python** (C API) - интерпретатор Python
- **NumPy** - для работы с массивами
- **OpenCV** - для работы с изображениями (через конвертеры)
- **Boost.Python** (опционально) - для конвертеров

### Особенности

- Использует Python C API для вызова Python кода из C++
- Поддерживает передачу данных между C++ и Python
- Конвертеры для OpenCV изображений
- Поддержка различных Python ML библиотек

## Rdk-TensorflowLib

### Назначение

Прямая интеграция с TensorFlow C API для использования моделей TensorFlow в проекте.

### Основной класс

- **TensorflowLib** - главный класс библиотеки

### Компоненты

#### Базовые компоненты

##### UTfComponent
Базовый компонент для всех TensorFlow компонентов.

#### Классификаторы

##### UTfClassifier
Классификатор на основе TensorFlow моделей.

#### Детекторы

##### UTfDetector
Детектор объектов на основе TensorFlow.

##### UTfSqDetector
Детектор SqueezeDet на основе TensorFlow.

#### Сессии TensorFlow

##### ttfsession
Сессия TensorFlow для выполнения графов вычислений.

##### ttfsessionSqDet
Сессия для SqueezeDet моделей.

#### Интерфейсы

##### Interface/label_image.h
Интерфейс для классификации изображений.

### Использование

Библиотека загружается условно:

```cpp
#ifdef RDK_USE_TENSORFLOW
libs_list.push_back(&RDK::TensorflowLib);
#endif
```

### Зависимости

- **rdk.static.qt** - ядро Rdk
- **TensorFlow** (C API) - библиотека TensorFlow
- Заголовочные файлы TensorFlow

### Особенности

- Прямая интеграция с TensorFlow C API
- Загрузка и выполнение предобученных моделей
- Работа с сессиями TensorFlow
- Поддержка различных архитектур (включая SqueezeDet)

## Rdk-DarknetLib

### Назначение

Интеграция с Darknet - фреймворком для детекции объектов, используемым в YOLO (You Only Look Once).

### Основной класс

- **DarknetLib** - главный класс библиотеки

### Компоненты

#### Детекторы объектов

##### TDarknetObjectDetector
Детектор объектов на основе Darknet/YOLO.

**Основные функции:**
- Загрузка моделей YOLO
- Детекция объектов на изображениях
- Возврат координат и классов объектов

#### Классификаторы

##### TDarknetUBitmapClassifier
Классификатор растровых изображений на основе Darknet.

### Использование

Библиотека загружается при наличии Darknet (условная компиляция).

### Зависимости

- **rdk.static.qt** - ядро Rdk
- **Darknet** - библиотека Darknet
- Заголовочные файлы Darknet

### Особенности

- Интеграция с Darknet для детекции объектов
- Поддержка моделей YOLO
- Работа с изображениями через UBitmap

## Сравнение библиотек

| Библиотека | Тип интеграции | Гибкость | Производительность | Сложность |
|------------|----------------|----------|---------------------|-----------|
| PyMachineLearningLib | Python C API | Высокая (любые Python библиотеки) | Средняя (overhead Python) | Средняя |
| TensorflowLib | TensorFlow C API | Средняя (только TensorFlow) | Высокая | Низкая |
| DarknetLib | Darknet API | Низкая (только Darknet) | Высокая | Низкая |

## Рекомендации по использованию

### Когда использовать PyMachineLearningLib

- Нужен доступ к широкому спектру Python ML библиотек
- Требуется быстрая интеграция существующих Python моделей
- Гибкость важнее производительности

### Когда использовать TensorflowLib

- Работа с TensorFlow моделями
- Требуется высокая производительность
- Не нужны другие Python библиотеки

### Когда использовать DarknetLib

- Детекция объектов с YOLO
- Простая интеграция Darknet моделей
- Высокая производительность детекции

## Примеры использования

### Python классификатор

```cpp
#ifdef RDK_USE_PYTHON
// Создание Python классификатора
TPyUBitmapClassifier* classifier = storage->CreateComponent<TPyUBitmapClassifier>();
// Настройка пути к Python скрипту и модели
// Классификация изображений
#endif
```

### TensorFlow детектор

```cpp
#ifdef RDK_USE_TENSORFLOW
// Создание TensorFlow детектора
UTfDetector* detector = storage->CreateComponent<UTfDetector>();
// Загрузка модели TensorFlow
// Детекция объектов
#endif
```

### Darknet детектор

```cpp
// Создание Darknet детектора
TDarknetObjectDetector* detector = storage->CreateComponent<TDarknetObjectDetector>();
// Загрузка YOLO модели
// Детекция объектов
```

## См. также

- [02-Libraries-Overview.md](02-Libraries-Overview.md) - обзор всех библиотек
- [04-Rdk-CvBasicLib.md](04-Rdk-CvBasicLib.md) - библиотека компьютерного зрения (может использоваться совместно)

