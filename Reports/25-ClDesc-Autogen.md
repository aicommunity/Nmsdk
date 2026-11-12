# 25. Автогенерация ClDesc

## Цель

Создать повторяемый процесс получения XML-описаний всех компонентов, загруженных в `UStorage`, чтобы убрать ручную работу по поддержке `Bin/ClDesc`.

## Что сделано

- В `NeuroModelerConsole` добавлен ключ `--generate-cldesc`, который:
  - подготавливает пути к `Bin/ClDesc` и `Bin/RTlibs`;
  - получает блокировку `UStorage` и проходит по каждому зарегистрированному классу;
  - создаёт/обновляет `UContainerDescription`, заполняет заголовки и описания свойств;
  - сохраняет XML в правильную папку библиотеки и выводит статистику.
- Добавлен модуль `ClDescGenerator` с эвристиками разбиения имён и локализацией на русский язык.
- Сформирован словарь `Docs/ClDescLexicon.json`, содержащий переводы токенов и точечные overrides (например, для `NDCEngine`, `NPulseNeuron`, `NActuatorSignals`).
- Инструкции по запуску: этот отчёт + [Docs/PropertyAliasGeneration.md](../Docs/PropertyAliasGeneration.md) + [Docs/ClDesc-Detailed-Methodology.md](../Docs/ClDesc-Detailed-Methodology.md).

## Как использовать

1. Соберите `NeuroModelerConsole` (через CMake или qmake).
2. Запустите генерацию:
   ```
   Bin/Platform/Linux/NeuroModelerConsole --generate-cldesc \
       --cldesc-lexicon Docs/ClDescLexicon.json
   ```
3. По окончании генератор выведет статистику (количество новых/обновлённых описаний и разбивку по библиотекам). Готовые XML находятся в `Bin/ClDesc/<Library>/ru-RU/<Class>.xml`.
4. При необходимости измените словарь и повторите запуск — **тексты** могут обновиться; Favorites aliases мержатся поверх существующих.

### Что делает генератор

- Загружает библиотеки через `RdkLoadPredefinedLibraries()`.
- Для каждого класса из `UStorage` вызывает `UContainerDescription::CreateProperties()`, чтобы зафиксировать актуальный набор свойств.
- Строит заголовки и описания на русском (разбиение CamelCase, перевод токенов, шаблоны фраз).
- Для `UNet` с вложенностью пишет **nested aliases** в `<Favorites>` (не curated primary).
- Пишет результат в `Bin/ClDesc`, сохраняя структуру `<Library>/ru-RU/`.

### Favorites ≠ DETAILED

Автоген — уровень **Autogen** (каркас). Уровень **DETAILED** (primary Favorites `{CompName}:Prop`, отфильтрованные aliases, смысловые Description) — ручная/агентная курация по [ClDesc-Detailed-Methodology.md](../Docs/ClDesc-Detailed-Methodology.md).

Не запускать массовый `--cldesc-force` после курации Favorites без политики сохранения. Autogen часто добавляет шум (`Coord`/`Activity`/`Type`) и **не** создаёт top-level primary Favorites.

Эталон схемы: [Bin/Docs/Examples/ClDesc-Example.md](../Bin/Docs/Examples/ClDesc-Example.md).

### Настройка словаря

Файл `Docs/ClDescLexicon.json` содержит четыре секции:

| Секция | Назначение |
| --- | --- |
| `tokens` | Переводы отдельных токенов (например, `Pulse -> "импульсный"`). |
| `classOverrides` | Готовые заголовки/описания для конкретных классов. |
| `propertyOverrides` | Точечные тексты для свойств внутри определённого класса. |
| `propertyFallbacks` | Глобальные шаблоны для свойств с одинаковыми именами. |

Пример override’а:

```json
"NDCEngine": {
  "header": "Модель двигателя постоянного тока",
  "description": "..."
}
```

После правок словаря достаточно снова выполнить `--generate-cldesc` (без `-F` на уже DETAILED Favorites), чтобы обновить тексты свойств/классов.

## Дальнейшие улучшения

- Фильтр технических leaf-имён в `PropertyAliasAnalyzer` / опция не трогать Favorites при наличии direct — **сделано** (см. `Docs/PropertyAliasConfig.json`).
- Добавить поддержку английской локализации.
- Интегрировать проверку CI, чтобы гарантировать актуальность `Bin/ClDesc`.
- Расширить словарь библиотек CV/Hardware дополнительными overrides, если появятся новые компоненты.
