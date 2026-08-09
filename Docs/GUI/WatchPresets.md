# Watch visualization presets

Каталог человекочитаемых JSON-пресетов для мастера **Add series** (режим **Preset**).

## Расположение

| Что | Путь |
|-----|------|
| Каталог продукта | `Bin/WatchPresets/<Library>/<ClassName>.json` |
| Композиция / семьи | `Bin/WatchPresets/composition.json` |
| Черновики майнера | `Bin/WatchPresets/draft/` (runtime **не** загружает) |
| Отчёты | `Bin/WatchPresets/meta/` (`mining-report`, `coverage`) |
| Непривязанные классы | `Bin/WatchPresets/Unassigned/` (загружается) |
| Майнер / тесты | `Scripts/WatchPresets/` |

INI:

```ini
[General]
WatchPresetsPath=../../WatchPresets/
```

## Наследование (composition + families)

`WatchPresetCatalog::presetsForClass` возвращает:

1. **Own** — JSON выбранного класса.
2. **Inherited** — пресеты детей из `composition.json` (`parents` / `membraneChildren`) с rewrite `path` (`""` → `LTZone`, …). Id: `inherited:<slot>:<id>`.
3. **Family** — own-пресеты sibling-классов одной роли (`ltzone`, `synapse`, …). Id: `family:<Sibling>:<id>`.

Resolve: `GetComponentL` + property exists + `isWatchableLanguageType`; при ошибке — полный reject.

Пример: выбран `NPNeuron` → виден `NPLTZone.Output` как `LTZone.Output`.

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
      "vizKind": "TimeSeries",
      "series": [
        { "path": "LTZone", "property": "Output", "jx": 0, "jy": 0 },
        { "path": "Soma1", "property": "SomaSumPotential", "jx": 0, "jy": 0 }
      ]
    }
  ]
}
```

Ключ — класс **выбранного** экземпляра. Nested path относительно него.

## Wizard

Manual | Preset → Component (class only) → Preset list (own+inherited+family) → Style → `createSerie`.

## Майнинг и покрытие

```bash
python3 Scripts/WatchPresets/mine_watch_presets.py \
  --configs Bin/Configs --cldesc Bin/ClDesc --out Bin/WatchPresets \
  --min-hits 3 --min-hits-internal 2

python3 Scripts/WatchPresets/promote_drafts.py \
  --out Bin/WatchPresets --cldesc Bin/ClDesc --min-hits 1

python3 Scripts/WatchPresets/check_coverage.py \
  --out Bin/WatchPresets --min-hit-coverage 0.95

python3 -m unittest Scripts/WatchPresets/tests/test_parsers.py
```

Slot-роли (`LTZone`, `Dendrite1_1.ExcChannel`, …) нормализуют instance-paths при агрегации. Coverage считает только серии с именованным property (numeric-only BCB unmatched исключены).

Цель: ≥95% hit-coverage; own JSON для всех `yClass` с ≥5 named hits.

## Связь с ClDesc

Convention + Favorites paths; без новых XML-тегов. См. [ADR-PlotDocument.md](ADR-PlotDocument.md).
