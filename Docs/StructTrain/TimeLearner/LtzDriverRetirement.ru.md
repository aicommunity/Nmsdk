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
complete=false. Группа16 принята после metadata/API проверки retrieval/absence
на двух серверах; native эксперименты и scientific verdict здесь не заявлены.

В новой локальной Bin linked worktree обнаружена унаследованная относительная
core.worktree привязка. Перед продолжением она заменена отдельной абсолютной
worktree настройкой;16 затронутых чистых копий восстановлены по исходному Git.
Оригинальная пользовательская Bin worktree осталась clean. Итоговый staged
scope проверен: ровно16 удалений scripts иодин README, без data/config edits.


## Приёмка группы

Production CLI history verify-migration проверил все238 records на Elder иM40,
включая16 новых. Версии исходников Root
`66f6504eb44922bcc9fb7361d9c73cce319c201e`, Bin
`10efba4162729d2fa49fed86747c8fea158cb0aa`. Обе проверки закрыты и leases released.
Evidence Elder `7cad641cd6d99fd849b2478528693e2662bd7b76`, M40
`cc26639d41012c4e37b9dc4f0e89274badb644e5`; compressed primary145348/145372 bytes,
по17 members. На каждом сервере отрицательный контроль восстановленного старого
пути получил отказ migration_old_path_still_present и не создал положительный
receipt. Старые исполнители не материализовались и не запускались.

[Независимая сверка](LtzDriverRetirementVerification.json) проверила оба архива,
точное множество238 записей, все238 архивных содержимых напрямую из локального
Git и288 actual tool hashes каждого worker. Scope Bin точно16D+1A; остальные
blobs идентичны. Code/native trees Root не менялись. Это production history/API
проверка, а не численное воспроизведение старых кампаний. Два оставшихся copy
helpers и17 Python analyses/patchers ещё требуют миграции зависимых групп.

Bin merge в develop: `b4f66eb137d3e1c19539890dbdee06faa3e1020b`, tree равен
проверенному candidate. Корневой gitlink фиксирует именно опубликованный merge.
Stage9 в целом не завершён; manifest.complete=false сохранён.
