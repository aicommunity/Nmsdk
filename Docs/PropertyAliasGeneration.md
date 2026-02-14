# Генерация алиасов свойств

## Обзор

Система автоматической генерации алиасов свойств интегрирована в процесс создания описаний классов (ClDesc). Алиасы генерируются автоматически для компонентов с вложенными структурами (например, `NPulseNeuron`) и сохраняются в Favorites описаний классов.

Алиасы свойств позволяют создавать "порты" верхнего уровня для входов/выходов глубоко вложенных компонентов, упрощая создание связей между компонентами и улучшая читаемость диаграмм.

## Процесс генерации

### 1. Сборка проекта

#### Linux:
```bash
cd /home/user/Nmsdk
mkdir -p build
cd build
cmake ..
cmake --build . -j$(nproc)
```

#### Windows:
```cmd
cd C:\path\to\Nmsdk
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64
cmake --build . --config Release
```

Или используйте скрипт:
```bash
./build-windows.bat release
```

### 2. Запуск генерации

После успешной сборки запустите `NeuroModelerConsole` с флагом `--generate-cldesc`:

#### Linux:
```bash
cd /home/user/Nmsdk
Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc \
    --cldesc-lexicon Docs/ClDescLexicon.json
```

#### Windows:
```cmd
cd C:\path\to\Nmsdk
Bin\Platform\Win\NeuroModelerConsole.exe --generate-cldesc ^
    --cldesc-lexicon Docs\ClDescLexicon.json
```

### 3. Опции генерации

Доступные опции:

- `--generate-cldesc` или `-g` - запустить генерацию описаний классов (включая алиасы)
- `--cldesc-lexicon <path>` или `-l <path>` - путь к словарю локализации (по умолчанию: `Docs/ClDescLexicon.json`)
- `--cldesc-library <name>` или `-C <name>` - ограничить генерацию указанной библиотекой (можно повторить)
- `--cldesc-class <class>` или `-K <class>` - ограничить генерацию указанным классом (можно повторить)
- `--cldesc-force` или `-F` - принудительно перезаписать существующие описания

### Примеры использования

#### Генерация для всех компонентов:
```bash
Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc
```

#### Генерация только для библиотеки PulseLibrary:
```bash
Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc \
    --cldesc-library PulseLibrary
```

#### Генерация только для конкретного класса:
```bash
Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc \
    --cldesc-class NPulseNeuron
```

#### Генерация с кастомным словарем:
```bash
Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc \
    --cldesc-lexicon /path/to/custom/lexicon.json
```

## Что происходит при генерации

1. **Загрузка библиотек**: Загружаются все предопределенные библиотеки через `RdkLoadPredefinedLibraries()`

2. **Анализ компонентов**: Для каждого класса из `UStorage`:
   - Создается экземпляр компонента
   - Анализируется его структура (вложенные компоненты)
   - Определяются важные свойства (выходы, входы, параметры)
   - Анализируется частота использования свойств в конфигурациях (если доступно)

3. **Генерация алиасов**: Для компонентов типа `UNet` с вложенными элементами:
   - Генерируются алиасы для важных свойств
   - Алиасы добавляются в Favorites описания класса
   - Примеры: `LTZoneOutput` → `LTZone.Output`, `Soma1ExcChannelOutput` → `Soma1.ExcChannel.Output`

4. **Сохранение**: XML описания сохраняются в `Bin/ClDesc/<Library>/ru-RU/<Class>.xml`

## Результат

После генерации:

- **XML описания классов** обновлены в `Bin/ClDesc/`
- **Алиасы свойств** добавлены в секцию `<Favorites>` каждого XML файла
- **Формат алиасов**: `AliasName:ComponentPath.PropertyName` (например, `LTZoneOutput:LTZone.Output`)

## Использование алиасов

После генерации алиасы автоматически:

1. **Загружаются в UNet** при инициализации компонента (метод `ABuild`)
2. **Отображаются в GUI**:
   - В списке Favorites в `UComponentsListWidget` (с пометкой `[Alias]`)
   - В списке портов в `UModernDiagramWidget`
3. **Используются для создания связей**:
   - В диаграмме можно создавать связи через короткие имена алиасов
   - Метод `CreateLinkByAlias()` автоматически разрешает алиасы в полные пути

## Настройка генерации

Настройки генерации можно изменить в файле `Docs/PropertyAliasConfig.json`:

```json
{
  "generationRules": {
    "minDepth": 2,                    // Минимальная глубина вложенности
    "preferredTypes": ["ptOutput", "ptInput", "ptParameter"],
    "maxAliasesPerComponent": 20,     // Максимум алиасов на компонент
    "excludePatterns": ["DataInput*", "DataOutput*"]
  }
}
```

## Ручное управление алиасами

Алиасы можно добавлять/редактировать вручную через:

1. **Редактор описаний классов** в GUI приложения NeuroModeler
2. **Прямое редактирование XML** в `Bin/ClDesc/<Library>/ru-RU/<Class>.xml`

Формат в XML:
```xml
<Favorites>
  <LTZoneOutput>
    <Path>LTZone.Output</Path>
  </LTZoneOutput>
</Favorites>
```

## Проверка результата

После генерации проверьте:

1. **XML файлы** в `Bin/ClDesc/PulseLibrary/ru-RU/` должны содержать секцию `<Favorites>` с алиасами
2. **В GUI** при выборе компонента `NPulseNeuron` в списке Favorites должны отображаться алиасы с пометкой `[Alias]`
3. **В диаграмме** алиасы должны отображаться в списке портов компонента

## Программное использование алиасов

### Структура UPropertyAlias

```cpp
struct UPropertyAlias
{
    std::string AliasName;        // Имя алиаса (отображаемое имя порта)
    std::string ComponentPath;     // Путь к компоненту (например: "SubNet.Neuron1")
    std::string PropertyName;      // Имя свойства в целевом компоненте
    unsigned int PropertyType;     // Тип свойства (ptPubInput, ptPubOutput и т.д.)
    
    // Методы
    std::string GetFullPropertyPath() const;  // Возвращает ComponentPath.PropertyName
    bool IsInput() const;                     // Проверяет, является ли алиас входом
    bool IsOutput() const;                    // Проверяет, является ли алиас выходом
};
```

### Пример 1: Добавление алиасов программно

```cpp
#include <rdk.h>

using namespace RDK;

// Создание компонента с вложенными компонентами
auto network = storage->CreateComponent<UNet>("MyNetwork");

// Добавление вложенного компонента
auto subNet = storage->CreateComponent<UNet>("SubNet");
auto neuron = storage->CreateComponent<NPulseNeuron>("Neuron1");
subNet->AddComponent(neuron);
network->AddComponent(subNet);

// Инициализация компонентов
network->Default();
network->Build();

// Добавление алиаса для выхода нейрона
bool success = network->AddPropertyAlias(
    "NeuronOutput",           // Имя алиаса
    "SubNet.Neuron1",         // Путь к компоненту
    "Output",                 // Имя свойства
    ptPubOutput | ptOutput    // Тип свойства
);

if (success) {
    std::cout << "Алиас успешно добавлен" << std::endl;
}

// Добавление алиаса для входа (тип определяется автоматически)
network->AddPropertyAlias(
    "NeuronInput",
    "SubNet.Neuron1",
    "Input",
    0  // Тип будет определен автоматически
);
```

### Пример 2: Проверка и получение алиасов

```cpp
// Проверка существования алиаса
if (network->CheckPropertyAlias("NeuronOutput")) {
    std::cout << "Алиас NeuronOutput существует" << std::endl;
}

// Получение алиаса
const UPropertyAlias* alias = network->GetPropertyAlias("NeuronOutput");
if (alias) {
    std::cout << "Имя алиаса: " << alias->AliasName << std::endl;
    std::cout << "Путь к компоненту: " << alias->ComponentPath << std::endl;
    std::cout << "Имя свойства: " << alias->PropertyName << std::endl;
    std::cout << "Полный путь: " << alias->GetFullPropertyPath() << std::endl;
    
    if (alias->IsOutput()) {
        std::cout << "Это выходной алиас" << std::endl;
    }
    if (alias->IsInput()) {
        std::cout << "Это входной алиас" << std::endl;
    }
}

// Получение всех алиасов
const auto& allAliases = network->GetPropertyAliases();
for (const auto& pair : allAliases) {
    const std::string& aliasName = pair.first;
    const UPropertyAlias& alias = pair.second;
    std::cout << "Алиас: " << aliasName 
              << " -> " << alias.GetFullPropertyPath() << std::endl;
}

// Получение только выходных алиасов
auto outputAliases = network->GetPropertyAliasesByType(ptPubOutput | ptOutput);
for (const auto& alias : outputAliases) {
    std::cout << "Выходной алиас: " << alias.AliasName << std::endl;
}

// Получение только входных алиасов
auto inputAliases = network->GetPropertyAliasesByType(ptPubInput | ptInput);
for (const auto& alias : inputAliases) {
    std::cout << "Входной алиас: " << alias.AliasName << std::endl;
}
```

### Пример 3: Создание связей через алиасы

```cpp
// Создание двух сетей с алиасами
auto network1 = storage->CreateComponent<UNet>("Network1");
auto network2 = storage->CreateComponent<UNet>("Network2");

// Настройка network1
auto subNet1 = storage->CreateComponent<UNet>("SubNet");
auto neuron1 = storage->CreateComponent<NPulseNeuron>("Neuron");
subNet1->AddComponent(neuron1);
network1->AddComponent(subNet1);
network1->Default();
network1->Build();

// Добавление алиаса выхода
network1->AddPropertyAlias("Output", "SubNet.Neuron", "Output", ptPubOutput | ptOutput);

// Настройка network2
auto subNet2 = storage->CreateComponent<UNet>("SubNet");
auto neuron2 = storage->CreateComponent<NPulseNeuron>("Neuron");
subNet2->AddComponent(neuron2);
network2->AddComponent(subNet2);
network2->Default();
network2->Build();

// Добавление алиаса входа
network2->AddPropertyAlias("Input", "SubNet.Neuron", "Input", ptPubInput | ptInput);

// Создание связи через алиасы
bool linkCreated = network1->CreateLinkByAlias("Output", network2->GetName() + ".Input");
if (linkCreated) {
    std::cout << "Связь создана успешно" << std::endl;
}

// Разрыв связи через алиасы
network1->BreakLinkByAlias("Output", network2->GetName() + ".Input");
```

### Пример 4: Разрешение алиасов в полные пути

```cpp
// Разрешение алиаса в полный путь
std::string resolvedPath = network->ResolveAlias("NeuronOutput");
std::cout << "Разрешенный путь: " << resolvedPath << std::endl;
// Выведет: "SubNet.Neuron1.Output"

// Если алиас не найден, возвращается исходная строка
std::string unknownAlias = network->ResolveAlias("UnknownAlias");
std::cout << "Неизвестный алиас: " << unknownAlias << std::endl;
// Выведет: "UnknownAlias"
```

### Пример 5: Управление алиасами

```cpp
// Удаление конкретного алиаса
network->DelPropertyAlias("NeuronOutput");

// Удаление всех алиасов
network->ClearPropertyAliases();

// Проверка после удаления
if (!network->CheckPropertyAlias("NeuronOutput")) {
    std::cout << "Алиас удален" << std::endl;
}
```

### Пример 6: Загрузка алиасов из описания класса

```cpp
// Алиасы автоматически загружаются при вызове ABuild()
// Но можно загрузить их вручную:

auto component = storage->CreateComponent<NPulseNeuron>("Neuron");
component->Default();
component->Build();  // Алиасы загружаются автоматически здесь

// Или вручную для UNet:
auto network = storage->CreateComponent<UNet>("Network");
network->Default();
network->Build();
network->LoadPropertyAliasesFromDescription();  // Загрузка из ClDesc

// Проверка загруженных алиасов
const auto& aliases = network->GetPropertyAliases();
std::cout << "Загружено алиасов: " << aliases.size() << std::endl;
```

### Пример 7: Использование алиасов в компонентах

```cpp
// Компонент, который использует алиасы для доступа к вложенным свойствам
class MyNetworkComponent : public UNet
{
public:
    UProperty<double, MyNetworkComponent, ptPubInput> Input;
    UProperty<double, MyNetworkComponent, ptPubOutput> Output;

    MyNetworkComponent() : 
        Input("Input", this),
        Output("Output", this)
    {
    }

protected:
    virtual bool ABuild(void) override
    {
        // Создание вложенных компонентов
        auto subNet = GetStorage()->CreateComponent<UNet>("SubNet");
        auto processor = GetStorage()->CreateComponent<UProcessor>("Processor");
        subNet->AddComponent(processor);
        AddComponent(subNet);
        
        // Добавление алиасов для удобного доступа
        AddPropertyAlias("ProcessorInput", "SubNet.Processor", "Input", ptPubInput | ptInput);
        AddPropertyAlias("ProcessorOutput", "SubNet.Processor", "Output", ptPubOutput | ptOutput);
        
        return true;
    }
    
    virtual bool ACalculate(void) override
    {
        // Использование алиасов для создания связей
        // Связываем вход компонента с входом процессора через алиас
        auto processorInput = GetComponent("SubNet.Processor");
        if (processorInput) {
            // Получаем свойство через алиас
            const UPropertyAlias* alias = GetPropertyAlias("ProcessorInput");
            if (alias) {
                // Используем полный путь для доступа
                std::string fullPath = alias->GetFullPropertyPath();
                // Создаем связь
                Input.Connect(processorInput->FindProperty(fullPath));
            }
        }
        
        // Выполнение расчета
        CalculateSubComponents();
        
        // Получение результата через алиас
        const UPropertyAlias* outputAlias = GetPropertyAlias("ProcessorOutput");
        if (outputAlias) {
            auto processor = GetComponent("SubNet.Processor");
            if (processor) {
                auto outputProp = processor->FindProperty(outputAlias->PropertyName);
                if (outputProp) {
                    // Копируем значение в выход компонента
                    Output = outputProp->GetData<double>();
                }
            }
        }
        
        return true;
    }
};
```

### Пример 8: Итерация по алиасам и фильтрация

```cpp
// Получение всех алиасов определенного типа
auto outputAliases = network->GetPropertyAliasesByType(ptPubOutput | ptOutput);

// Фильтрация алиасов по имени компонента
std::vector<UPropertyAlias> filteredAliases;
const auto& allAliases = network->GetPropertyAliases();
for (const auto& pair : allAliases) {
    const UPropertyAlias& alias = pair.second;
    // Фильтруем алиасы, которые относятся к определенному компоненту
    if (alias.ComponentPath.find("Neuron") != std::string::npos) {
        filteredAliases.push_back(alias);
    }
}

// Вывод отфильтрованных алиасов
for (const auto& alias : filteredAliases) {
    std::cout << "Алиас нейрона: " << alias.AliasName 
              << " -> " << alias.GetFullPropertyPath() << std::endl;
}
```

### Пример 9: Динамическое создание алиасов на основе структуры компонента

```cpp
// Функция для автоматического создания алиасов для всех выходов вложенных компонентов
void CreateAliasesForOutputs(UNet* network, const std::string& componentPath, int depth = 0)
{
    if (depth > 3)  // Ограничение глубины
        return;
    
    auto component = network->GetComponent(componentPath);
    if (!component)
        return;
    
    // Получаем все свойства компонента
    const auto& properties = component->GetPropertiesList();
    
    for (const auto& propEntry : properties) {
        const std::string& propName = propEntry.first;
        
        // Проверяем, является ли свойство выходом
        if (propEntry.second.CheckMask(ptPubOutput | ptOutput)) {
            // Создаем имя алиаса
            std::string aliasName = componentPath;
            std::replace(aliasName.begin(), aliasName.end(), '.', '_');
            aliasName += "_" + propName;
            
            // Добавляем алиас
            network->AddPropertyAlias(aliasName, componentPath, propName, ptPubOutput | ptOutput);
        }
    }
    
    // Рекурсивно обрабатываем вложенные компоненты
    if (auto subNet = dynamic_cast<UNet*>(component.Get())) {
        auto subComponents = subNet->GetComponents();
        for (const auto& subComp : subComponents) {
            std::string subPath = componentPath.empty() 
                ? subComp->GetName() 
                : componentPath + "." + subComp->GetName();
            CreateAliasesForOutputs(network, subPath, depth + 1);
        }
    }
}

// Использование
auto network = storage->CreateComponent<UNet>("Network");
// ... настройка сети ...
network->Default();
network->Build();

// Создание алиасов для всех выходов
CreateAliasesForOutputs(network, "");
```

### Пример 10: Валидация алиасов

```cpp
// Функция для проверки валидности всех алиасов
bool ValidatePropertyAliases(UNet* network)
{
    bool allValid = true;
    const auto& aliases = network->GetPropertyAliases();
    
    for (const auto& pair : aliases) {
        const std::string& aliasName = pair.first;
        const UPropertyAlias& alias = pair.second;
        
        // Проверяем, существует ли компонент
        auto component = network->GetComponent(alias.ComponentPath);
        if (!component) {
            std::cerr << "Ошибка: компонент не найден для алиаса " << aliasName 
                      << " (путь: " << alias.ComponentPath << ")" << std::endl;
            allValid = false;
            continue;
        }
        
        // Проверяем, существует ли свойство
        auto property = component->FindProperty(alias.PropertyName);
        if (!property) {
            std::cerr << "Ошибка: свойство не найдено для алиаса " << aliasName 
                      << " (свойство: " << alias.PropertyName << ")" << std::endl;
            allValid = false;
            continue;
        }
        
        // Проверяем соответствие типа свойства
        unsigned int actualType = property->GetType();
        if ((actualType & alias.PropertyType) == 0) {
            std::cerr << "Предупреждение: тип свойства не соответствует для алиаса " 
                      << aliasName << std::endl;
        }
    }
    
    return allValid;
}

// Использование
if (!ValidatePropertyAliases(network)) {
    std::cerr << "Обнаружены невалидные алиасы!" << std::endl;
}
```

### Лучшие практики

1. **Используйте осмысленные имена алиасов**: имена должны отражать назначение свойства
2. **Проверяйте существование алиасов** перед использованием
3. **Валидируйте алиасы** после их создания или загрузки
4. **Используйте автоматическое определение типа** (передавайте 0) когда возможно
5. **Загружайте алиасы из описаний классов** вместо ручного создания когда возможно
6. **Документируйте алиасы** в описаниях классов для других разработчиков

### Устранение проблем

### Алиасы не генерируются

- Убедитесь, что компонент является `UNet` (имеет вложенные компоненты)
- Проверьте, что компонент имеет свойства на глубине >= 2 уровней
- Проверьте логи генератора на наличие ошибок

### Алиасы не отображаются в GUI

- Убедитесь, что компонент был собран после генерации описаний (`ABuild()` вызывается при сборке)
- Проверьте, что описание класса загружено из `Bin/ClDesc/`
- Перезапустите приложение после генерации

### Ошибки при создании связей через алиасы

- Убедитесь, что оба компонента находятся в одной сети (алиасы работают только внутри одной сети)
- Проверьте, что алиасы правильно разрешаются в полные пути
- Используйте обычный метод создания связей, если алиасы не работают

### Программные ошибки при работе с алиасами

- **Проверяйте результат `AddPropertyAlias()`**: метод возвращает `false` если алиас уже существует
- **Используйте `CheckPropertyAlias()`** перед доступом к алиасу
- **Валидируйте пути к компонентам**: убедитесь, что компонент существует перед созданием алиаса
- **Проверяйте типы свойств**: используйте `DetectPropertyType()` для автоматического определения типа

---

## EN

### Overview

The automatic property alias generation system is integrated into the class description (ClDesc) creation process. Aliases are automatically generated for components with nested structures (e.g., `NPulseNeuron`) and saved in Favorites of class descriptions.

Property aliases allow creating "ports" at the top level for inputs/outputs of deeply nested components, simplifying component connections and improving diagram readability.

### Generation Process

#### 1. Building the Project

#### Linux:
```bash
cd /home/user/Nmsdk
mkdir -p build
cd build
cmake ..
cmake --build . -j$(nproc)
```

#### Windows:
```cmd
cd C:\path\to\Nmsdk
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64
cmake --build . --config Release
```

Or use the script:
```bash
./build-windows.bat release
```

#### 2. Running Generation

After successful build, run `NeuroModelerConsole` with `--generate-cldesc` flag:

#### Linux:
```bash
cd /home/user/Nmsdk
Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc \
    --cldesc-lexicon Docs/ClDescLexicon.json
```

#### Windows:
```cmd
cd C:\path\to\Nmsdk
Bin\Platform\Win\NeuroModelerConsole.exe --generate-cldesc ^
    --cldesc-lexicon Docs\ClDescLexicon.json
```

#### 3. Generation Options

Available options:

- `--generate-cldesc` or `-g` - run class description generation (including aliases)
- `--cldesc-lexicon <path>` or `-l <path>` - path to localization dictionary (default: `Docs/ClDescLexicon.json`)
- `--cldesc-library <name>` or `-C <name>` - limit generation to specified library (can be repeated)
- `--cldesc-class <class>` or `-K <class>` - limit generation to specified class (can be repeated)
- `--cldesc-force` or `-F` - force overwrite existing descriptions

### Usage Examples

#### Generate for all components:
```bash
Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc
```

#### Generate only for PulseLibrary:
```bash
Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc \
    --cldesc-library PulseLibrary
```

#### Generate only for specific class:
```bash
Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc \
    --cldesc-class NPulseNeuron
```

#### Generate with custom dictionary:
```bash
Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc \
    --cldesc-lexicon /path/to/custom/lexicon.json
```

### What Happens During Generation

1. **Library Loading**: All predefined libraries are loaded via `RdkLoadPredefinedLibraries()`

2. **Component Analysis**: For each class from `UStorage`:
   - Component instance is created
   - Its structure is analyzed (nested components)
   - Important properties are identified (outputs, inputs, parameters)
   - Property usage frequency in configurations is analyzed (if available)

3. **Alias Generation**: For `UNet`-type components with nested elements:
   - Aliases are generated for important properties
   - Aliases are added to class description Favorites
   - Examples: `LTZoneOutput` → `LTZone.Output`, `Soma1ExcChannelOutput` → `Soma1.ExcChannel.Output`

4. **Saving**: XML descriptions are saved to `Bin/ClDesc/<Library>/ru-RU/<Class>.xml`

### Result

After generation:

- **XML class descriptions** updated in `Bin/ClDesc/`
- **Property aliases** added to `<Favorites>` section of each XML file
- **Alias format**: `AliasName:ComponentPath.PropertyName` (e.g., `LTZoneOutput:LTZone.Output`)

### Using Aliases

After generation, aliases are automatically:

1. **Loaded in UNet** when component is initialized (method `ABuild`)
2. **Displayed in GUI**:
   - In Favorites list in `UComponentsListWidget` (marked with `[Alias]`)
   - In port list in `UModernDiagramWidget`
3. **Used for creating connections**:
   - In diagram, connections can be created via short alias names
   - Method `CreateLinkByAlias()` automatically resolves aliases to full paths

### Generation Configuration

Generation settings can be changed in `Docs/PropertyAliasConfig.json`:

```json
{
  "generationRules": {
    "minDepth": 2,                    // Minimum nesting depth
    "preferredTypes": ["ptOutput", "ptInput", "ptParameter"],
    "maxAliasesPerComponent": 20,     // Maximum aliases per component
    "excludePatterns": ["DataInput*", "DataOutput*"]
  }
}
```

### Manual Alias Management

Aliases can be added/edited manually via:

1. **Class description editor** in NeuroModeler GUI application
2. **Direct XML editing** in `Bin/ClDesc/<Library>/ru-RU/<Class>.xml`

Format in XML:
```xml
<Favorites>
  <LTZoneOutput>
    <Path>LTZone.Output</Path>
  </LTZoneOutput>
</Favorites>
```

### Programmatic Usage of Aliases

#### UPropertyAlias Structure

```cpp
struct UPropertyAlias
{
    std::string AliasName;        // Alias name (displayed port name)
    std::string ComponentPath;     // Path to component (e.g.: "SubNet.Neuron1")
    std::string PropertyName;      // Property name in target component
    unsigned int PropertyType;     // Property type (ptPubInput, ptPubOutput, etc.)
    
    // Methods
    std::string GetFullPropertyPath() const;  // Returns ComponentPath.PropertyName
    bool IsInput() const;                     // Checks if alias is input
    bool IsOutput() const;                    // Checks if alias is output
};
```

#### Example 1: Adding Aliases Programmatically

```cpp
#include <rdk.h>

using namespace RDK;

// Creating component with nested components
auto network = storage->CreateComponent<UNet>("MyNetwork");

// Adding nested component
auto subNet = storage->CreateComponent<UNet>("SubNet");
auto neuron = storage->CreateComponent<NPulseNeuron>("Neuron1");
subNet->AddComponent(neuron);
network->AddComponent(subNet);

// Initializing components
network->Default();
network->Build();

// Adding alias for neuron output
bool success = network->AddPropertyAlias(
    "NeuronOutput",           // Alias name
    "SubNet.Neuron1",         // Component path
    "Output",                 // Property name
    ptPubOutput | ptOutput    // Property type
);

if (success) {
    std::cout << "Alias added successfully" << std::endl;
}

// Adding alias for input (type determined automatically)
network->AddPropertyAlias(
    "NeuronInput",
    "SubNet.Neuron1",
    "Input",
    0  // Type will be determined automatically
);
```

#### Example 2: Checking and Getting Aliases

```cpp
// Check if alias exists
if (network->CheckPropertyAlias("NeuronOutput")) {
    std::cout << "Alias NeuronOutput exists" << std::endl;
}

// Get alias
const UPropertyAlias* alias = network->GetPropertyAlias("NeuronOutput");
if (alias) {
    std::cout << "Alias name: " << alias->AliasName << std::endl;
    std::cout << "Component path: " << alias->ComponentPath << std::endl;
    std::cout << "Property name: " << alias->PropertyName << std::endl;
    std::cout << "Full path: " << alias->GetFullPropertyPath() << std::endl;
    
    if (alias->IsOutput()) {
        std::cout << "This is an output alias" << std::endl;
    }
    if (alias->IsInput()) {
        std::cout << "This is an input alias" << std::endl;
    }
}

// Get all aliases
const auto& allAliases = network->GetPropertyAliases();
for (const auto& pair : allAliases) {
    const std::string& aliasName = pair.first;
    const UPropertyAlias& alias = pair.second;
    std::cout << "Alias: " << aliasName 
              << " -> " << alias.GetFullPropertyPath() << std::endl;
}

// Get only output aliases
auto outputAliases = network->GetPropertyAliasesByType(ptPubOutput | ptOutput);
for (const auto& alias : outputAliases) {
    std::cout << "Output alias: " << alias.AliasName << std::endl;
}

// Get only input aliases
auto inputAliases = network->GetPropertyAliasesByType(ptPubInput | ptInput);
for (const auto& alias : inputAliases) {
    std::cout << "Input alias: " << alias.AliasName << std::endl;
}
```

#### Example 3: Creating Links via Aliases

```cpp
// Creating two networks with aliases
auto network1 = storage->CreateComponent<UNet>("Network1");
auto network2 = storage->CreateComponent<UNet>("Network2");

// Setup network1
auto subNet1 = storage->CreateComponent<UNet>("SubNet");
auto neuron1 = storage->CreateComponent<NPulseNeuron>("Neuron");
subNet1->AddComponent(neuron1);
network1->AddComponent(subNet1);
network1->Default();
network1->Build();

// Add output alias
network1->AddPropertyAlias("Output", "SubNet.Neuron", "Output", ptPubOutput | ptOutput);

// Setup network2
auto subNet2 = storage->CreateComponent<UNet>("SubNet");
auto neuron2 = storage->CreateComponent<NPulseNeuron>("Neuron");
subNet2->AddComponent(neuron2);
network2->AddComponent(subNet2);
network2->Default();
network2->Build();

// Add input alias
network2->AddPropertyAlias("Input", "SubNet.Neuron", "Input", ptPubInput | ptInput);

// Create link via aliases
bool linkCreated = network1->CreateLinkByAlias("Output", network2->GetName() + ".Input");
if (linkCreated) {
    std::cout << "Link created successfully" << std::endl;
}

// Break link via aliases
network1->BreakLinkByAlias("Output", network2->GetName() + ".Input");
```

#### Example 4: Resolving Aliases to Full Paths

```cpp
// Resolve alias to full path
std::string resolvedPath = network->ResolveAlias("NeuronOutput");
std::cout << "Resolved path: " << resolvedPath << std::endl;
// Output: "SubNet.Neuron1.Output"

// If alias not found, original string is returned
std::string unknownAlias = network->ResolveAlias("UnknownAlias");
std::cout << "Unknown alias: " << unknownAlias << std::endl;
// Output: "UnknownAlias"
```

#### Example 5: Alias Management

```cpp
// Delete specific alias
network->DelPropertyAlias("NeuronOutput");

// Delete all aliases
network->ClearPropertyAliases();

// Check after deletion
if (!network->CheckPropertyAlias("NeuronOutput")) {
    std::cout << "Alias deleted" << std::endl;
}
```

#### Example 6: Loading Aliases from Class Description

```cpp
// Aliases are automatically loaded when ABuild() is called
// But can be loaded manually:

auto component = storage->CreateComponent<NPulseNeuron>("Neuron");
component->Default();
component->Build();  // Aliases are automatically loaded here

// Or manually for UNet:
auto network = storage->CreateComponent<UNet>("Network");
network->Default();
network->Build();
network->LoadPropertyAliasesFromDescription();  // Load from ClDesc

// Check loaded aliases
const auto& aliases = network->GetPropertyAliases();
std::cout << "Loaded aliases: " << aliases.size() << std::endl;
```

### Best Practices

1. **Use meaningful alias names**: names should reflect property purpose
2. **Check alias existence** before using
3. **Validate aliases** after creation or loading
4. **Use automatic type detection** (pass 0) when possible
5. **Load aliases from class descriptions** instead of manual creation when possible
6. **Document aliases** in class descriptions for other developers

### Troubleshooting

#### Aliases Not Generated

- Ensure component is `UNet` (has nested components)
- Check that component has properties at depth >= 2 levels
- Check generator logs for errors

#### Aliases Not Displayed in GUI

- Ensure component was built after description generation (`ABuild()` is called during build)
- Check that class description is loaded from `Bin/ClDesc/`
- Restart application after generation

#### Errors When Creating Links via Aliases

- Ensure both components are in the same network (aliases work only within one network)
- Check that aliases are correctly resolved to full paths
- Use regular link creation method if aliases don't work

#### Programmatic Errors When Working with Aliases

- **Check `AddPropertyAlias()` result**: method returns `false` if alias already exists
- **Use `CheckPropertyAlias()`** before accessing alias
- **Validate component paths**: ensure component exists before creating alias
- **Check property types**: use `DetectPropertyType()` for automatic type detection

