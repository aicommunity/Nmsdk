# Watch visualization presets

Каталог человекочитаемых JSON-пресетов для мастера **Add series** (режим **Preset**).

## Расположение

| Что | Путь |
|-----|------|
| Каталог продукта | `Bin/WatchPresets/<Library>/<ClassName>.json` |
| Черновики майнера | `Bin/WatchPresets/draft/` (runtime **не** загружает) |
| Отчёт майнера | `Bin/WatchPresets/meta/` (runtime **не** загружает) |
| Непривязанные классы | `Bin/WatchPresets/Unassigned/` (загружается) |
| Майнер / тесты | `Scripts/WatchPresets/` |

INI (`Project.ini` / settings):

```ini
[General]
WatchPresetsPath=../../WatchPresets/
```

По умолчанию — соседняя папка с `ClDescPath`. Runtime: `UApplication::GetWatchPresetsPath()` → `WatchPresetCatalog`.

## Схема JSON (`schemaVersion: 1`)

```json
{
  "schemaVersion": 1,
  "library": "PulseLibrary",
  "className": "NPulseNeuronIaF",
  "presets": [
    {
      "id": "spikes_and_soma",
      "title": "Spikes + soma potential",
      "description": "…",
      "vizKind": "TimeSeries",
      "series": [
        { "path": "LTZone", "property": "Output", "jx": 0, "jy": 0 },
        { "path": "Soma1", "property": "SomaSumPotential", "jx": 0, "jy": 0 }
      ]
    }
  ]
}
```

- Ключ пресета — **класс выбранного экземпляра** (не родителя).
- `path: ""` — свойство самого выбранного компонента.
- `path: "LTZone"` → `rootLongName + ".LTZone"`.
- `vizKind`: `TimeSeries` | `XYLine` | `XYScatter`.
- Наследование пресетов родителя в v1 **не** делается.

## Wizard (Manual | Preset)

`UWatchSeriesWizard`:

1. **Type** — Manual (как раньше: Kind + Source form) или Preset.
2. **Preset → Component** — выбор экземпляра; class через `componentClassNameFromModelScope`. Property **не** обязателен.
3. **Preset → Select** — список `presetsForClass`; preview серий; resolve через `GetComponentL`.
4. **Style** — имя prefill от `title`; цвет / shift.
5. **Apply** — цикл `createSerie` / `createSerieXY`; при ошибке resolve — без частичного набора.

Семейство графика (TS vs XY) блокируется так же, как в Manual.

Код: `Rdk/GUI/Qt/Plot/WatchPresetCatalog.*`, `UWatchSeriesWizard.*`.

## Майнинг из конфигов

```bash
python3 Scripts/WatchPresets/mine_watch_presets.py \
  --configs Bin/Configs \
  --cldesc Bin/ClDesc \
  --out Bin/WatchPresets \
  --min-hits 3

python3 -m unittest Scripts/WatchPresets/tests/test_parsers.py
```

Парсеры: BCB `UWatchForm` / `UWatchFrame_*`, Qt v1 `serie_*`, Qt v2 role fields, MDI `Watches_*`; class map из `Model_*.xml` и legacy `model.xml`.

Курация: правки в `Bin/WatchPresets/<Lib>/` (submodule `Nmsdk-Bin`); `draft/` в продукт не коммитить как «истину».

## Связь с ClDesc

Convention + docs; **без** новых XML-тегов ClDesc в первом релизе.

См. также [ADR-PlotDocument.md](ADR-PlotDocument.md) (Add series wizard).
