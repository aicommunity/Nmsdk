# Генерация алиасов свойств

## Обзор

Система автоматической генерации алиасов свойств интегрирована в процесс создания описаний классов (ClDesc). Алиасы генерируются автоматически для компонентов с вложенными структурами (например, `NPulseNeuron`) и сохраняются в Favorites описаний классов.

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

## Устранение проблем

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

