# Qt GUI UX — baseline (2026-10)

**Дата:** 2026-10-02  
**Среда:** Linux, NeuroModeler собран (`Bin/Platform/Linux/NeuroModeler`), `DISPLAY` в сессии аудита отсутствовал — живые скриншоты/DPI-замеры отложены; ниже — кодовая базовая линия и чеклисты.

## 1. Code-derived layout chrome (до Stage 2)

| Сетка | Per-cell modeBar | Title/legend default | Источник |
|-------|------------------|----------------------|----------|
| 1×1 | 1× (Pan/Box/Track/Reset; Expand hidden) | ON / ON | `UWatchChart` ctor |
| 2×2 | 4× toolbars | ON / ON | то же + `updateExpandActionsVisibility` |
| 4×4 | 16× toolbars | ON / ON | то же |

Оценка доли plotArea (без DISPLAY): при типичной ячейке ~400×250 px toolbar (~28 px) + title/legend Qt Charts съедают заметную долю; целевой прирост после Dense — измерить на GUI (100/125/150% DPI) и дописать сюда числа.

**TODO (live GUI):** заполнить таблицу `plotArea_px / cell_px` для 1×1, 2×2, 4×4 × DPI.

## 2. Smoke / ADR checklist (ручной прогон на GUI)

См. также [ADR-PlotDocument.md](../GUI/ADR-PlotDocument.md) Test plan.

- [ ] Add TimeSeries, pan / box zoom / track / reset
- [ ] Reverse box zoom resets viewport
- [ ] X range 5/10 s
- [ ] Grid expand: double-click / Esc / Restore
- [ ] Save chart / Save all / Quick save
- [ ] Inspector Chart|Series; Hide/Esc
- [ ] Layout dialog presets; charts full width
- [ ] Multi-chart: click selects active; settings target active
- [ ] Add series wizard Manual + Preset paths
- [ ] Multi-channel series survives Interface.xml
- [ ] XY scalar + row/col; TS+XY blocked on same chart
- [ ] **P0:** 2×2 → 1×2 → 2×2 preserves panel ids, titles, series (после Stage 1)

## 3. Interface.xml round-trip checklist

1. Открыть проект со старым Watch (`schemaVersion` отсутствует или 1/2).
2. Load → не терять серии/каналы/оси.
3. Save → появляется `schemaVersion` (целевой v3 после Stage 1), атрибуты `PanelId` / `SerieId` / `PanelVisible`.
4. Reload → те же id и состав панелей.
5. Смена сетки в Layout dialog без потери панелей (overflow/hidden, не delete).

## 4. Сценарии аудита §7

1. Добавить один сигнал (до Stage 4 — wizard; после — Quick Add).
2. Собрать панель из группы сигналов.
3. Сравнить несколько каналов.
4. Выделить участок (box zoom) и Reset / Track.

## 6. Implementation status (2026-10-02 code pass)

Сборка `NeuroModeler` / `NeuroModelerConsole` после доработок: OK.

| Stage | Статус в коде |
|-------|----------------|
| 0 Baseline doc | [`Qt-GUI-UX-Baseline-2026-10.md`](Qt-GUI-UX-Baseline-2026-10.md) — live DPI/plotArea% ждут DISPLAY |
| 1 Layout integrity | schema v3, PanelId/SerieId, non-destructive `createGridLayout`, overflow revive |
| 1 Browser / undo | panel combo + Panel ↑/↓; Undo для panel delete и hide/show/delete/dup/reorder series |
| 2 Dense | `setDenseChrome` / Dense checkbox, shared margins, layout presets overview/dense |
| 3 Inspector | series ops, Fixed Y/X range toggles, Y shift double, Sync X, Reset/Auto-scale |
| 4 Quick add | `UWatchQuickAddDialog` + DnD; **Watch templates** `*.watch.xml` (Save/Load) |
| 5 Rest | logger/channels/FitToView; property filter; Window → Workspace layout |
| 6 Perf | envelope in adapter + `AUpdateInterface` |

### 7. Сверка с аудитом §4–8 (2026-10-02, после шаблонов)

| Критерий аудита | Статус |
|-----------------|--------|
| §4.1 P0 layout ≠ composition, schema v3 | **Done** |
| §4.2 panel browser / reorder | **Mostly** — combo + Panel ↑/↓ + Expand; нет переноса между вкладками Watch |
| §4.3 dense grid, shared toolbar | **Done** |
| §4.4 inspector Auto/Fixed | **Done** — Fixed Y / Fixed X (XY) + gated min/max |
| §4.5 quick add, DnD, watch templates | **Done** — Quick Add + DnD + `WatchTemplateStore` (`Bin/WatchTemplates/`, project `WatchTemplates/`) |
| §4.6 series ops, decimation | **Done** + Undo для series mutations |
| §5 workspaces | **Partial** — QSettings presets; factory capture вручную |
| §5 property search | **Partial** — фильтр properties; нет инкрементального rebuild |
| §5 i18n/a11y | **Open** — нет `.ts/.qm` |
| §8 acceptance (live) | **Code-ready**; smoke/DPI — нужен DISPLAY |

Live GUI smoke из §2–4 этого файла всё ещё нужно прогнать на машине с DISPLAY.

