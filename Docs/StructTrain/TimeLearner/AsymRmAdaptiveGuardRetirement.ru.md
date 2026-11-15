# Вывод исторических AsymRm adaptive guards

Этап9, отдельная конечная группа: три прежних инструмента
`SelectivityAsymRm/scripts/length_step_guard.py`, `l_train_guard.py`,
`train_time_budget.py`. Все исходники прочитаны целиком; новый manifest содержит
245 records:243 retired и2 moved, `complete=false`. Серверная приёмка завершена на обоих workers. Удаление не меняет алгоритмы или физику learner.

## Почему эта группа историческая

- length_step_guard использовал fixed N=4/reference3, предсказание cable delay,
  L-reference и heuristic hopeless/plateau для отмены старого adaptive length step.
- l_train_guard правил XML длины/IsNeedToTrain/StructureBuildMode и накладывал
  табличный L-floor либо rollback по эвристике изменения LastAbsDtTrace.
- train_time_budget оценивал wall time из old gts/span/model-time calibration,
  мог брать произвольную первую запись калибровки и сам не владел процессом.

Их executable driver уже выведен. Буквальный поиск module names (с расширением
и без) по pinned root/Pulse/Bin/Rdk source/config/docs не обнаружил действующих
исполняемых потребителей. Единственная Bin-ссылка в historical REPORT и одна
root-ссылка заменены immutable Git URL. Старые inventory JSON и исходные
измерения не переписаны. Динамические внешние вызовы таким поиском не исключены.

Роли штатного поиска и остановки теперь принадлежат корневому production runner,
owned process budgets и bounded native controller. Старые аналитические L-floor,
plateau и wall/model-time предположения не переносятся как математический
контракт. Это не утверждение функциональной или научной эквивалентности.
`asymrm_train_common.py`, `patch_l_reference.py`, остальные analyzers сохраняются
до разбора их действующих зависимостей. Старые кампании не запускаются.

## Git retrieval и точный scope

Archive snapshot Bin:`918ae5e1a2d6085b9ff148f7162eb9e744126592`;
feature:`36f4ce6ae4cdbea90240dced08425fdf64f3bcf7`.
В [script_migration.json](script_migration.json) для каждого old path сохранены
repository/full archive commit/last-change commit/blobSHA1/contentSHA256/bytes
и `git show` команда. Старых путей, wrappers и копий в feature нет.

Bin scope ровно3D+1M: три helpers и единственная ссылка REPORT. Остальные
config/model/CSV/report blobs неизменны. Root scope — gitlink, metadata/retrieval
реестр, полный четырёхрепозиторный inventory и одна pinned historical link;
production Scripts/Tests/native code не меняются. Проверки: production history
CLI по всем245 записям на обоих workers, restored-path negative Git fixture
(exit2/no positive receipt), точный diff scope и metadata source hashes.

## Полный обход текущих деревьев

[Machine-readable snapshot](FourTreeScriptInventory-20261108.json) основан
на root27d6e4b/Pulse2c3eb8d/Bin918ae5e/Rdkd6c9df7; чтение — `git ls-tree`
полных pinned trees, независимо от sparse checkout. По явно указанным suffix,
Git executable-mode и CMake rules найдено803 paths:root652/Pulse1/Bin130/Rdk20.
Это **не803 кандидата на удаление**: maintained package/tests и обычные build
или product definitions классифицированы отдельно. Распознавание произвольного
языка в файле с неизвестным suffix и без executable-mode не заявлено.

В Bin105 Python всего,18 Python в AsymRm до этой группы; после неё15.
В root109 loose provenance-source executable-suffix paths под Reports остаются
отдельным открытым retirement batch. Они не объявляются допустимыми wrappers
или завершённой миграцией. Primary archives/models/наблюдения сохраняются;
для каждого будущего удаления нужен immutable Git retrieval и consumer review.
Maintained artifact_bundle хранит provenance внутри primary archive, но generic
publisher пока разрешает явно заявленные loose scripts; отдельный будущий guard
должен прекратить их повторное появление, сохранив старую доказательность.


## Приёмка

На Elder и M40 production history CLI проверил все245 retrieval records;
negative Git fixture, возвращающий length_step_guard.py, получил exit2 и не
создал positive receipt. Подтверждены exact3D+1M Bin, шесть root paths,
неизменность остальных code/native trees и полное совпадение803 строк inventory
с четырьмя Git trees. Никакие старые helpers и модели не исполнялись.

Первые A1 попытки сохранены с terminal=false: CLI245 был успешен, затем
one-off wrapper неправильно декодировал UTF8 worker через Windows locale и
сломал ожидаемую русскую подпись ссылки. Исправлена только передача source
с explicitUTF8. A2 получили новые job IDs после kernel/lease closure; source,
конфиги и физика остались теми же. Статусы CLI и wrapper не объединены.

[Независимая квитанция](AsymRmAdaptiveGuardRetirementVerification.json)
проверила по60 members,245 records и411 source hashes на каждом worker,
local canonical UTF8-LF worker SHA против actual producer/runtime declaration,
два closed/released attempts на каждом worker и negative Git pack scope.
Evidence M40:`001d26c0293b97472bfc34aacac4f8bab64e42a3`,
Elder:`3bbc24f685ef656a32b29fdf7fdc602018e6c3f7`, около162KB каждый.
Архивы используют объявленный128MiB dictionary; metadata reader применил
ограничение256MiB. Это компактные Git primary, не полноразмерные figure caches.
При подготовке Git receiver M40 сначала не хватало .gitattributes в минимальном
Rdk pack; только собственный ещё неиспользуемый receiver дополнен Git blobs,
после чего checkout clean. [Delivery receipt](AsymRmAdaptiveGuardDeliveryRepair.json).
Пользовательские копии и активные model runtimes не менялись.

Полный этап9 и develop-приёмка остаются открытыми; accepted scoped batch не
означает переноса остальных AsymRm tools, удаления109 loose Reports scripts
или полного допуска нового experiment pipeline.
