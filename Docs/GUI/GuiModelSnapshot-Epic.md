# GuiModelSnapshot — performance epic (deferred)

## RU

Крупный эпик производительности Qt GUI (исторический план: [Reports/GUI-Qt-ImprovementPlan.md](../../Reports/GUI-Qt-ImprovementPlan.md)).

**Статус:** задокументирован как отдельный эпик после Component GUI migration; **не входит** в закрытие TD-008…TD-011.

### Цель

Заменить полный rebuild `QTreeWidget` на каждом тике (`UComponentsListWidget::AUpdateInterface`) на версионированный immutable snapshot модели + точечные diff-обновления.

### Основные блоки

1. События ядра: `ComponentAdded/Removed`, `PropertyChanged`, `PropertyClassChanged`
2. `GuiModelSnapshot` + `SnapshotBus` в GUI-процессе
3. `QTreeView` + `QAbstractItemModel` вместо `QTreeWidget`
4. Batch replot / кольцевые буферы для графиков

### Триггер старта

Профильные замеры `AUpdateInterface` на больших сетях или отдельный product sprint после стабилизации native dock / tab-host.

---

## EN

Large Qt GUI performance epic (historical plan: [Reports/GUI-Qt-ImprovementPlan.md](../../Reports/GUI-Qt-ImprovementPlan.md)).

**Status:** documented as a separate epic after Component GUI migration; **out of scope** for closing TD-008…TD-011.

### Goal

Replace full `QTreeWidget` rebuilds each tick with a versioned immutable model snapshot and incremental diffs.

### Start trigger

Profile evidence on large nets, or a dedicated product sprint after native dock / tab-host stabilization.
