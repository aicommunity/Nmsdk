# Исторические запускатели внутри Reports: удаление из текущего дерева

Адресный подэтап9/12. Удалены13 исполняемых файлов из Reports без wrappers и
копий. Общий перенос скриптов, production runner и исходные этапы0–12 этим не
завершены. Изменения не затрагивают код learner, физику, конфиги, модели,
исходные CSV, метрики или прежние verdict.

## Исходный снимок и назначение

Полный root retrieval snapshot: `3bfb72a1fbe7712796e65bea59db343d507d48f4`.
Это снимок извлечения инструмента, а не утверждение о runtime source каждого
исторического задания. Все13 записей имеют точный path, полный commit,
last-change commit, blob SHA1, content SHA256, размер и команду git show в
[script_migration.json](script_migration.json).

| Каталоги Reports/StructTrain/TimeLearner | Файлы | Историческая функция |
|---|---|---|
| s03-inherited-review-selection-{normal,asan}-a{1,2} | 4 job.py | Фиксированные checkout/build/report-selection/publication задания проверки inherited properties. Producer квитанции и выборки рисунков, не реализация физики. |
| s05-repeat-boundary-baseline-{elder1,m40}-a1 | 2 runner.sh | Построение старого выделенного runtime и выполнение baseline boundary tests по фиксированным путям. |
| s07-n0-closure-m40-a1 | 1 runner.sh | Одноразовая проверка recursive checkout согласованного develop. |
| s07-n0-combined-{elder1,m40}-a3/a{1,2,3} | 6 runner.sh | Попытки агрегированной validation/report проверки старых N0 fixtures с конкретными environment bindings; ранние ошибки сохранены в их результатах. |

В production корневом пакете нет буквальных references на эти13 полных старых
путей. Их тела привязаны к прежним workspace/readback/runtime. Они не считаются
новыми универсальными командами или декларативными job specs. Полный перенос
активных tools из Docs/Bin и устранение временных внешних orchestration helpers
остаются открытыми.

## Исторические отчёты и контрольные суммы

В девять отчётных каталогов добавлена оговорка с immutable retrieval commit.
Текущие directory SHA256SUMS.json исключают только удалённые launcher entries
и учитывают обновлённый README. Исходные manifests доступны в том же commit.
Хэши остальных payload entries не изменяются, данные и прежняя интерпретация
измерений не переписываются. Прежние научные критерии этим не подтверждаются.

## Требуемая приёмка

Manifest теперь содержит94 records:92 retired и2 moved, complete=false.
До merge нужны production history verify-migration на обоих workers:

1. Точные commits/blobs/размеры/SHA256 всех94 записей извлекаются из Git.
2. Старые пути отсутствуют в согласованном root/child tree; moved replacements
   существуют в корневом пакете.
3. Отрицательный Git fixture, возвращающий один из13 launcher blobs на прежний
   путь, отклоняется с migration_old_path_still_present без положительной квитанции.
4. Diff ограничен manifest, документацией,13 удалениями и соответствующими
   directory checksums; все прочие payload blobs совпадают с исходным снимком.
5. Активные numerical sources/builds/runtimes не меняются. Проверка выполняется
   из отдельных Git objects и source copy корневого Python-пакета.

Локальная статическая сверка и подготовка manifest не заменяют эту серверную
приёмку. Runtime/scientific equivalence исторических launchers не заявляется.


## Проверка на двух workers

Проверенный source root9b07a7714b00e93e7dc37894ba41a329de353d49.
Elder evidence27f98de68f4a1ffb179ac270be372e70de95db0d (10 members/37771 bytes),
M40 evidence10a48a8c0313bc16d62a010757f11d5042819c77 (10 members/37751 bytes).
Оба прошли production CLI94 records и negative restored-job fixture (exit2,
migration_old_path_still_present, положительный receipt отсутствует).
Их архивы, outer/member checksums и380 точных Git source hashes независимо
проверены локально. Source inventories обоих workers совпали. Проверка diff
ограничила изменения указанными13 launchers, manifest, оговорками и checksum
индексами; остальные payload blobs и checksum values сохранены.
Это адресная приёмка данного удаления; whole_migration_attested=false.
