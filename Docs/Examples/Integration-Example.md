# Пример: Интеграция с внешними библиотеками

## RU

### Описание задачи

Интегрировать компоненты из разных библиотек Nmsdk для создания комплексного решения.

### Решение

#### Пример: Компьютерное зрение + Импульсные нейронные сети

```cpp
#include <rdk.h>
using namespace RDK;

void VisionSpikingIntegration() {
    UStorage storage;
    // ... загрузка библиотек ...
    
    // Захват видео (Rdk-CvBasicLib)
    auto capture = storage.CreateComponent<UCapture>("Capture");
    capture->DeviceIndex = 0;
    capture->Default();
    capture->Build();
    
    // Обработка изображения (Rdk-CvBasicLib)
    auto filter = storage.CreateComponent<UImageFilter>("Filter");
    filter->InputImage.AttachTo(&capture->OutputImage);
    filter->FilterType = "Gaussian";
    filter->Default();
    filter->Build();
    
    // Конвертация в данные для нейронной сети (Rdk-BasicLib)
    auto converter = storage.CreateComponent<UIOConverter>("Converter");
    converter->Input.AttachTo(&filter->OutputImage);
    converter->Default();
    converter->Build();
    
    // Импульсная нейронная сеть (Nmsdk-PulseLib)
    auto generator = storage.CreateComponent<NPulseGenerator>("Generator");
    generator->Frequency = 10.0;
    generator->Default();
    generator->Build();
    
    auto neuron = storage.CreateComponent<NPulseNeuron>("Neuron");
    neuron->InputPulses.AttachTo(&generator->Output);
    neuron->Default();
    neuron->Build();
    
    // Выполнение
    for (int i = 0; i < 1000; i++) {
        capture->Calculate();
        filter->Calculate();
        converter->Calculate();
        generator->Calculate();
        neuron->Calculate();
    }
}
```

### Связанная документация

- [Libraries/Overview.md](../Libraries/Overview.md) - обзор библиотек
- [Nmsdk-PulseLib/Docs/Usage-Examples.md](../../Libraries/Nmsdk-PulseLib/Docs/Usage-Examples.md) - примеры импульсных сетей
- [Rdk-CvBasicLib/Docs/Usage-Examples.md](../../Libraries/Rdk-CvBasicLib/Docs/Usage-Examples.md) - примеры компьютерного зрения

---

## EN

### Task Description

Integrate components from different Nmsdk libraries to create a comprehensive solution.

### Solution

#### Example: Computer Vision + Spiking Neural Networks

```cpp
#include <rdk.h>
using namespace RDK;

void VisionSpikingIntegration() {
    UStorage storage;
    // ... load libraries ...
    
    // Video capture (Rdk-CvBasicLib)
    auto capture = storage.CreateComponent<UCapture>("Capture");
    capture->DeviceIndex = 0;
    capture->Default();
    capture->Build();
    
    // Image processing (Rdk-CvBasicLib)
    auto filter = storage.CreateComponent<UImageFilter>("Filter");
    filter->InputImage.AttachTo(&capture->OutputImage);
    filter->FilterType = "Gaussian";
    filter->Default();
    filter->Build();
    
    // Convert to neural network data (Rdk-BasicLib)
    auto converter = storage.CreateComponent<UIOConverter>("Converter");
    converter->Input.AttachTo(&filter->OutputImage);
    converter->Default();
    converter->Build();
    
    // Spiking neural network (Nmsdk-PulseLib)
    auto generator = storage.CreateComponent<NPulseGenerator>("Generator");
    generator->Frequency = 10.0;
    generator->Default();
    generator->Build();
    
    auto neuron = storage.CreateComponent<NPulseNeuron>("Neuron");
    neuron->InputPulses.AttachTo(&generator->Output);
    neuron->Default();
    neuron->Build();
    
    // Execute
    for (int i = 0; i < 1000; i++) {
        capture->Calculate();
        filter->Calculate();
        converter->Calculate();
        generator->Calculate();
        neuron->Calculate();
    }
}
```

### Related Documentation

- [Libraries/Overview.md](../Libraries/Overview.md) - libraries overview
- [Nmsdk-PulseLib/Docs/Usage-Examples.md](../../Libraries/Nmsdk-PulseLib/Docs/Usage-Examples.md) - spiking network examples
- [Rdk-CvBasicLib/Docs/Usage-Examples.md](../../Libraries/Rdk-CvBasicLib/Docs/Usage-Examples.md) - computer vision examples
