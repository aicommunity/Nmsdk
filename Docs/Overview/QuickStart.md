# Быстрый старт (Quick Start)

## RU

### Установка зависимостей

#### Linux (Ubuntu/Debian 22.04+)

На Linux проект использует **Qt6** (системные пакеты). Рекомендуемый набор зависимостей:

```bash
sudo apt update
sudo apt install -y \
  build-essential cmake git g++ \
  qt6-base-dev qt6-tools-dev qt6-serialport-dev qt6-svg-dev qt6-charts-dev \
  libboost-all-dev libcurl4-openssl-dev \
  libcups2-dev libgtest-dev
```

- `qt6-charts-dev` — графики Watch/NeuroModeler (Qt Charts)
- `qt6-svg-dev` — GUI-диаграммы в HardwareLib
- `libcups2-dev` — печать через Qt PrintSupport
- `libgtest-dev` — системный Google Test (без скачивания через FetchContent при configure)

#### Windows

- Установите Visual Studio 2019 или новее
- Установите CMake 3.16+
- Qt5 (VS2019) или Qt6/vcpkg (VS2022) — см. пресеты в `CMakePresets.json`

### Сборка проекта

```bash
# Вариант 1: CMake preset (рекомендуется, Qt Creator / CLI)
cmake --preset linux-gcc-debug-local
cmake --build --preset linux-gcc-debug

# Вариант 2: классическая out-of-source сборка
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build . -j$(nproc)
```

### Создание первого проекта

1. **Запустите NeuroModeler:**
   ```bash
   ./Bin/Platform/Linux/NeuroModeler
   ```

2. **Создайте новый проект:**
   - File → New Project

3. **Добавьте компонент:**
   - Перетащите компонент из библиотеки в редактор диаграмм
   - Настройте параметры компонента

4. **Соедините компоненты:**
   - Соедините выходы одних компонентов с входами других

5. **Запустите выполнение:**
   - Нажмите кнопку "Start" в панели управления

### Пример: Простая сеть компонентов

```mermaid
flowchart LR
    Source["Источник данных<br/>UMatrixSource"] --> Process["Обработка<br/>UStatistic"]
    Process --> Output["Выход<br/>UIO"]
```

**Пример создания компонента программно:**

```cpp
#include <rdk.h>
using namespace RDK;

// Создание хранилища и движка
UStorage storage;
UEngine engine;
engine.SetStorage(&storage);

// Загрузка библиотек
std::list<ULibrary*> libs;
RdkLoadPredefinedLibraries(libs);
for(auto lib : libs) {
    storage.AddCollection(lib);
}
storage.BuildStorage();

// Создание компонента
auto source = storage.CreateComponent<UMatrixSource>("Source");
source->FileName = "data.csv";
source->Build();

auto processor = storage.CreateComponent<UStatistic>("Processor");
processor->Build();

// Соединение компонентов
processor->InputData.AttachTo(&source->OutputMatrix);

// Выполнение
engine.GetEnvironment()->Start();
for(int i = 0; i < 10; i++) {
    source->Calculate();
    processor->Calculate();
}
```

**Пример конфигурационного файла проекта (XML):**

```xml
<Project>
  <Name>MyFirstProject</Name>
  <Components>
    <Component Name="Source" Class="UMatrixSource">
      <Properties>
        <Property Name="FileName" Type="string">data.csv</Property>
      </Properties>
    </Component>
    <Component Name="Processor" Class="UStatistic">
      <Properties>
        <Property Name="InputData" Type="link">Source.OutputMatrix</Property>
      </Properties>
    </Component>
  </Components>
</Project>
```

### Следующие шаги

- [Компонентная система](../../Rdk/Docs/Guides/Component-System.md) - детальное описание работы с компонентами
- [Обзор библиотек](../Libraries/Overview.md) - доступные библиотеки компонентов
- [GUI Overview](../GUI/Overview.md) - описание интерфейса

---

## EN

### Installation dependencies

#### Linux (Ubuntu/Debian 22.04+)

The project uses **Qt6** system packages on Linux. Recommended dependencies:

```bash
sudo apt update
sudo apt install -y \
  build-essential cmake git g++ \
  qt6-base-dev qt6-tools-dev qt6-serialport-dev qt6-svg-dev qt6-charts-dev \
  libboost-all-dev libcurl4-openssl-dev \
  libcups2-dev libgtest-dev
```

- `qt6-charts-dev` — Watch charts in NeuroModeler (Qt Charts)
- `qt6-svg-dev` — HardwareLib GUI diagrams
- `libcups2-dev` — Qt PrintSupport (printing)
- `libgtest-dev` — system Google Test (avoids FetchContent download at configure time)

#### Windows

- Install Visual Studio 2019 or newer
- Install CMake 3.16+
- Qt5 (VS2019) or Qt6/vcpkg (VS2022) — see presets in `CMakePresets.json`

### Build project

```bash
# Option 1: CMake preset (recommended, Qt Creator / CLI)
cmake --preset linux-gcc-debug-local
cmake --build --preset linux-gcc-debug

# Option 2: classic out-of-source build
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build . -j$(nproc)
```

### Create first project

1. **Run NeuroModeler:**
   ```bash
   ./Bin/Platform/Linux/NeuroModeler
   ```

2. **Create new project:**
   - File → New Project

3. **Add component:**
   - Drag component из library в editor diagrams
   - Configure parameters component

4. **Connect components:**
   - Connect outputs some components с inputs others

5. **Run execution:**
   - Click button "Start" в panel control

### Example: Simple network components

```mermaid
flowchart LR
    Source["Источник данных<br/>UMatrixSource"] --> Process["Processing<br/>UStatistic"]
    Process --> Output["Выход<br/>UIO"]
```

**Example creation component programmatically:**

```cpp
#include <rdk.h>
using namespace RDK;

// Создание хранилища и движка
UStorage storage;
UEngine engine;
engine.SetStorage(&storage);

// Загрузка библиотек
std::list<ULibrary*> libs;
RdkLoadPredefinedLibraries(libs);
for(auto lib : libs) {
    storage.AddCollection(lib);
}
storage.BuildStorage();

// Создание компонента
auto source = storage.CreateComponent<UMatrixSource>("Source");
source->FileName = "data.csv";
source->Build();

auto processor = storage.CreateComponent<UStatistic>("Processor");
processor->Build();

// Соединение компонентов
processor->InputData.AttachTo(&source->OutputMatrix);

// Выполнение
engine.GetEnvironment()->Start();
for(int i = 0; i < 10; i++) {
    source->Calculate();
    processor->Calculate();
}
```

**Example configuration file project (XML):**

```xml
<Project>
  <Name>MyFirstProject</Name>
  <Components>
    <Component Name="Source" Class="UMatrixSource">
      <Properties>
        <Property Name="FileName" Type="string">data.csv</Property>
      </Properties>
    </Component>
    <Component Name="Processor" Class="UStatistic">
      <Properties>
        <Property Name="InputData" Type="link">Source.OutputMatrix</Property>
      </Properties>
    </Component>
  </Components>
</Project>
```

### Next steps

- [Component system](../../Rdk/Docs/Guides/Component-System.md) - detailed description work с components
- [Overview libraries](../Libraries/Overview.md) - available library components
- [GUI Overview](../GUI/Overview.md) - description interface

---
