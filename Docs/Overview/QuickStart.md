# Быстрый старт (Quick Start)

## RU

### Установка зависимостей

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install build-essential cmake qtbase5-dev
```

#### Windows

- Установите Visual Studio 2019 или новее
- Установите CMake 3.16+
- Установите Qt5

### Сборка проекта

```bash
# Создать директорию сборки
mkdir build
cd build

# Конфигурация CMake
cmake ..

# Сборка
cmake --build . -j$(nproc)  # Linux
# или
cmake --build . --config Release  # Windows
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
    Source[Источник данных] --> Process[Обработка]
    Process --> Output[Выход]
```

### Следующие шаги

- [Компонентная система](../Components-And-Configuration/Component-System.md) - детальное описание работы с компонентами
- [Обзор библиотек](../Libraries/Overview.md) - доступные библиотеки компонентов
- [GUI Overview](../GUI/Overview.md) - описание интерфейса

---

## EN

### Installing Dependencies

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install build-essential cmake qtbase5-dev
```

#### Windows

- Install Visual Studio 2019 or newer
- Install CMake 3.16+
- Install Qt5

### Building the Project

```bash
# Create build directory
mkdir build
cd build

# Configure CMake
cmake ..

# Build
cmake --build . -j$(nproc)  # Linux
# or
cmake --build . --config Release  # Windows
```

### Creating Your First Project

1. **Launch NeuroModeler:**
   ```bash
   ./Bin/Platform/Linux/NeuroModeler
   ```

2. **Create a new project:**
   - File → New Project

3. **Add a component:**
   - Drag a component from the library to the diagram editor
   - Configure component parameters

4. **Connect components:**
   - Connect outputs of some components to inputs of others

5. **Start execution:**
   - Press the "Start" button in the control panel

### Example: Simple Component Network

### Next Steps

- [Component System](../Components-And-Configuration/Component-System.md) - detailed component description
- [Libraries Overview](../Libraries/Overview.md) - available component libraries
- [GUI Overview](../GUI/Overview.md) - interface description
