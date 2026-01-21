# Компонентная система

## Обзор

Компонентная система является основой архитектуры Nmsdk. Все функциональные единицы реализованы как компоненты, которые могут быть соединены в сети для выполнения вычислений.

## Базовые концепции

### Компонент (UComponent)

**UComponent** - базовый класс для всех компонентов в системе. Каждый компонент:

- Наследуется от `UComponent` или `UNet`
- Имеет свойства (Properties) - параметры, состояния, входы, выходы
- Может быть соединен с другими компонентами
- Имеет жизненный цикл: Default → Build → Reset → Calculate

### Свойства (Properties)

Свойства компонентов могут быть следующих типов:

- **ptParameter** - параметр компонента (настраивается пользователем)
- **ptState** - состояние компонента (изменяется во время выполнения)
- **ptTemp** - временное свойство (используется для промежуточных вычислений)
- **ptInput** - входное свойство (получает данные от других компонентов)
- **ptOutput** - выходное свойство (передает данные другим компонентам)

Группы свойств:

- **pgPublic** - публичное свойство (доступно пользователю)
- **pgSystem** - системное свойство (внутреннее использование)
- **pgInput** - входная группа
- **pgOutput** - выходная группа

### Контейнер (UContainer)

**UContainer** - контейнер для группировки компонентов. Позволяет:

- Организовывать компоненты в иерархические структуры
- Управлять жизненным циклом группы компонентов
- Изолировать компоненты друг от друга

### Сеть (UNet)

**UNet** - сеть компонентов, наследник `UItem`. Сеть:

- Содержит компоненты и их соединения
- Управляет выполнением компонентов
- Обеспечивает передачу данных между компонентами

### Окружение (UEnvironment)

**UEnvironment** - окружение выполнения компонентов. Управляет:

- Временем выполнения (TimeStep)
- Логированием
- Обработкой исключений
- Выполнением компонентов

### Хранилище (UStorage)

**UStorage** - хранилище (реестр) компонентов. Предоставляет:

- Реестр классов компонентов
- Фабрики для создания компонентов
- Описания компонентов
- Управление библиотеками

## Жизненный цикл компонента

### 1. Default (ADefault)

Инициализация значений по умолчанию. Вызывается при создании компонента.

```cpp
virtual bool ADefault(void);
```

### 2. Build (ABuild)

Построение структуры компонента. Вызывается после установки всех параметров.

```cpp
virtual bool ABuild(void);
```

### 3. Reset (AReset)

Сброс состояния компонента. Вызывается перед началом вычислений.

```cpp
virtual bool AReset(void);
```

### 4. Calculate (ACalculate)

Выполнение вычислений компонента. Вызывается на каждом шаге времени.

```cpp
virtual bool ACalculate(void);
```

## Создание компонентов

### Регистрация компонента в библиотеке

Каждая библиотека регистрирует свои компоненты в методе `CreateClassSamples()`:

```cpp
void MyLibrary::CreateClassSamples(UStorage *storage)
{
    // Регистрация компонента
    storage->RegisterComponent<MyComponent>("MyComponent");
}
```

### Создание экземпляра компонента

Компоненты создаются через хранилище:

```cpp
// Создание компонента
MyComponent* comp = storage->CreateComponent<MyComponent>();

// Или через имя
UComponent* comp = storage->CreateComponent("MyComponent");
```

## Система свойств

### Определение свойств

Свойства определяются в классе компонента:

```cpp
class MyComponent: public UComponent
{
public:
    // Параметр
    UProperty<double, MyComponent, ptPubParameter> MyParameter;
    
    // Вход
    UPropertyInputData<double, MyComponent> MyInput;
    
    // Выход
    UPropertyOutputData<double, MyComponent, ptPubParameter | ptOutput> MyOutput;
};
```

### Типы свойств

#### UProperty<T, ComponentT, Flags>
Базовое свойство типа T.

#### UPropertyInputData<T, ComponentT>
Входное свойство для получения данных.

#### UPropertyOutputData<T, ComponentT, Flags>
Выходное свойство для передачи данных.

#### UPropertyInput / UPropertyOutput
Специализированные входы/выходы.

### Соединение свойств

Свойства соединяются через коннекторы:

```cpp
// Соединение выхода одного компонента с входом другого
connector->Connect(component1->MyOutput, component2->MyInput);
```

## Контейнеры и сети

### Контейнер (UContainer)

Контейнер группирует компоненты:

```cpp
UContainer* container = storage->CreateContainer();
container->AddComponent(component1);
container->AddComponent(component2);
```

### Сеть (UNet)

Сеть организует компоненты и их соединения:

```cpp
UNet* net = storage->CreateNet();
net->AddComponent(component1);
net->AddComponent(component2);
// Настройка соединений
```

## Сериализация компонентов

### XML сериализация

Компоненты могут быть сериализованы в XML:

```cpp
UXMLEnvSerialize serializer;
serializer.Serialize(component, xmlFile);
```

### Бинарная сериализация

Для эффективного хранения используется бинарная сериализация:

```cpp
UBinaryEnvSerialize serializer;
serializer.Serialize(component, binaryFile);
```

## Описания компонентов

### UComponentDescription

Описание компонента содержит:

- Имя класса
- Параметры и их типы
- Входы и выходы
- Метаданные

### UContainerDescription

Описание контейнера содержит:

- Структуру контейнера
- Компоненты внутри
- Соединения между компонентами

## Фабрики компонентов

### UComponentFactory

Фабрика для создания компонентов определенного типа:

```cpp
UComponentFactory* factory = storage->GetFactory("MyComponent");
UComponent* component = factory->Create();
```

### UComponentAbstractFactory

Абстрактная фабрика для создания компонентов.

## Библиотеки компонентов

### ULibrary

Библиотека компонентов:

- Регистрирует компоненты в хранилище
- Предоставляет метаданные о библиотеке
- Управляет версионированием

### Регистрация библиотеки

Библиотеки регистрируются при инициализации:

```cpp
bool RdkLoadPredefinedLibraries(std::list<ULibrary*> &libs_list)
{
    libs_list.push_back(&MyLibrary);
    return true;
}
```

## Пример создания компонента

```cpp
class MyComponent: public UComponent
{
public:
    // Параметр
    UProperty<int, MyComponent, ptPubParameter> Count;
    
    // Вход
    UPropertyInputData<double, MyComponent> Input;
    
    // Выход
    UPropertyOutputData<double, MyComponent, ptPubParameter | ptOutput> Output;

protected:
    virtual bool ADefault(void)
    {
        Count = 10;
        return true;
    }
    
    virtual bool ABuild(void)
    {
        // Инициализация структур
        return true;
    }
    
    virtual bool AReset(void)
    {
        // Сброс состояния
        return true;
    }
    
    virtual bool ACalculate(void)
    {
        // Вычисления
        Output = Input * Count;
        return true;
    }
};
```

## См. также

- [01-Rdk-Core-Structure.md](01-Rdk-Core-Structure.md) - структура ядра Rdk
- [Docs/Libraries/Overview.md](../Docs/Libraries/Overview.md) - обзор библиотек компонентов
- [00-Project-Overview.md](00-Project-Overview.md) - общий обзор проекта

