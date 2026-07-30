# DETAILED ClDesc — методология для авторов и агентов

## RU

## 1. Цель и уровни зрелости

| Уровень | Что есть | Когда достаточно |
|---------|----------|------------------|
| **Skeleton** | Набор свойств из `CreateProperties()`, пустые/минимальные тексты | Новый класс только что зарегистрирован |
| **Autogen** | Header/Description из лексикона + stub; Favorites = сырые nested-алиасы | Быстрый каркас; **не** финальный UX |
| **DETAILED** | Смысловые Description; курируемые Favorites (primary + редкие I/O-aliases); при необходимости UI hints | Классы из SpikeSamples / демо / LLM `describe_class` |

Цель DETAILED: вкладка Favorites показывает **главные** свойства; второстепенные/технические остаются только в `Properties`.

Хранилище XML: `Bin/ClDesc/<Library>/ru-RU/<ClassName>.xml` (субмодуль Bin). Рядом с кодом в `Libraries/*` файлов ClDesc нет.

## 2. Каноническая схема XML

Источник истины: `Rdk/Core/Engine/UContainerDescription::{Save,Load}`.

```xml
<ClassDescription>
  <ClassName>UNoiseGen</ClassName>
  <Header>краткий заголовок для UI</Header>
  <Description>назначение, библиотека, когда применять</Description>
  <Properties>
    <NoiseLevel>
      <Header>Уровень шума</Header>
      <Description>поведение, единицы, edge vs level</Description>
      <Type>| ptPubParameter |</Type>
      <DataSelectionType>0</DataSelectionType>
      <ValueList Type="std::vector" Size="2" elemType="std::string">
        <elem Type="std::string"></elem>
        <elem Type="std::string"></elem>
      </ValueList>
      <PropertyType>257</PropertyType>
    </NoiseLevel>
  </Properties>
  <Favorites>
    <NoiseLevel>
      <Path>{CompName}:NoiseLevel</Path>
    </NoiseLevel>
    <Soma1ExcSynapse1Input>
      <Path>Soma1.ExcSynapse1.Input</Path>
    </Soma1ExcSynapse1Input>
  </Favorites>
</ClassDescription>
```

`DataSelectionType`: `0` произвольные, `1` checkbox, `2` диапазон, `3` список, `4` диапазон+шаг (`Step`).

### PropertyType (частые значения)

| Константа | Значение | Смысл |
|-----------|---------:|-------|
| `ptPubParameter` | 257 | публичный параметр |
| `ptPubState` | 258 | публичное состояние |
| `ptPubInput` | 264 | публичный вход |
| `ptPubOutput` | 272 | публичный выход |
| `ptSysParameter` | 513 | системный (`Id`/`Name`/`TimeStep`) |
| `ptPubSysParameter` | 769 | public+system (debug) |

См. также: [Bin/Docs/Examples/ClDesc-Example.md](../Bin/Docs/Examples/ClDesc-Example.md).

## 3. Конвейер инструментов

1. `NeuroModelerConsole --generate-cldesc` → skeleton/autogen тексты + (для `UNet`) aliases в Favorites.
2. Лексикон `Docs/ClDescLexicon.json`: `tokens`, `classOverrides`, `propertyOverrides`, `propertyFallbacks`.
3. DETAILED: **ручная** правка XML и/или GUI (`UClDescEditor`, `UClassFavoritesEditor`).
4. Markdown в `Libraries/*/Docs/Components/` — источник смысла; секция «Ключевые свойства / Favorites».

**Не** гонять массовый `--generate-cldesc --cldesc-force` после курации Favorites: генератор не создаёт curated direct Favorites и может добавить шумные aliases.

Ограничения `PropertyAliasAnalyzer`: не применяет полноценно `preferredTypes`; потолок ~20 aliases; часто попадают `Coord`/`Activity`/`Type`. Autogen **не** пишет top-level primary Favorites.

## 4. Конвенция Favorites

1. **Direct** (`Path` без `.`, обычно `{CompName}:PropName`) — primary / user-facing свойства.
2. **Alias** (`Path` с `.`) — только ценные nested **I/O** для связей на диаграмме.
3. **Secondary** — только в `Properties`, не в Favorites.

**Типичный secondary (inherited):** `Activity`, `Coord`, `Name`, `Id`, `TimeStep`, `StepDuration`, `CalculationDurationThreshold`, `MaxCalculationDuration`, `DebugSysEventsMask`.

**Антипаттерны aliases:** `*.Coord`, `*.Activity`, `*.Type`, `*.StepDuration`, deep `NeuronTrainer1.Neuron.Soma1.ExcChannel.*` без нужды в линке.

Критерий alias: «нужен ли порт на диаграмме чаще, чем раз в отладке?»

Эталон mix: `Bin/ClDesc/MotionControlLibrary/ru-RU/NActuatorSignals.xml` (direct + aliases). Эталон текстов: `ArduinoFirmata` ClDesc + Docs.

## 5. Правила Description

- Класс: назначение, библиотека, когда применять — не «сформировано автоматически».
- Свойство: эффект, единицы, edge vs level, побочные эффекты.
- Header — короткий UI; Description — поведение.
- Запрет: «%1 — свойство %2», дословный CamelCase без семантики.

Источники: `.h`/`.cpp` (`ADefault`/`ABuild`/`ACalculate`), `Libraries/*/Docs/Components/*.md`, `Bin/Configs/SpikeSamples`.

## 6. Чеклист DETAILED для одного класса

1. Список свойств из ClDesc минус inherited secondary.
2. Прочитать реализацию и Component.md (или добавить секцию).
3. Primary (обычно 5–15) → direct Favorites.
4. Aliases: ≤ полезных nested I/O; иначе очистить autogen-шум.
5. Переписать Description там, где stub/ложь.
6. Проверить в NeuroModeler: вкладка Favorites, `[Alias]`, диаграмма.

## 7. Анти-примеры

- Учебный пример со схемой `DisplayName`/`Category` — устарел (исправлен в ClDesc-Example.md).
- Композит с ровно 20 aliases на `Coord`/`Activity`/`Type` детей — не DETAILED.
- Leaf (`NPSynapse`, `NPGenerator`) с пустым Favorites при насыщенных Parameters — пробел UX.

## 8. Связанные файлы

| Путь | Роль |
|------|------|
| [PropertyAliasGeneration.md](PropertyAliasGeneration.md) | Автоген aliases + dual-purpose Favorites |
| [Reports/25-ClDesc-Autogen.md](../Reports/25-ClDesc-Autogen.md) | Отчёт автогена; Favorites ≠ DETAILED |
| [ClDescLexicon.json](ClDescLexicon.json) | Overrides для текстов |
| `App/NeuroModelerConsole/ClDescGenerator.*` | Генератор |
| `Rdk/Core/Engine/UContainerDescription.*` | Load/Save Favorites |

---

## EN

DETAILED ClDesc means curated primary Favorites (`{CompName}:Prop`), rare high-value nested I/O aliases, and behavior-based Descriptions — not autogen stubs or Coord/Activity/Type dumps. See the RU sections for schema, checklist, and anti-patterns. Storage: `Bin/ClDesc/<Library>/ru-RU/<Class>.xml`.
