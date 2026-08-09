# ADR: PlotDocument — канон графиков Qt GUI

**Status:** Accepted  
**Date:** 2026-08-02

## Context

В Qt GUI существовали два стека графиков: **UWatch + Qt Charts** (активный, MDI, LLM tools) и **UGraphWidget + QCustomPlot** (отключён в UI). Параметры серий и осей были размазаны по виджетам, XML и диалогам; канал расчёта терялся при load; источники данных — только Y(t).

## Decision

1. **Канон UI** = `UWatch` / `UWatchTab` / `UWatchChart` / `UWatchSerie` на Qt Charts.
2. **Legacy** UGraph + QCustomPlot + stubs (`UWatchFormWidget`, `UWatchSettingsDialog`) **удалены** из runtime и сборки.
3. **Единая модель** `PlotDocument` / `PlotPanel` / `PlotSeries` / `DataBinding` — источник правды для GUI, `Interface.xml` и LLM watch tools.
4. **Viz roadmap:** TimeSeries → XY (PropertyPair, same-tick) → Heatmap / Histogram.
5. Рендер v1–v3: **Qt Charts**; альтернативы (Qwt/QtGraphs) — только если heatmap упрётся в лимиты.

## Contracts

### XML (`Interface.xml`)

- v1 (без `schemaVersion`): прежний layout `graph_N` / `serie_N`.
- v2+: `schemaVersion`, `VizKind`, `SerieChannel`; X-role по умолчанию Time.

### LLM tools (host `llmWatch*`)

- `add/list/remove/clear_watch_series`
- `list/create/focus/close_watch_mdi`
- Расширения: `set_series_binding`, `set_panel_viz_kind` на той же DTO.

## Consequences

- Один стек в UI; меньше бинарного размера (нет ~23k LOC QCP).
- Миграция XML на save; load v1 остаётся совместимым.
- BCB TeeChart (`TUWatchInfo` X+Y sources) — только референс для DataBinding, не порт.

### UX инспектора (Watch settings)

Разделение scope:

1. **Tab layout** — отдельный modal `UWatchLayoutDialog` (пресеты сетки + Custom, preview, `UpdateIntervalMs`). Toolbar **Layout** открывает только этот диалог; side panel не затрагивается.
2. **Chart / Series** — `PlotSettingsSidePanel` в `QSplitter` (скрыт по умолчанию): hero «Chart N · title», combo активного графика, вкладки только Chart | Series. Live apply (без Apply-кнопок); формы в `QGroupBox` (Identity / Axes / Display; список серий + Selected series). Ширина ~320–420 px. Hide и Esc закрывают инспектор.

Активный график задаётся кликом / combo в шапке / context menu; Chart/Series toolbar не сбрасывает выбор на chart 0.

### Add series wizard

GUI «Add series…» открывает `UWatchSeriesWizard`:

1. **Type** — режим **Manual** | **Preset** (default Manual). Manual: `VizKind` + form (TS: cell/multi/row/column → N серий; XY: cell pair **или** row/column snapshot curve). Preset: Kind/Form скрыты → страницы компонента и выбора пресета.
2. **Sources (Manual)** — TS: **Y**; XY: **X → Y** (отдельные страницы).
3. **Preset** — компонент (class via `componentClassNameFromModelScope`) → пресет из `Bin/WatchPresets/` → Style. Resolve: `WatchPresetCatalog` + `GetComponentL`; без частичного apply.
4. **Style** — scrollable; name/color/shift (в Preset name prefill от title); ClDescr → X/Y min/max; для scalar XY Sampling (max points / min interval / min distance).

Каталог пресетов: [WatchPresets.md](WatchPresets.md).

Семейства на одном chart **взаимоисключающие**: TimeSeries vs Y(x) (`XYLine`/`XYScatter`/matrix-slice). Внутри Y(x) Line+Scatter+slice можно смешивать.

XY chart axes: `AxisXmin`/`AxisXmax` + `AxisYmin`/`AxisYmax` (inspector скрывает time `X range` / Track). Scalar XY readers: `SetTimeInterval(0)`. Matrix row/col XY: snapshot zip `min(nx,ny)` каждый тик (`SliceKind` в XML `SerieXSlice`/`SerieYSlice`).

TS default `AxisXrange` = **5** с; смена X range через `updateTimeIntervals` (только `axisXrange` + `SetTimeInterval(W)` на TS-ридерах; ось не двигает).

### Инвариант окна TimeSeries

`W = axisXrange = reader.TimeInterval` (секунды model time):

1. **Reader** — единственный owner истории (`TimeInterval` + `NumPoints`). `NumPoints` ≥ ~`2·W·Hz` (RT может давать плотнее 1 сэмпла/шаг); при упирании в cap до заполнения окна `AUpdate` наращивает буфер по наблюдаемой частоте.
2. **Display** (`sampleTimeSeries`) — pass-through ридера; decimation только для отрисовки (endpoints сохраняются). Не trim’ить историю по `windowSize`/`TimeInterval`.
3. **Track** (если trackable и не zoomed):  
   `lo=oldest`, `hi=latest`; если `hi-lo < W` → `hi = lo+W`; если `hi-lo > W` → `lo = hi-W`; затем **атомарно** `axis.setRange(lo, hi)`.

XY не трогаем: `SetTimeInterval(0)`, свой Track/extents.

Box Zoom: reverse ROI сбрасывает зум; rubber band только в Box Zoom.

### Grid expand и экспорт

- Сетка (`countGraphs()>1`): double-click по chart / кнопка **Expand** на modeBar — скрыть соседей (без пересоздания layout); **Esc** или **Restore** — вернуть сетку и размеры splitters.
- Экспорт: toolbar **Save chart…** / **Save all…** / **Quick save**; форматы PNG/SVG/JPEG. Quick save пишет в `<ProjectPath>/SavedWatches/<yyyy-MM-dd_HH-mm-ss>/` (сессионная папка до перезапуска вкладки/окна).

Commit через `createSerie` / `createSerieXY`. Type-gate: `RDK::isWatchableLanguageType`.
TS matrix resize: фиксированные jx/jy — при уменьшении матрицы серия уходит offline; новые ячейки не появляются сами (пересоздать серии).

## Test plan

- [x] Сборка `NeuroModeler` (linux-gcc-debug)
- [ ] Watch window: add TimeSeries, pan/box zoom/track/reset modebar
- [ ] Reverse box zoom resets viewport (+ Track)
- [ ] X range 5/10 s matches visible TS window (not stuck at 2 s)
- [ ] Grid expand: double-click / Esc / Restore
- [ ] Save chart / Save all / Quick save → `SavedWatches/`
- [ ] Inspector: Chart|Series side panel with hero identity; live apply; Hide/Esc
- [ ] Layout toolbar → Tab layout dialog (presets + interval); charts stay full width
- [ ] Multi-chart grid: click + chrome; Chart/Series settings target active chart
- [ ] Add series wizard: Manual Type → X→Y (XY) or Y (TS) → Style; Preset → Component → Select → Style; ClDesc axis limits
- [ ] Watch presets: LIF root (`NPulseNeuronIaF` spikes+soma); leaf `NPulseLTZoneIaF`; `NPGenerator`
- [ ] Multi-channel: series with `channel_index != 0` survives Interface.xml save/load
- [ ] XY: scalar pair; XY row/col snapshot curve; Line+Scatter mix OK; TS+XY blocked on same chart
- [ ] Hover tooltip shows series binding + X/Y
- [ ] LLM: `add_watch_series`, `set_panel_viz_kind`, `set_series_binding`, MDI create/list
- [ ] Profiling (`UTableInfo`) opens without legacy Graph includes
