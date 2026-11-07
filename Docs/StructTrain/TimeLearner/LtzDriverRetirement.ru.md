# Исторические LTZ drivers: отдельная группа миграции

Из candidate Bin удалены16 файлов:15 campaign shell drivers/shared cold helper
иverify_regression.py. Archive commit `fc67a3b0958e8becdfbe1cd3f0e4e054d966d54f`,
candidate `10efba4162729d2fa49fed86747c8fea158cb0aa`. Все пути, last-change SHA,
blob SHA1, SHA256, bytes и retrieval command записаны в script_migration.json
и [точной постановке](LtzDriverRetirement.preparation.json). Wrappers/копий
исторических исполнителей на старых местах не оставлено.

Два copy helpers исключены: SelectivityBranch/phase8_tiprmin_gate.py и
scripts/phase12_wave3.py ещё вызывают их. Их перенос входит в последующую
миграцию зависимой группы. Python analyses/patchers этого каталога отдельно
остаются на review. Literal search текущих committed executable trees
Root/Bin/Pulse не нашёл внешних callers выбранных16 файлов. Computed paths
и внешние непроиндексированные пользователи этим не исключаются.

Снимаемые drivers привязаны к старым campaign layouts, общему Bin/Platform,
ручным XML overlays/cold/warm copying и offline threshold/separability tools.
Они не являются новым production pipeline. Например run_regression.sh допускает
nonzero Console exit при существующем results.csv; такой CSV не доказывает
корректного завершения. Новые задания используют корневой пакет, полную модель,
explicit provenance и раздельные execution/validity/training/evaluation axes.
Это не утверждение численной эквивалентности всех старых LTZ сценариев.

Configs/models/CSV/traces и тела исторических научных отчётов не удаляются и
не пересчитываются. Добавлен только navigation notice в README каталога.
Сохранённые в истории научные наблюдения не оцениваются задним числом по
новым критериям. Migration manifest содержит238 records:236 retired+2 moved,
complete=false. Группа16 ещё требует metadata/API проверки retrieval/absence
на двух серверах; native эксперименты и scientific verdict здесь не заявлены.

В новой локальной Bin linked worktree обнаружена унаследованная относительная
core.worktree привязка. Перед продолжением она заменена отдельной абсолютной
worktree настройкой;16 затронутых чистых копий восстановлены по исходному Git.
Оригинальная пользовательская Bin worktree осталась clean. Итоговый staged
scope проверен: ровно16 удалений scripts иодин README, без data/config edits.
