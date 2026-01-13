# Rdk-CvBasicLib - Библиотека компьютерного зрения

## Назначение

**Rdk-CvBasicLib** предоставляет компоненты компьютерного зрения на базе OpenCV. Библиотека включает компоненты для захвата видео, обработки изображений, детекции объектов, классификации и сегментации.

## Структура библиотеки

### Основной класс

- **CvBasicLib** (CvBasicLibrary) - главный класс библиотеки, наследник `ULibrary`

## Категории компонентов

### 1. Захват видео и изображений

#### TCapture
Базовый класс для захвата видео и изображений.

#### TCaptureCamera
Захват с камеры (веб-камера, USB-камера).

#### TCaptureCameraIp
Захват с IP-камеры по сети.

#### TCaptureImageSequence
Захват последовательности изображений из файлов.

#### TCaptureSupport
Вспомогательные функции для захвата.

### 2. Источники изображений

#### UBASource
Базовый источник изображений.

#### UBASourceFile
Источник изображений из файла.

#### UBASourceMultiFile
Источник из множества файлов.

#### UBABitmapSource
Источник из растровых изображений (UBitmap).

### 3. Обработка изображений (UBA* компоненты)

#### UBAColorConvert
Конвертация цветовых пространств (RGB, HSV, Grayscale и др.).

#### UBAResize
Изменение размера изображения.

#### UBARotate
Поворот изображения.

#### UBAFlipImage
Отражение изображения (горизонтальное/вертикальное).

#### UBACrop
Обрезка изображения.

#### UBAReduce
Уменьшение размерности изображения.

#### UBADifferenceFrame
Вычисление разности кадров.

#### UBABackground
Работа с фоновым изображением.

#### UBABinarization
Бинаризация изображения.

#### UBALooping
Циклическое воспроизведение изображений.

#### UBALabeling
Маркировка объектов на изображении.

#### UBAMovingDetector
Детектор движения.

#### UBAObjectDetector
Детектор объектов (базовый).

#### UBAShowObjects
Отображение объектов на изображении.

#### UBAGuiSelection
Графический выбор области на изображении.

#### UBShowRect
Отображение прямоугольников.

### 4. Симуляторы данных

#### UBAVideoSimulator
Симулятор видео.

#### UBADataSimulator
Симулятор данных.

#### UBARotCameraSimulator
Симулятор вращающейся камеры.

### 5. Математические операции

#### UBMathOperator
Математические операции над изображениями.

#### UMatrixMath
Математические операции с матрицами.

#### UMDMatrixMux
Мультиплексор матриц.

### 6. Классификаторы (UCR* компоненты)

#### UCRClassifier
Базовый классификатор.

#### UCRPerseptron
Перцептрон для классификации.

#### UCRDirectCompare
Прямое сравнение для классификации.

#### UCRDistance
Классификация по расстоянию.

#### UCRFusion
Слияние результатов классификации.

#### UCRSample
Образец для обучения.

#### UCRTeacher
Учитель (обучение классификаторов).

#### UCRTeacherPerseptronBP
Обучение перцептрона методом обратного распространения.

#### UCRTeacherPerseptronDL
Обучение перцептрона с глубоким обучением.

#### UCRTeacherCVNetworkBP
Обучение сверточной сети методом обратного распространения.

#### UCRConvolutionNetwork
Сверточная нейронная сеть.

#### UCRPrincipalComponentAnalysis
Анализ главных компонент (PCA).

#### UCRBarnesHutTSNE
t-SNE визуализация (Barnes-Hut алгоритм).

#### UClassifierBase
Базовый класс классификатора.

#### UClassifierResSaver
Сохранение результатов классификации.

### 7. Детекторы

#### UDetectorBase
Базовый класс детектора объектов.

#### UDetResSaverPVOC
Сохранение результатов детекции в формате PASCAL VOC.

### 8. Сегментация

#### USegmentatorBase
Базовый класс сегментатора.

### 9. Статистика

#### UBStatistic
Статистика по изображениям.

### 10. Конвейеры обработки

#### UBPipeline
Конвейер обработки изображений.

### 11. Модели

#### UBAModel
Модель для обработки изображений.

### 12. Специальные алгоритмы

#### PCA/
Подкаталог с реализацией PCA (Principal Component Analysis).

#### TSNE/
Подкаталог с реализацией t-SNE (t-distributed Stochastic Neighbor Embedding):
- `sptree.cpp/h` - пространственное дерево
- `tsne.cpp/h` - основной алгоритм t-SNE
- `vptree.h` - VP-дерево

#### UCVNetwork/
Подкаталог с реализацией сверточной нейронной сети:
- `CNetwork.cpp/h` - сеть
- `CNeuron.cpp/h` - нейрон
- `CNField.cpp/h` - поле нейронов
- `CNLayer.cpp/h` - слой сети

## Ключевые классы

### CvBasicLib

Главный класс библиотеки:

```cpp
class CvBasicLib : public ULibrary
{
public:
    CvBasicLib(void);
    virtual void CreateClassSamples(UStorage *storage);
    
    // Функция для создания свойств из мок-сетей
    static bool CvBasicLibCrPropMock(RDK::USerStorageXML* serstorage, 
                                     RDK::UMockUNet* mock_unet);
};
```

### TCapture

Базовый класс для захвата видео/изображений. Наследники реализуют конкретные источники:
- Камеры (USB, IP)
- Файлы
- Последовательности изображений

### UBA* компоненты

Компоненты обработки изображений с префиксом UBA (UBitmap Algorithm):
- Обработка пикселей
- Геометрические преобразования
- Фильтрация
- Детекция объектов

### UCR* компоненты

Компоненты классификации и распознавания с префиксом UCR:
- Классификаторы
- Обучение
- Нейронные сети

## Использование

Библиотека автоматически загружается при инициализации:

```cpp
libs_list.push_back(&RDK::CvBasicLibrary);
```

## Зависимости

- **rdk.static.qt** - ядро Rdk (обязательно)
- **OpenCV** - библиотека компьютерного зрения (обязательно)
- Стандартная библиотека C++

## Зависимости от этой библиотеки

- **Nmsdk-MotionControlLib** - использует компоненты компьютерного зрения для систем управления движением

## Примеры использования

### Захват с камеры

```cpp
// Создание компонента захвата с камеры
TCaptureCamera* capture = storage->CreateComponent<TCaptureCamera>();
// Настройка индекса камеры и параметров
```

### Обработка изображения

```cpp
// Создание конвейера обработки
UBPipeline* pipeline = storage->CreateComponent<UBPipeline>();
// Добавление этапов обработки: resize, color convert, binarization
```

### Классификация

```cpp
// Создание классификатора
UCRClassifier* classifier = storage->CreateComponent<UCRClassifier>();
// Обучение и классификация
```

## См. также

- [02-Libraries-Overview.md](02-Libraries-Overview.md) - обзор всех библиотек
- [07-Nmsdk-MotionControlLib.md](07-Nmsdk-MotionControlLib.md) - библиотека управления движением (использует CvBasicLib)

