# Qt GUI UX — план оставшейся работы

**Дата:** 2026-10-02  
**База:** [Qt-GUI-UX-Audit-2026-10-02.ru.md](Qt-GUI-UX-Audit-2026-10-02.ru.md), [Qt-GUI-UX-Baseline-2026-10.md](Qt-GUI-UX-Baseline-2026-10.md)  
**Контекст:** P0/P1 Watch (layout, dense, inspector, Quick Add, DnD, templates, Undo) уже в коде; сборка `NeuroModeler` OK. Ниже — только то, чего ещё нет или что нельзя закрыть без GUI.

---

## 0. Что уже сделано (не повторять)

| Тема | Где в коде |
|------|------------|
| Layout ≠ composition, schema v3, PanelId/SerieId | `UWatchTab`, `PlotDocument` |
| Dense chrome + shared tool strip | `UWatchTab::m_sharedModeBar`, `UWatchChart::setDenseChrome` |
| Inspector: серии, Fixed Y/X, Sync X, Panel ↑/↓ | `PlotSettingsSidePanel` |
| Quick Add Y(t), DnD свойств | `UWatchQuickAddDialog`, `WatchPropertyDndPayload` |
| Watch templates `*.watch.xml` | `WatchTemplateStore`, меню Watch, `Bin/WatchTemplates/` |
| Undo panel/series | `PlotWatchUndoCommands` |
| Logger / channels toolbar / FitToView / workspace presets | соответствующие виджеты |

---

## 1. Приёмка на живом GUI (блокер DISPLAY) — P0 для выпуска

**Цель:** закрыть критерии §8 аудита числами и чеклистом, а не только кодом.

1. Прогнать smoke из baseline §2–4 и ADR-PlotDocument Test plan.
2. Сценарий P0: сетка `2×2 → 1×2 → 2×2` — те же PanelId, titles, series.
3. Dense `2×2` / `4×4`: одна общая полоса инструментов, нет per-cell modeBar.
4. Quick Add + DnD свойства → Y(t); Load template `2x1-overview.watch.xml`.
5. Delete panel / Hide series → Ctrl+Z.
6. Заполнить таблицу `plotArea_px / cell_px` для 1×1, 2×2, 4×4 × DPI 100/125/150% в baseline.
7. Window → Workspace: один раз **Capture factory layout**, затем Save/Apply Model/Monitoring/Debug.

**Критерий готовности:** все пункты отмечены `[x]` в baseline; нет регрессий по сохранению `Interface.xml`.

---

## 2. Watch — довести до «полноценного браузера панелей» — P1

Сейчас: combo + Expand + Panel ↑/↓. Не хватает:

1. Отдельный компактный **список панелей** (имя, тип, N series, online/offline) с поиском.
2. Переименование из списка (уже есть Title в inspector — связать с inline rename в списке).
3. **Перенос панели между вкладками** Watch (`UWatch` tab bar).
4. Двойной щелчок по элементу списка = activate + expand (частично есть на combo).

**Критерий:** любой график выбирается/переименовывается/прячется/дублируется/удаляется без клика по полотну; reorder внутри вкладки и между вкладками.

---

## 3. Quick Add — signal-first полировка — P2

1. Недавние и избранные свойства в `UWatchQuickAddDialog`.
2. Мультивыбор свойств + кнопка «Добавить в…» (выбор панели).
3. Компактный matrix preview уже в picker — проверить UX на матрицах в GUI.
4. Пресеты компонента (`WatchPresetCatalog`) как готовые действия на главном пути (не только в wizard).

**Критерий:** один обычный Y(t) из поиска/избранного ≤ 2 клика после выбора свойства.

---

## 4. Остальные виджеты — P2

| Область | Остаток |
|---------|---------|
| Дерево компонентов | Инкрементальный update ветви (без полного clear при тике значений); единицы/описание у свойства; Undo значения |
| Каналы | Обновление списка без полной очистки; статус/ошибки в строке |
| Лог | Переход к компоненту-источнику; лимит блоков + индикатор «N new» уже частично — добить |
| Диаграмма | Поиск/переход к узлу; видимый масштаб; фильтры связей |
| Workspaces | Зафиксировать factory layout в репозитории или при первом старте; индикатор открытых/закреплённых окон |

---

## 5. i18n / a11y / shortcuts — P2

1. Qt `.ts` / `.qm` (RU/EN) для Watch + inspector + logger + channels (см. `Rdk/GUI/Qt/i18n/README.md`).
2. Единый язык строк (убрать смесь EN action / RU tooltip там, где мешает).
3. Горячие клавиши: Quick Add, Layout, Focus search, каналы Start/Pause.
4. Tab order + accessible names на dense grid и inspector.
5. Контраст light/dark + disabled на новых контролах.

---

## 6. Perf / визуализация — по замерам — P2

1. Включить `BUILD_TESTING` и прогнать `Test_WatchTemplateStore`, `Test_PlotDecimation`.
2. Замерить latency/FPS на 1×1, 2×2, 4×4 с длинными рядами.
3. Coalesce обновлений UI при высокой частоте тика (если замер покажет дрожь).
4. Backend Charts менять **только** если dense + envelope не достигают целевых цифр.

---

## 7. Порядок работ (рекомендуемый)

```
A. §1 Live smoke + plotArea% + factory workspace   ← нужен DISPLAY
B. §2 Panel browser list + move between tabs
C. §3 Quick Add favorites / multi-add
D. §5 i18n skeleton + shortcuts
E. §4 tree/channels incremental + diagram polish
F. §6 tests + perf numbers
```

Не начинать B–F, пока A не даст хотя бы smoke «зелёный» на типичном проекте — иначе правки UX уйдут вслепую.

---

## 8. Файлы-точки входа

- Watch: `Rdk/GUI/Qt/UWatchTab.*`, `UWatchChart.*`, `UWatch.*`
- Inspector / templates: `Rdk/GUI/Qt/Plot/PlotSettingsSidePanel.*`, `WatchTemplateStore.*`
- DnD / Quick Add: `WatchPropertyDndPayload.*`, `UWatchQuickAddDialog.*`
- Главное окно: `UGEngineControlWidget.*` (workspaces)
- Документация: этот файл, baseline, `Docs/GUI/ADR-PlotDocument.md`
