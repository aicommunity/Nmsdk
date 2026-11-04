# Текущая карта выполнения исходного плана,04.11.2026

Основание — [утверждённый план0–12](RefactoringPlan.ru.md). Нумерация и критерии
не сокращены до реализованных API. Это актуализация состояния после принятых
04.11 объединений; подробный прежний перечень требований сохранён в
[аудите01.11](PlanCompletionAudit-2026-11-01.ru.md). Старые «ещё не реализовано»
или «worker жив» в исторических дополнениях не заменяют текущие receipts.

Полностью принят только этап0. Все этапы1–12 остаются **частичными**. Exact
для нескольких fixtures, завершённый процесс и научный PASS различаются.
Ни итоговая карта всех моделей, ни весь рефакторинг пока не завершены.

## Актуальный краткий срез после последних приёмок04.11

Ниже расположена хронология дня: старые слова «работает», «не запускался» и «pending» относятся к моменту записи соответствующего дополнения. Текущие подтверждённые результаты:

| Проверка | Фактический итог и границы |
|---|---|
| Миграция cable/E1 | Приняты группы20+9 scripts:текущий manifest150 на обоих workers, negative restored-path controls/exact scopes. Production inventory подтверждает188 Bin candidates/0 выбранных root; общий этап9 не закрыт. [Приёмка](CableFamilyRetirement.ru.md). |
| Joint normal focused | 44/44; ошибочный исходный42 сохранён отдельно. |
| Joint normal full | 304/304 на Elder; полные первичные данные опубликованы. |
| ModelSpec2 fresh-process replay | 8/8 Classic/Branch×N0/N1×C-Off/On; actual soma/input CSV побайтно совпадают с исходными paired observations. |
| Python readers этого корпуса | 128/128, без failures/errors/skips. [Приёмка](JointOwnerReplayNormal.ru.md). |
| Временные графики переноса | Реальный plotting test1/1 на M40:60 видов/12 сом/8 моделей. В Git24 PNG; full cache на Data. [Читаемый отчёт и ограничения](JointOwnerReplayVisuals.ru.md). |
| Managed normal full path | 8/8:четыре Exact N1 Train/export/frozen пути и четыре stopped/export-refusal controls;16 actual managed native units закрыты. [Scope и открытые пункты](ManagedNativePipelineAcceptance.ru.md). |
| Managed frozen temporal reports | 1/1 на M40:24 trial–soma pairs,360 views;30 selected PNG в Git. При фиксированном threshold1.0 все4 случая TP0/FP0/FN2/TN2, успех классификации отсутствует. [Графики и ограничения](ManagedNativePipelineVisuals.ru.md). |
| Managed measured calibration normal | 4/4 на Elder:реальные grids,confirmation,отдельный frozen Test и NonSeparable/source preservation при исходном1.0 (changed-threshold rollback здесь не проверен);12 native groups закрыты. Все4 инженерных N1 случая TP2/FP0/FN0/TN2 после same-matrix calibration; stock scientific PASS не заявляется. [Приёмка/ограничения](ManagedNativeCalibrationAcceptance.ru.md). |
| Managed changed-threshold rollback normal | 4/4,16 actual native units, fresh restored model reproduces every sample/spike count; temporal report1/1 принят,32 матрицы/192 trial–soma pairs/84 selected PNG. [Scope и первичные данные](ManagedChangedThresholdRollbackAcceptance.ru.md). |
| Managed calibration temporal reports | 1/1 на M40:168 trial–soma pairs,2512 PNG;54 selected PNG в Git. [Галерея и ограничения](ManagedNativeCalibrationVisuals.ru.md). |
| Общий lifecycle dispatcher | Baseline133 SDK802:119 passed/14 failed/0 skips, core18 passed. Cold fixture не получил certificate; candidate8644 не компилировался. Corrected baseline33fc прошёл focused25/full133; candidate8644 ещё не собирался. [Полный отрицательный readback](Baseline133PrerequisiteReadback.ru.md). |
| Совместный ASan runtime | Build-only принят; сам по себе не подтверждает native44/304. |
| Прежний C-search ASan K1 | Тот же supervisor3649813/start284056538 подтверждён живым; full262 ещё работает. Это иной code snapshot. |
| Следующий joint ASan44 | Поставлен в ожидание K1; новый worker3836828/start286684788, фактические модели ещё не запускались. [Условия и budgets](../../../Reports/StructTrain/TimeLearner/s07-joint-asan44-queued-a2/job.json). |

Pending algorithm/Pulse branch не объединена в develop. Опубликованы данные и адресные исправления инфраструктуры, а не общий алгоритмический срез. Остаются joint ASan44/304/replay/readers, остальные режимы/профили, общий контроллер, production pipeline и научная матрица. Только этап0 полностью принят;1–12 частичны. Восемь replay моделей — инженерный transport-контроль с одним паттерном, не научная классификация всей матрицы и не доказательство влияния LT-мембраны.

## Принятая C++ основа до последующих Python merges

| Репозиторий | Принятая исходная точка |
|---|---|
| Root | `e218753e49b12f05708a60a4f22266882f810430` |
| PulseLib | `9ec4566d71bf56d4eeb5c8a920bbc683fcd85299` |
| Rdk | `10e9d05aa658dd2203c89bc84ba9166595b50014` |
| Bin | `99f58da9296a794374cef679bbb878cb62af979a` |

Таблица фиксирует согласованный C++/native-probe snapshot, не текущий root HEAD.
Последующие infrastructure Python merges до `1c51d0c23f1cee8fe0c59eceba872fcf30145235`
не меняют эти child gitlinks. Источник конкретного runtime берётся из manifest
его задания, а актуальный root HEAD — из Git, не из исторической таблицы.

Root develop последовательно принял resource budgets, construction threshold/
calibration и native probe/report acceptance. Merge commits сохранены; rebase,
squash, cherry-pick не использовались. Pulse child опубликован прежде root.
[Threshold integration receipt](InitialThresholdIntegrationVerification.json) и
[native probe integration receipt](NativeProbeIntegrationVerification.json)
сравнивают реальные trees с ранее проверенными источниками, вместо присвоения
merge commit вымышленного нового runtime pass. Нового численного запуска под
этими merge commits не было. Исходные normal/ASan primary и отрицательные
предшествующие verdicts сохраняются.

## Что принято и что ещё требуется

| Этап | Проверенные подэтапы / текущее состояние | Требования до полного закрытия |
|---|---|---|
|0 — начальное объединение|Принят ранее; дальнейшие адресно принятые изменения идут children-first через `--no-ff`.|Не считать каждую feature выполненной по одному merge. Текущий Git checkout проверяется отдельно ниже.|
|1 — доказательства и параметры|Есть source/property/evidence registries и адресные runtime receipts. Даты и версии критериев сохраняются.|Закончить полный semantic/property/evidence review обоих learner; разрешить remaining unknowns и отличать code fix от runtime-verified fix для каждого режима.|
|2 — сборки и runtime|Изолированные deploy roots, runtime/source manifests и process identities используются в принятых gates. Новые большие отчёты — на Data M40.|Закончить весь build/resource matrix, quantitative worker policies и проверку воспроизводимости общего runtime; не обновлять работающие SDK.|
|3 — измерения и scorer|Строгие native observations/scorer, explicit incomplete/invalid statuses и реальные временные отчёты работают в проверенных путях.|Покрыть все legacy adapters и оставшиеся modes/physical profiles; вся оценка должна зависеть от полных реальных окон и единственного versioned verdict.|
|4 — lifecycle/storage|Нативные fixtures и explicit model boundaries проверены;18 threshold/archive cases на каждом worker, включая реальные ответы2000/20000Hz.|Полная fresh/reuse/Copy/Load/growth/heterogeneous physics матрица и все legacy/V2 paths, единая семантика Default/Build/Init/Reset/Calculate без learner-specific обходов.|
|5 — model export/Train→Test|Исправленные8 calibration cases и7 readers на каждом worker:4 реальные Exact sources,4 исходных stopped controls,2 ModelSpec2 distinct-owner transfers.|Распространить полную semantic/response identity на остальные modes/topologies/dimensions/profiles. Не подменять полный export overlays и не обещать mid-probe checkpoint.|
|6 — общий контроллер|Native V2 service, adapters и scoped controllers реализованы; native probe теперь объединён. Граф, history и source references сохраняются в адресных import/probe случаях.|Полное legacy/V2 A/B и рефакторинг remaining duplicated controls; вся configured/multirate/compatibility матрица.|
|7 — алгоритмы|Честные bounded search/measurement/final certificate пути реализованы и адресно проверялись. C-search normal262/119 принят своей веткой; ASan K1 ещё работает.|Принять pending algorithm branches и их общий срез, завершить N0/N1/C-trim/quantization/bounds/nonmonotonicity/reset/physics matrix. Отрицательный stock Train не доказывает PhysicalInfeasible.|
|8 — conversion/PostTune/calibration|Есть versioned final states, transactional candidates и реальные calibration/frozen controls. Проверены новые threshold construction/transfer semantics.|Все реализованные PostTune/mute/inhibition/calibration/reset modes, commit/rollback/interruption, idempotent conversion и frozen independent evaluation для всей матрицы.|
|9 — единый пакет и миграция|Активные root CLI/анализ/отчёты реализованы; migration manifest и часть retirements приняты.|Удалить оставшиеся исторические executables из Bin/PulseLib/Docs после переноса нужного функционала, без wrappers; указать repository/full commit/path/blob. Завершить prepare/preflight всех supported factors.|
|10 — очередь/provenance/publish|Приняты path reservations15/15 и path+slot+RAM+disk budgets30/30 на обоих workers; диск привязан к реальному filesystem.|Связать public JobSpec/ConditionSpec с production Train→Test, весь owned process graph, cancel/recovery, actual resource policies и все publication/fault cases. Учёт заявленных ресурсов не является OS quota или полным scheduler.|
|11 — контрольные эксперименты|Августовские saved-state replay и cold controls сохраняют исходные4/8,5/8,6/8. Новый stock stopped A4:32 trials,80 trial-soma pairs,6+3 report checks,20 selected PNG просмотрены.|Legacy/V2, target в каждой позиции, order/ITI/reset, independent frozen и вся научная физическая матрица. Stock stopped diagnostic не заменяет Test обученной модели и не отменяет август.|
|12 — документация|Актуальные receipts/отчёты обновляются при каждом принятом срезе; новый A4 доступен для чтения.|Сквозное согласование root/submodule/config/ClDesc/defaults, оставшиеся migration links и снятие конкурирующих актуальных спецификаций.|

## Завершённые04.11 адресные проверки

- [Threshold/archive](InitialThresholdConstruction.ru.md):18 native cases на
  Elder и M40 ASan; четыре физических roundtrip Classic/Branch×2000/20000Hz
  сохраняют construction100 и поздний effective0.005, без LTMembrane.
- [Calibration preconditions](CalibrationFixturePreconditions.ru.md):8 native
  и7 data checks на worker; нет изготовленного certificate или ослабления
  CapturedPerInput/sync0.02/abs amp1e-5/relative0. Engineering LT fixture
  не обозначается как научный stock четырёхвходовый нейрон.
- [Native probe phases](NativeProbePhases.ru.md):12 imported jobs,7 readers
  и2 cold regressions на worker; прерывание warm baseline не меняет Rs и не
  запускает main probe. Все7362 primary files восстанавливаются побайтно.
- [Reservations](ResourceReservations.ru.md): schema2 атомарно учитывает
  каталоги/slots/RAM/disk;30 tests на каждом worker, включая настоящие два
  конкурирующих процесса и два filesystem. Recovery и production wiring
  остаются открытыми; живой K1 ledger не мигрировал.
- [Читаемый stock temporal report](../../../Reports/StructTrain/TimeLearner/s11-stock-stopped-phasea-visual-a4/REPORT.ru.md):
  полный кэш14728 файлов на M40,4450 trial-soma views,20 выбранных PNG в Git.
  Проверены40 metadata members и414 source hashes. Визуальная приёмка
  относится только к этим20 изображениям, не ко всему кэшу.

## Работающие проверки и следующие действия

C-search K1 root69789b8cb/Pulse84e456d на M40 имеет собственный неизменяемый
SDK/runtime. Supervisor3649813/start_ticks284056538, targeted native3660392
подтверждены живыми04.11. Предусмотрены34 адресных native cases, затем262
полных и119 readers. Успех не присваивается до фактического завершения и
независимой проверки. Этот снимок не включает новые initial-threshold/Rdk
и не является проверкой их будущего общего среза.

Отдельно запущен настоящий fresh recursive checkout root develope218753e4
только из origin, без object donors/alternates: M40 owner3667868,
`readbacks/s00-current-develop-checkout-m40-a1`. Он не собирает SDK и не
запускает модель. Проверяются exact gitlinks, чистота, tracked blobs и Git
connectivity. На момент записи checkout ещё работает; результата PASS нет.

Дальнейший порядок: принять эти результаты по факту; завершить общий
algorithm slice и его regression/probe checks; затем расширять контрольную
матрицу по уровням этапа11. Series D автоматически не возобновлять. Параллельно
продолжать незакрытые property/migration/scheduler требования; ожидание ASan
не является причиной объявлять план завершённым или останавливать всю работу.


## Последующее уточнение04.11

Fresh checkout owner3667868 закрыт успешно: origin-only roote218753e4 и все
семь gitlinks чисты,100534 tracked files сверены на worker и независимо с
локальными Git objects. [Доказательства и границы](FreshDevelopCheckout.ru.md).
Это не новый SDK build и не приёмка будущего C-search/containment code.

[Contained process primitive](ContainedProcess.ru.md) прошёл12/12 controls
на каждом worker;11 групп на сервер закрыты с kernel membership receipts.
OS limits и учёт потомков после потери frontend работают в этом API. Однако
lease recovery/journal/ConditionSpec/Train→Test wiring ещё не подключены;
старый runner и работающий K1 не переведены. Этап10 остаётся частичным.


Текущий contained-process sourceecc384214 прошёл расширенный13-case gate
на обоих workers; в develop принимается только этот явно ограниченный API.
Подготовлен также **непринятый** Pulse кандидат совместного C-search и
construction threshold `cc97149c90ce98ff24ca688452f4a40d54e0e63d`: merge
от9ec4566 с84e456d, без текстовых конфликтов. Его runtime/gates с ModelSpec2,
config schema4, новым Rdk/root и optional C On ещё не выполнялись; исходный
K1 не заменяет эти совместные проверки.

## Ресурсы и явный recovery04.11

Проверен узкий [closed-worker recovery](ClosedWorkerRecovery.ru.md):49/49
реальных infrastructure controls на каждом сервере, с сохранёнными events,
ledger readbacks и kernel closures. Он освобождает только lease первоначального
main процесса той же закрытой cgroup. Старые outside-controller leases,
автоматический dispatcher, полный journal и production wiring остаются открыты.
Этап10 по-прежнему частичный.

Подготовка joint normal a1 root9f92a40b/Pulsecc97149c на Elder была остановлена
до configure/build/native probes: слишком глубокая цепочка Git alternates
вызвала рекурсивные lazy fetch и достижение TasksMax128. Это ошибка доставки,
а не отрицательный научный результат. Whole-worker unit явно остановлен;
резерв оставлен held до отдельной проверяемой recovery, без ручного SQL.
Новая исходная копия normal a2 доставлена самостоятельными shallow Git packs:
rootcode и Pulsecode не имеют alternates; Docs/Reports явно не материализованы,
остальные gitlinks пока не установлены. Это ещё не SDK/runtime и не gate PASS.

На момент адресной проверки Elder имел23GiB свободно при95% заполнении.
Удалены только1832 промежуточных `.o` четырёх закрытых старых CMake builds,
815872568 bytes; подробный сжатый журнал включён в Elder recovery proof.
Исходные данные, библиотеки, `_deps` и Git object donors сохранены.
M40 имел84GiB свободно на system и393GiB на Data. Повторное утверждение,
что последняя ошибка подготовки вызвана SSH, не подтверждено: SSH работает.

Позднее04.11 резерв a1 действительно освобождён через проверенный API;
точный владелец и released ledger сохранены в Git. [Подробный статус](JointPreparationRecovery.ru.md)
фиксирует работающую normal a3 SDK compilation с тем же joint root9f92a40b,
семью чистыми gitlinks и без alternates в новой копии. Native42 gate ещё
не завершён. M40 K1 targeted34 прошёл по runner verdict,262 regression
работает; полная primary/reader приёмка остаётся открытой. Ни один из этапов
1–12 этими инфраструктурными подэтапами целиком не закрывается.

Следующий принятый подэтап10 — [contained runner/native-gate schema3](ContainedRunner.ru.md):
77/77 Python checks и2 реальных native C++ codec/storage cases на worker,
normal/ASan, без skips. Новый gate сочетает actual loaded files, cooperative
capture и закрытие всей cgroup; MainPID0 с живыми потомками наблюдается явно.
Прежние gates schema1/2 и текущие long-running jobs не меняются. Это не перевод
всех production Train/Test workers, полный scheduler или приёмка joint algorithms.

Следующий source-аудит исправил смешение commit/index/working headers в
[inventory schema2](InventorySnapshots.ru.md):10/10 tests на worker,
byte-identical current catalog,217 declarations и231 path-selected оставшийся
tool (root43/Bin188/Pulse0). Это нижняя граница для review, не разрешение
удалить каждый файл без разбора и не завершение semantic/runtime matrix.

Совместный normal42 gate root9f92a40b завершился с34 passed/8 failed:
восемь новых ModelSpec2/C-history cases с construction/effective threshold100
дошли до полных frozen observations без spikes, но общий fixture по суффиксу
`_spiking` ошибочно ожидал положительный spike count для любого threshold!=1.
Исходный failed результат сохраняется. Исправление expectations и повторная
native приёмка ещё требуются; алгоритмический или scientific PASS не присвоен.
На M40 отдельно работает **build-only** ASan joint SDK с одним compiler,
memory cap4GiB и preflight MemAvailable>=36GiB. Он не запускает native gates;
первоначальный K1 regression продолжает работу независимо.

[Первичный failed42 gate](Joint42Failure.ru.md) независимо проверен и сохранён
в Git:1205 members/510 source blobs,8 high100 graphs и32 полных frozen trials.
Работает отдельный повтор normal44 root8021301e после явного исправления
fixture expectations; old runtime/primary сохранены. Это pending native
приёмка, не completed joint algorithms. Temporal report этих probes пока pending.

Совместный [ASan build-only9f](JointASanBuild.ru.md) завершён и независимо
проверен:65 members,510 source blobs совпадают с normal9f, четыре instrumented
target flags и закрытая4GiB cgroup. Native gates0. Идёт отдельная инкрементальная
build-only подготовка corrected8021301e в новом runtime; K1 продолжает работать.
Компиляция и последующая численная/native приёмка учитываются раздельно.

Актуализация после завершения normal44: [44/44 cases подтверждены](Joint44Acceptance.ru.md),
включая восемь high100 negative и два low-threshold positive controls.
Независимо проверены1275 archive members/510 source blobs; восемь графов
и32 frozen observations совпадают с failed42 с учётом только абсолютного
сдвига времени (остаток<=1.43e-14s). Прежние pending normal44 записи выше
описывают предыдущий момент. Normal304 теперь запущен отдельно на том же
неизменённом runtime; full304/readers/ASan joint native ещё не приняты.
Компактный Git хранит primary5.87MB, без полного производного render cache.

Corrected ASan build-only root8021301e также [завершён и проверен](JointASanBuild.ru.md):
два приложения, четыре instrumented target flags,510 source blobs совпадают
с normal44; native models0. Готовность сборки не закрывает pending ASan gates.

Для joint normal44 построены [временные отчёты всех40 frozen trials](Joint44FrozenReports.ru.md):
60 trial/soma pairs,5 production-reader checks без skips,80 выбранных PNG
(10.4MiB) и full275-view cache на Data M40. Визуально просмотрены17 рисунков,
представляющих все10 моделей; полный manual review всех views не заявлен.
High100 controls: каждый TP0/FP0/FN2/TN2. Low0.0001 controls: каждый
TP0/FP1/FN2/TN1 плюс ранний target response. Это отрицательные LT engineering
контроли, не августовский stock replay и не science PASS. Молчание означает
отсутствие LT spikes при ненулевой soma response. Этап11 по-прежнему частичный.

[Native process policy portable checks](PipelinePolicyPortableAcceptance.ru.md):
15/15 на M40,54 archive members/279 source blobs, повторное чтение двух
реальных C++ process archives normal/ASan без нового расчёта. Pending worker
integration source1fd77d34f не включён в develop. Перед production promotion
нужны actual native job tests и учёт отдельных systemd units в lease release/
recovery, с registration-before-launch и fault-проверкой. Whole cgroup
управляющего worker сама по себе не доказывает завершение созданных им units.

Требование учёта managed-unit graph теперь подтверждено [реальным fault baseline](WorkerUnitGraphBaseline.ru.md):
isolated M40 recovery освобождает simulated runtime lease после parent closure,
когда отдельно созданная child unit ещё жива. SQLite и свежие kernel records
проверены; обе unit затем закрыты. Main registry/нейронные jobs не менялись.
Исправление, registration-before-launch, aggregate caps и повтор этого fault
case остаются обязательными до promotion source1fd77d34f. Этап10 не завершён.

[Schema3 managed-unit reservations](ManagedUnitsM40Acceptance.ru.md): M40
61/61, включая12 новых graph/cap/recovery cases и49 legacy controls. Fault
parent-closed/managed-child-live теперь удерживает isolated schema3 runtime;
после full graph closure освобождение подтверждено в SQLite. Приняты290
members/279 source blobs/21 fresh unit closures, implementation34394c301
ещё feature, не develop. Elder61 поставлен в ожидание normal304 slot; global
M40 schema1 и действующие SDK неизменны. Production integration/остальные
fault cases и весь этап10 остаются частичными.


## Дополнение после восстановления связи и проверки дисков

[Завершённые Elder gates](ElderCompletedGates-2026-11-04.ru.md): joint normal304/304
и schema3 kernel61/61 завершились; первичные архивы и closures проверены на
worker и локально и сохранены в Git. Дополнительные joint readers/ASan и
production worker acceptance остаются открытыми. На Elder18GiB free/97% used,
поэтому новые большие model jobs там не запускались. M40 Data387GiB free.
Повторный запуск уже работающего K1 не выполнялся.


[Managed native preflight acceptance](ManagedNativePreflightAcceptance.ru.md):
Elder62/62 новых alias/resource controls, M4019/19 actual public preflight/
portable checks. Предшествующая M4017/19 попытка сохранена с доказанными
512MiB OOM. Это адресная приёмка evidence; code backend не promoted,
Train→Test/production matrix и M40 повтор suite62 остаются pending.


## Принятый пакет theory/sim

[14 исторических исходников](TheoryScriptRetirement.ru.md) удалены из Docs
без wrappers; модели данных, отчёты и прежние научные критерии сохранены.
Manifest121 records (119 retired,2 moved), complete=false, проверен на обоих
workers с restored-path Git-tree negative control. После этого адресного
удаления прежний path-based остаток231 уменьшается до217 (29 root,188 Bin).
Это поправка к историческому inventory, не новая общая semantic/runtime приёмка.


## Исправленная регрессия analysis CLI

[Коллизия имени analyze](AnalysisDispatchRegression.ru.md) исправлена отдельным
alias import; production5 checks прошли на каждом worker по настоящим native
данным. На Elder дополнительно исполнены два readonly native controls; на M40
выполнен повторный анализ тех же Git primaries, без нового native запуска.
Совместные readers124/ModelSpec2 fresh-process coverage и joint ASan остаются
открытыми; этот hotfix не является их приёмкой.


## Joint readers: приёмка остаётся открытой

[Точные результаты и следующий gate](JointReaderOpenGates.ru.md): source802
reader119 и source4c reader124 не прошли. CLI shadowing исправлен отдельно,
но для новых восьми ModelSpec2 recognition cases ещё нужен настоящий
fresh-process replay, затем полный reader gate. Недостающий domain fixture
получен в отдельном native2, не добавлен задним числом в старый native304.
Все failed attempts сохранены в Git; algorithm feature/joint ASan не приняты.


## Normal joint owner8/readers128

[Восемь настоящих отдельных импортов](JointOwnerReplayNormal.ru.md) и полный
reader128 source982 прошли. Новые ответы byte-exact с original paired waveform,
original dataset304 не менялся. Failed attempts сохранены. Это закрывает
конкретные normal reader/replay blockers; joint ASan и общий режимный/scientific
охват остаются pending. Код алгоритмов/Pulsecc этим evidence merge не promoted.

### Читаемые графики fresh-process переноса

[Отчёт и ограничения](JointOwnerReplayVisuals.ru.md): на M40 прошёл реальный plotting gate 1/1 для 8 моделей, 12 сом и 60 видов. В Git сохранены 24 выбранных PNG и данные проверки; полные отчёты — воспроизводимый кэш на отдельном диске M40. Проверка не заменяет научную матрицу всех паттернов. Joint ASan и остальные пункты плана остаются открытыми; стадии целиком не закрываются.


## Pending cable/E1 migration04.11

Feature `1d5c8276cc9344362ebffccf43a0970d55cc2084` подготовил удаление20 связанных исторических cable/E1 tools. Числа и первичные данные сохранены; source retrieval внесён в candidate manifest141 records. В текущем develop остаётся принятый manifest121 records; общий остаток217 не уменьшается до завершения gate. [Два bounded metadata workers и exact handles](../../../Reports/StructTrain/TimeLearner/s09-cable-retirement-queued-a1/jobs.json) ожидают закрытия предшествующих native jobs. Исторический код не исполняется; общая native equivalence не заявляется.


## Ресурсы полного ASan: фактическое наблюдение04.11

[Kernel readback K1](../../../Reports/StructTrain/TimeLearner/s07-full-asan-resource-observation-20261104-a1/observation.json) подтверждает native PID3690746/start284598691, RSS23.30GiB/HWM23.32GiB, текущее выполнение Classic0At20000. Full262 ещё не terminal. Для будущего full304 необходим отдельный бюджет по реальным peak/free RAM; лимит8GiB focused gate не распространяется автоматически на полный набор. Это иной snapshot, причина памяти/утечка не установлена; число tests и критерии не меняются.


## Текущие implementation candidates после baseline133

Root33fc48278cff860d20c570cb703198847f028065/Pulsecc — только исправленная cold test-постановка, separate build/focused25/133; stage6 candidate8644 пока не испытывался. Новый Python coordinatorabf22df34c6a409f34ecdd2243dfadf547efca1c с pipeline run/continue/audit и8 actual integration checks сохранён в отдельной ветке; в develop этот CLI не включён и runtime ещё не проверен. Открыты ConditionSpec binding, fault/cancel/reconciliation, queue/publish/report wiring. Полный план0–12 не сужается; только0 полностью принят.


## Pending coordinator/render и единая A/B test-постановка

[Точные два jobs/handles](../../../Reports/StructTrain/TimeLearner/s10-coordinator-and-rollback-render-pending-a1/jobs.json):M40 строит все4 phase reports changed-threshold corpus, включая rollback-frozen; Elder ожидает свободного ресурса для8 actual production coordinator checks/20 units. Root1eab24de/Pulse8644 подготовлен с теми же Tests/App/CMake, что corrected baseline33fc. Ни candidate dispatcher, ни coordinator, ни новый render по этой записи ещё не приняты. Полный исходный план и scopes независимой оценки сохраняются.

## Принята галерея changed-threshold rollback

[Новый report gate1/1 и выборочная визуальная проверка14 видов](ManagedChangedThresholdRollbackVisuals.ru.md):32 матрицы,192 trial–soma pairs,2872 PNG в воспроизводимом M40 cache;84 PNG и manifests опубликованы компактно. Для всех четырёх случаев calibrated frozen TP2/FP0/FN0/TN2, rollback-frozen TP0/FP0/FN2/TN2. Возвращённое молчание — проверка восстановления, не classifier PASS. Ранее queued render теперь завершён; исходные queued записи сохраняют историю. Только этап0 полностью принят.

Coordinator source2cc остаётся queued на Elder; готовый reconciliation candidate970dd48a716a065583b1de197e49df4ac6f0895d с7 actual-corpus проверками пока не развёрнут и не исполнен. Он не изменяет immutable запущенное задание. Полная fault/cancel/reboot матрица, ConditionSpec и публикация остаются открытыми.

## Очередь сверки после сбоя coordinator

[Точное bounded задание7 checks](../../../Reports/StructTrain/TimeLearner/s10-managed-reconciliation-queued-normal-a1/job.json), source71b56cd5b1a0ce877054f9e45bc59f30fc2523c8, поставлено на Elder после полного закрытия и освобождения coordinator8. Это новые временные копии настоящего completed corpus с сохранением symlink log aliases, без новых native units. Не принято до фактического gate. Corrected baseline33fc уже прошёл focused25/25; полный133 ещё выполняется. Ни lifecycle candidate8644, ни новый coordinator/reconcile не promoted в develop.

## Pending ранний preflight всех фаз

[Новая постановка и ограничения](ManagedDeclarationPreflight.ru.md), candidate427a5f2ef28b90a76c458951cad8ef70bb118c95: до Train проверяются объявленные downstream probe/grid/conversion factors, criterion проверяется общей функцией scorer. Portable audit прежних schema1 данных сохраняет прежнюю structural validation. [Серверный gate11](../../../Reports/StructTrain/TimeLearner/s10-managed-declaration-queued-normal-a1/job.json) ждёт закрытия metadata reconcile worker и использует настоящий coordinator corpus без новых native units. Код не promoted; обязательны также полный повтор coordinator8 с собственными target negative jobs и scorer regression. Этап10 и весь план остаются частичными.

## Pending managed live recognition route

Candidate289a28ee73f4812fc860de88883ac469cf3e5516 добавляет отдельный schema2 Train→frozen Test без повторного export из solo: [контракт и открытые проверки](ManagedLiveRecognitionRouting.ru.md). [Gate6/10 actual native units](../../../Reports/StructTrain/TimeLearner/s10-managed-live-routing-queued-normal-a1/job.json) поставлен на Elder после corrected baseline133 и declaration11, SDK33fc/Pulsecc неизменяемый. До фактического результата не принят; остальные scientific/mode/fault требования исходного плана сохраняются.

## Pending minimum native sample window

Сверка preflight с NativeRecognitionObservationValidation.cpp выявила missing ticks>=1: slack округления сам по себе допускал окно около нуля шагов. Candidate df5e06800ca57a65a66e8f401c23e192d39d8778 добавляет явный минимум и проверки subtick/fractional/overflow без изменения physical tolerances. [Gate13](../../../Reports/StructTrain/TimeLearner/s10-managed-declaration-queued-normal-a2/job.json) поставлен после полного закрытия live-routing worker; native моделей в нём нет. Прежние pinned gate11/source427 и live6/source289 не менялись. Новое исправление пока AST-only и не принято в develop.

## Cable/E1 migration принята после M40 A2

M40 gate141 и negative restored-path control прошли на том же source1d5; полный scope36 и production trees проверены. Вместе с прежним Elder141 это разрешило merge20 исторических script removals: [приёмка и retrieval](CableFamilyRetirement.ru.md). Текущий manifest141 records (139 retired/2 moved), complete=false; нижняя граница оставшихся scripts197 (9 root/188 Bin). Прежняя queued A1 запись историческая: M40 A1 отменён до reserve/checks, A2 ограничен512MiB и использовал непересекающиеся с ASan пути. K1 не прерывался. Эта приёмка не подтверждает runtime equivalence исторических моделей и не закрывает весь план.

## Pending последние9 path-selected root tools

Candidate0cd87e45ecf350301483ff4371994ced688931ef удаляет9 historical E05/ITI/surrogate/snapshot tools без wrappers и сохраняет точный Git retrieval; production package/Tests/App/CMake/child gitlinks не меняются. [M40150 passed и source review](RemainingRootToolsRetirement.ru.md), failed first delivery retained. [Elder bounded metadata job](../../../Reports/StructTrain/TimeLearner/s09-remaining-root-retirement-pending-a1/jobs.json) ожидает declaration13. В develop остаётся manifest141/нижняя граница197 scripts; candidate150/188 не принят до второго gate. Более широкий review scripts без path tags остаётся обязательным.

## Приняты corrected baseline и операционные gates

[Baseline33fc25/133](CorrectedColdBaselineAcceptance.ru.md) полностью прошёл на тех же algorithms/Pulsecc с исправленной положительной cold постановкой; он не продвигает общий dispatcher или pending C-search в develop. [Resource dependency9/9 на обоих workers](WorkerDependencyState.ru.md) сохраняет сырые SQLite/kernel данные, отделяет ready от business/scientific success и устраняет зависимость от момента записи release-file. Пять failed prerequisites до reserve/model сохранены. [Последние9 path-selected root tools](RemainingRootToolsRetirement.ru.md) приняты после двух150-record gates; текущий manifest150, complete=false. Новый production inventory source287b75d0 подтверждает217 declarations и188 Bin candidates; это metadata-only sparse clones, не SDK/пользовательские working-tree readbacks. Более широкий source/property/mode/runtime/science аудит остаётся открытым.

Coordinator retryA2 source2cc/runtimef679 фактически выполняется после resource readiness; первый Branch case прошёл. Live/reconcile/declaration candidate gates из прежней failed chain ещё не испытывались. Следующий C++ шаг — build/A-B общего lifecycle8644 с теми же corrected Tests и source declarations, после освобождения текущего ресурса. Только этап0 полностью принят;1–12 частичны.
