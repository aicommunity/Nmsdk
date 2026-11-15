# Вывод исторических AsymRm seed/reset инструментов

Отдельная группа этапа9: четыре инструмента из Bin
`Configs/SpikeSamples/StructTrain/SelectivityAsymRm/scripts/`:

| Файл | Историческая операция |
|---|---|
| seed_initial_from_ltzcal.py | Выбор Initial/TipR из соседнего LtzCal Train/Test |
| seed_from_done_preinh.py | Частичный перенос preinh→gen, включая surgical overlay |
| seed_tipr_from_done_sibling.py | Частичный перенос PackB→C, ранее superseded |
| reset_pathological_tip.py | Неуспешная историческая гипотеза H1, замена TipR эвристикой |

Последние три импортируют XML-helpers первого. Других исполняемых потребителей
группы не обнаружено в проверенном Git tree. Общий `asymrm_train_common.py`
и остальные18 AsymRm Python-файлов сохраняются до отдельного разбора.

Исходники извлекаются из Bin commit
`b4f66eb137d3e1c19539890dbdee06faa3e1020b`. Для каждого в
[script_migration.json](script_migration.json) записаны полный old_path,
archive commit, blob SHA1, content SHA256, размер и команда git show.
Четыре файла удалены из текущего feature-дерева без wrappers и копий.
Исторические отчёты получили pinned Git-ссылки; измерения, конфиги и модели
не изменяются. Локальная пользовательская копия Bin не переключалась.

Современный полный native import/export заменяет процесс подстановки нескольких
parent-векторов. Это не обещание математической эквивалентности хирургическому
seeding. Legacy-критерий Need=0 не повышается до доказательства сходимости.
Серия D и исторические задания не запускаются заново.

Manifest содержит242 записи:240 retired и2 moved. Полная миграция по-прежнему
`complete=false`. Предыдущая приёмка238 записей не подтверждает автоматически
эти четыре: требуется production verify_migration на обоих серверах с точным
Git object closure всех242 archive/path записей и отрицательным контролем,
который возвращает один удалённый путь в диагностическое Git tree.

Адресная приёмка выполнена на M40 и Elder. Production CLI на каждом worker
проверил все242 записи, затем отказал для диагностического дерева с одним
восстановленным старым путём: exit2, `migration_old_path_still_present`,
положительная квитанция не создана. Диагностический скрипт не материализовался
и не исполнялся. Подтверждён exact scope Bin4D+4M и отсутствие изменений
других Bin blobs; root native/code trees сохранены. Группы закрыты, leases released.

[Независимая сверка](AsymRmSeedRetirementVerification.json) проверяет68 archive
members, все242 manifest bindings и403 source hashes на каждом worker.
Git-primary: M40 `210a46ec562f11e975eae59425383ab2964e9855`, Elder
`32e50cbef287ada149c663b0c249ad24c5cd3c70`. Архивы около160KB на worker;
модели и старые эксперименты не запускались. Ветка удаления и её доказательства
не означают завершение всего этапа9 или общей приёмки develop.
