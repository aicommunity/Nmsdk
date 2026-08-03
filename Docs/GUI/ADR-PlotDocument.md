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

GUI «Add series…» открывает `UWatchSeriesWizard` (не цепочку modal dialogs):

1. **Type** — `VizKind` + form выборки матрицы (cell / multi / row / column).
2. **Sources** — old `UComponentsListWidget` (дерево всегда видно, `setWatchablePropertiesOnly`) + inline `UWatchMatrixSelector`; для XY — Y и X на одной странице.
3. **Style** (опционально) — name / color / Y shift; Finish доступен уже со страницы Sources.

Commit через существующие `createSerie` / `createSerieXY`. Общий type-gate: `RDK::isWatchableLanguageType` (`Core/Math/UWatchablePropertyTypes.h`), зеркало `NMSDK::Plot::isWatchableLanguageType`.

## Test plan

- [x] Сборка `NeuroModeler` (linux-gcc-debug)
- [ ] Watch window: add TimeSeries, pan/box zoom/track/reset modebar
- [ ] Inspector: Chart|Series side panel with hero identity; live apply; Hide/Esc
- [ ] Layout toolbar → Tab layout dialog (presets + interval); charts stay full width
- [ ] Multi-chart grid: click + chrome; Chart/Series settings target active chart
- [ ] Add series wizard: Type → Sources (+ matrix) → optional Style; XY Y+X one page
- [ ] Multi-channel: series with `channel_index != 0` survives Interface.xml save/load
- [ ] XY: set viz XYLine, pick Y then X property; points accumulate
- [ ] Hover tooltip shows series binding + X/Y
- [ ] LLM: `add_watch_series`, `set_panel_viz_kind`, `set_series_binding`, MDI create/list
- [ ] Profiling (`UTableInfo`) opens without legacy Graph includes
