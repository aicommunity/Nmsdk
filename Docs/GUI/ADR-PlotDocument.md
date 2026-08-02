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

Инспектор `PlotSettingsSidePanel` **скрыт по умолчанию** (графики на всю ширину; `QSplitter` charts|inspector).

Три явных scope-страницы вместо смешанного «Panel»:

1. **Layout** — сетка вкладки (`gridRows`/`gridCols`) и `UpdateIntervalMs`.
2. **Chart** — активный `PlotPanel` (title, axes, viz, legend, track).
3. **Series** — серии активного chart.

Активный график задаётся кликом / combo в шапке / context menu; toolbar Layout/Chart/Series не сбрасывает выбор на chart 0. Hide и Esc закрывают инспектор.

## Test plan

- [x] Сборка `NeuroModeler` (linux-gcc-debug)
- [ ] Watch window: add TimeSeries, pan/box zoom/track/reset modebar
- [ ] Inspector hidden by default; Layout | Chart | Series pages; Hide/Esc
- [ ] Multi-chart grid: click + chrome; Chart/Series settings target active chart
- [ ] Multi-channel: series with `channel_index != 0` survives Interface.xml save/load
- [ ] XY: set viz XYLine, pick Y then X property; points accumulate
- [ ] Hover tooltip shows series binding + X/Y
- [ ] LLM: `add_watch_series`, `set_panel_viz_kind`, `set_series_binding`, MDI create/list
- [ ] Profiling (`UTableInfo`) opens without legacy Graph includes
