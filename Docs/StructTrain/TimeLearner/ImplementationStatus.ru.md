# Состояние реализации TimeLearner — 08.11.2026

**Полностью принят только исходный этап 0. Этапы 1–12 выполнены частично.**
Полный объём сохраняется в [плане](RefactoringPlan.ru.md). Технический PASS,
merge и научная разделимость — разные утверждения; 8/8 не является условием
завершения. Эта страница содержит текущую сводку; промежуточный журнал сохранён в Git. Исторические попытки
и отрицательные результаты сохранены в Git и отдельных receipts.

Уточнение 07.11.2026 после просмотра Classic burst: Train измеряет максимум
закреплённого импульса, Test — реакцию на паттерн целиком. Проверка числа пиков
во всей пачке не является общей математической целью. Исправление выбора и
сопоставления ещё открыто: [source review, файлы и адресная приёмка](PeakMeasurementContractReview-2026-11-07.ru.md).
Ранее сохранённые InvalidObservation не переоцениваются автоматически в Exact.

Начат [диагностический API подмножеств пачки](StimulusSubsetDiagnostics.ru.md),
нужный для проверки наложения на неизменном нейроне. Planner7/7 принят;
schema6 прошла71 unit и19 native checks на Elder/normal; результаты и каждый
из138 source hashes сверены с Git. Последующая версия с обязательным sink,
фактическим restoration readback и строгим reader также прошла отдельную
приёмку:71 unit,20 physical и7 reader checks без skipped.
Это waveform-only
режим без назначения пиков/сертификатов, не исправление full-burst assignment.
[Точное действующее задание](StimulusSubsetNativeJobs.json).

Console schema6 также прошла6 реальных проб и6 reader checks; опубликованы
сжатые primary и [отчёт с временными графиками](StimulusSubsetControlReport-2026-11-08.ru.md).
Это low-threshold diagnostic состояния с фактическим порогом0,0117,
не повтор high-threshold модели с порогом100. Все12 рисунков в кэше M40;
две выбранные overview проверены визуально. Имя старого каталога не заменяет
проверку параметров эффективного графа. Для нужных high-threshold состояний
выполнены14 full/omit/single условий с точными state/model hashes.
[Научный отчёт с четырьмя проверенными иллюстрациями](HighThresholdSubsetScientificReport-2026-11-08.ru.md),
[primary receipt](HighThresholdSubsetPrimaryVerification.json),
[temporal receipt](HighThresholdSubsetTemporalVerification.json). Полный кэш28 фигур
на M40; в Git — сжатые первичные данные, метаданные и выбранные рисунки.
Все пробы диагностические, без Train/классификации/assigned certificate.

Исправлен отдельный [дефект повторного учёта общей вершины в сертификате](AssignedVertexCertificateGuard-2026-11-07.ru.md):
контролируемый counterexample воспроизведён до изменения; после него23/23
production C++ unit checks прошли на Elder/normal и M40/ASan. Диагностическое
чтение schema1/2 сохранено. Полный SDK Elder теперь собран:23/23 нового
CMake target,21/21 native storage/training и7/7 reader checks прошли.
[Новый native-контроль с графиками обеих сом](AssignedVertexNativeControlReport-2026-11-07.ru.md)
подтверждает отказ общей вершины. ASan SDK batch M40:build и23 unit прошли,
но прежний physical21 прерван timeout; неуспешная попытка сохранена целиком.
Последующая интегрированная сборка b711/Pulse609 прошла71 unit,10 physical
и7 reader checks: [receipt](IntegratedSubsetASanVerification.json).
Отдельный дефект записи EventsLog прошёл адресную проверку:
[receipt](TestLogOwnershipASanVerification.json). Это не полная матрица.
Сопоставление волн штатной пачки остаётся открытым; это feature branch.

На M40 выполнена [проверка гипотезы наложения](SuperpositionDiagnostic-2026-11-07.ru.md)
для двух архивных high-threshold burst/single пар. Сумма сдвинутых single
близко воспроизводит все пять soma channels, включая три максимума Soma1
при четырёх импульсах. Для Soma4 глобальный максимум предшествует закреплённому
pulse3, подтверждая запрет подмены индивидуальной цели Train общей Test
характеристикой. Четыре tests прошли; новых native calculations/сертификатов
нет. Это диагностика для исправления measurement, не реализация его замены.

Принят [исторический frozen-пилот порядка/ITI с графиками](HistoricalFrozenProtocolScientificReport-2026-11-07.ru.md):
четыре условия, во всех6/8, TP1/FP2/FN0/TN5; те же два FP, без late spikes.
128 temporal views построены на M40 из Git primary, шесть выбранных проверены
визуально. Это не cold retrain и не независимый Test. Последующая [полная первичная матрица16 условий](HistoricalFrozenProtocolMatrixScientificReport-2026-11-07.ru.md) принята: target во всех8 позициях на двух Delay, те же6/8 и FP IDs.Полный temporal комплект512 views/128 presentations и оглавление приняты;384 новых,128 использованы по hashes. Это одна frozen историческая модель, не полный этап11.


Проверка Rdk загрузчика выполнена на M40 и Elder: before воспроизводит отказ
без свободных потоков, after проходит2 metadata checks на каждом сервере.
На M40 дополнительно5 storage/physical checks и чистый Classic-6 replay:
входы/потенциалы4 сом и JSON каналов побитово совпали с исходной пробой,
stderr пуст. Исходный ERROR сохраняется; точное место прежнего исключения
не доказано. [Диагностика](DescriptionLoadingResourceDiagnostic.ru.md),
[квитанция M40](RdkDescriptionLoadingVerification.json),
[квитанция Elder](RdkDescriptionLoadingElderVerification.json).

Исправление открытия существующего worker ledger прошло44 проверки на каждом
сервере: [документ](ExistingWorkerLedger.ru.md),
[независимая сверка](ExistingWorkerLedgerVerification.json). Оно не закрывает
весь scheduler/publisher scope этапа10. Следующая операционная проверка ошибок
stdout/stderr прошла по33 проверки на обоих серверах: [политика](OperationalDiagnostics.ru.md).
На M40 production portable auditor отклонил исходный положительный manifest
Classic-6 с ERROR и принял чистый повтор; численные файлы не переписывались.

Выделен общий production extractor измеренных вершин без смены assignment
policy. На Elder приняты78 unit и15 native cases: [normal93](MeasuredResponseNormalVerification.json).
На M40 завершены78 unit и9 native checks с ASan; Classic N=6 превысил
wall budget1200 секунд, остальные5 cases и A/B не выполнены. Попытка закрыта,
lease освобождён, evidence сохранён; полная ASan-приёмка не заявляется:
[квитанция неполной проверки](MeasuredResponseAsanPartialVerification.json),
[точные задания](MeasuredResponseJobs.json).
Это не исправление принадлежности пиков полной пачки и не завершение этапа7.

Подготовлен отдельный production diagnostic `ResponseDomainAssociation`:
26/26 проверок на Elder и26/26 на M40 с ASan, без skipped. Он сохраняет
измеренные вершины и signed offsets, отклоняет общую вершину/плато и явно
не допускает `Hypothesis` к сертификату обучения. ASan здесь проверяет
utility, а не весь SDK. [Контракт, receipts и подробная подготовка native bridge](ResponseDomainAssociation.ru.md).
Связка штатных onPrepared/onSample/result с portable evidence и независимым
reader описана ниже. Следующая алгоритмическая задача — отдельно принять
метод происхождения отклика. Эксклюзивность временного окна сама этого не доказывает.

Связка native capture/portable codec/reader подготовлена и прошла normal-проверку:
10 integrity/codec checks и4 настоящие Classic/Branch пробы на2000/20000 Гц;
reader12/12 на каждом сервере и независимый пересчёт4 C++ пакетов по primary CSV.
Дополнительно совместный old/new native gate2/2 подтвердил раздельные trial/
artifact identities. Все эти результаты и исходные отказы по ресурсам доступны
в Git: [контракт и receipts](ResponseDomainEvidence.ru.md).
Полная ASan-проверка связки на M40 запущена. Console integration, расширенная
fault/N матрица, визуальный отчёт и causal attribution остаются открытыми;
в Train диагностическая Hypothesis не включена.

Миграция расширена до242 записей (240 retired/2 moved): четыре исторических
AsymRm seed/reset инструмента удалены без wrappers. На обоих workers прошли
production CLI, negative restored-path control и exact4D+4M scope:
[приёмка](AsymRmSeedRetirementVerification.json). Осталось18 AsymRm Python;
полная миграция и develop-приёмка остаются открытыми.

## Проверенные срезы

| Срез | Подтверждено и ограничения |
|---|---|
| Принятый root develop | `1d1c8e5dc3e50bca51c174d9552feab4a5ccf5d9`; принята отдельная группа16 LTZ drivers, не весь этап9 |
| Принятые PulseLib / Bin / Rdk | `0ec9193e6620ae2439329eece5ecd6d6f167c70a` / `b4f66eb137d3e1c19539890dbdee06faa3e1020b` / `10e9d05aa658dd2203c89bc84ba9166595b50014` |
| Общий ASan SDK | root2e061/Pulse12d: 133/133; не подтверждает последующие изменения |
| Baseline recovery SDK | root84d6/Pulse416: normal118 и адресный ASan19 приняты; stock Train/evaluation завершены |
| Fair-domain compiled SDK | root36f598/Pulse8f057: normal137/137 и адресный ASan38/38 на M40; общая приёмка в develop ещё открыта |
| Исторический documentation snapshot PulseLib | `2f6b57253bd7ae380a19320ef3835a2701cb4d30`; Core совпадает с tested8f; это не текущий HEAD feature |
| Storage feature документация PulseLib | `3e19cdb97566d6f7e09ff2bc0804115eb59204f9`; Core совпадает с compiled1f97 и Elder8702. Добавлены Train/Test peak contract, диагностика наложения и Elder normal gate; scope runtime не расширен |
| Новый кандидат измерителя | Core PulseLib6c520fb: explicit schema5 single-impulse maximum; [unit ASan34](ProbeAlgorithmsASan.ru.md) на M40 и [normal38/readers25/unit34](SingleImpulseMaximumElderAcceptance.ru.md) на Elder приняты на root629/Pulse24f. A1 failure сохранён. [Console replay stock multi-peak](SingleMaximumConsoleReplay.ru.md): Root038/Pulse217,4 native operations,5 design tests, exact archived and A/B waveforms; [physical ASan38/readers25](SingleImpulseMaximumPhysicalASan.ru.md) Root038/Pulse217 принят; [normal N1/2/4/6 matrix9/readers10](SingleImpulseMaximumDimensionMatrix.ru.md) RootE91/Pulse217 принята; её ASan9/readers10 на M40 также принята, whole-burst assignment открыт; [контракт](SingleImpulseMaximum.ru.md) |
| Prepared-owner / storage Console SDK | M40 root844b278/Pulse1f97: normal26, readers29+9+2, Console12 и4 exact baseline pairs. Elder rootac9/Pulse8702: normal163/readers19. M40 rootb97/Pulse8702: ASan26/readers19 приняты; Console12 на Elder открыты |
| Single-pulse ASan SDK | root5d0b80/Pulse302: M40 native37, Console4 иPython42. Это предыдущий SDK, без нового storage API |
| Worker-limit Python SDK | rooteae3: 26/26 на каждом сервере; не проверка нейронного обучения |

На Elder закрыта дополнительная подготовка диска: удалены 275 подтверждённых
дублирующих static `.a`, для каждой оставлена проверенная копия. Остальные
462 file/symlink bindings выбранных runtime неизменны. Свободное место в ходе
операции1.52→4.11GiB; исходники, executable, модели и primary не удалялись.
Шесть filesystem/lease tests прошли; группа закрыта, lease released, схема2/
capacity/slots не менялись. [Отчёт и ограничения](StaticArchiveCleanup.ru.md),
[проверка Git primary](StaticArchiveCleanupVerification.json).
Это освобождение места не заменяет preflight конкретной следующей сборки и не
означает автоматической приёмки всех storage/Console gates на Elder;
normal163/readers19 подтверждены отдельно в
[отчёте второго сервера](FeedbackStorageElder-2026-11-07.ru.md).

В [исправленных channel reports](ChannelObservationScope-2026-11-07.ru.md)
разделены полнота сигнала, отказ packet measurement и принадлежность окна soma.
На M40 прошли три tests и A/B всех 163 views; три выбранных рисунка просмотрены
после исправления перекрытия легенды. Это не исправляет C++ assignment и не
закрывает полную визуальную матрицу этапа11.

Полные SHA, source hashes, первичные архивы и process closure:
[ASan133](IntegratedSharedAsan133Verification.json),
[normal137](FairDomainTraversalNormal137Verification.json),
[ASan38](FairDomainTraversalAsan38Verification.json),
[worker limits](WorkerLimitPreflightVerification.json).
ASan не является leak check. Эти результаты имеют область соответствующего
receipt, не всей матрицы. Default native comparison нового fair варианта:
284 CSV и 480 JSON идентичны baseline, ещё 19 startup JSON отличаются лишь
StepDuration. [Изменение алгоритма](FairDomainTraversal.ru.md) касается только
opt-in N1 AdvanceUnassignedBurst; CapturedPerInput, reference и допуски сохранены.

## Научные результаты

Baseline stock серия: все восемь Train остановились InvalidObservation без
сертификата. Последующие 64 диагностические пробы полны и валидны; переданы
фактические stopped модели. При inherited0.0117 каждый случай TP1/FP7/FN0/TN0,
при100 — TP0/FP0/FN1/TN7. Молчание7/8 не является успешной детекцией. Два
порога не доказывают NonSeparable на всей сетке.
[Научный отчёт](StockRecoveryScientificReport-2026-11-06.ru.md),
[Train primary](StockRecoveryNativeVerification.json),
[evaluation primary](StockRecoveryEvaluationVerification.json).

Полный render этой baseline серии завершён: 160 trial/soma pairs, 8931 views,
30287 файлов, все checksums проверены. Каждая пара имеет полный2с обзор и
40 непрерывных50мс увеличений с потенциалом сомы и входными импульсами, без
прореживания. Полный2.1GB cache хранится на M40; Git содержит компактные
primary, metadata и выбранные PNG. Вручную просмотрены четыре PNG, не весь cache.
[Проверка графиков](StockRecoveryFullVisualVerification.json),
[visual QA](StockRecoverySelectedVisualQA.json).

Новая matched серия s07-stock-fair-domains-normal-a2 завершена и опубликована:
8 cold preflight и8 Train, все InvalidObservation без certificate. Полные
аудиты обеих серий и сравнение восьми пар условий прошли; группа процессов
закрыта, lease released. [Приёмка primary](FairDomainStockTrainVerification.json).
Advance расширил записанные geometry groups: Classic2→59 и5→47,
Branch5→58 и31→60. Это не полный search box и не улучшение классификации.
В четырёх default Retry случаях совпали модели, summaries и728 native CSV.
[Сравнительный отчёт](FairDomainStockScientificReport-2026-11-07.ru.md).

[Оценка восьми новых моделей](FairDomainStockEvaluationVerification.json) завершена:
пять role/job checks прошли, все64 native diagnostic пробы полны и valid.
При inherited0.0117 вновь TP1/FP7/FN0/TN0, при100 — TP0/FP0/FN1/TN7.
Primary опубликован:5043 members, каждый повторно проверен по размеру и SHA256.
Процессы закрыты, lease released. Все160 trial/soma pairs отрисованы:
9190 временных views,30302 cache files/2077769934B на M40.
Четыре выбранных PNG проверены [вручную](FairDomainStockSelectedVisualQA.json);
это не полный ручной просмотр cache. Обученных моделей с сертификатом0.
Условия — исходный NSPNeuronGen без дополнительной LTMembrane, без
C-trim/PostTune/калибровки. Baseline ответы не подставлялись вместо новой серии.
[Адресный wave-аудит](FairDomainStockPeakAudit-2026-11-07.ru.md) подтвердил
все264 invalid по CSV: дополнительные либо недостающие локальные максимумы
при четырёх фактических импульсах. Общая причина всех264 и исправление
assignment ещё открыты. Для двух low/Retry состояний выполнено отдельное
[контролируемое feedback-вмешательство](FeedbackProfileScientificReport-2026-11-07.ru.md);
его выводы нельзя переносить на все случаи missing/ambiguous.
[Точный replay двух low/Retry candidate](StockWaveReplay.ru.md) после полного
import/Reset воспроизвёл все soma/input samples и ambiguous. Шесть серверных
проверок прошли. [Первый импульс](StockFirstPulse.ru.md): до второго onset
Classic уже имеет3 положительных максимума, Branch —1; четыре адресных tests
прошли. Это ограничивает предположение «один максимум на импульс», но не
определяет правило выбора response wave. Replay cache251 view завершён.
Последующие [single-pulse controls](SinglePulseCharacterizationScientificReport-2026-11-07.ru.md)
проверили полное окно: Branch имеет второй слабый максимум после прежнего
префикса. [Feedback12](FeedbackProfileScientificReport-2026-11-07.ru.md) сузил
причину для двух low states; общее правило измерения ещё не принято.

Августовские4/8,5/8,6/8 подтверждены не только исходным визуальным наблюдением:
выполнены [saved-state replay](HistoricalAugustReplay.ru.md) и
[настоящее cold Train → frozen Test](HistoricalAugustColdStart.ru.md)
на историческом SDK и в исходном протоколе. TP1, FP4/3/2, FN0, TN3/4/5;
это legacy_done_uncertified, не V2 Exact. Временные данные cold Test совпали
с replay, граф передан полностью. [Повторная проверка трёх primary архивов](HistoricalCompletedEvidenceRevalidation-20261107.json)
подтвердила все104+83+236 members и неизменность относительно опубликованных
commits. Порядок, увеличенный ITI и legacy/V2 A/B этим не проверены. Ранее N2 LT проверка дала5/8
(TP1/FP3/FN0/TN4), NonSeparable на проверенной сетке. Узкие engineering случаи
TP2/FP0 повторяли один target/foil после same-matrix калибровки и не являются
независимой восьмипаттерновой оценкой.
[Исходные результаты](ScientificResults-2026-11-03.ru.md).
Серия D не возобновлялась.

## Приёмка по исходным этапам

Source-сверка07.11 [feature против develop](PropertyFeatureSourceDrift-20261107.ru.md)
подтвердила неизменность всех217 исследованных property slices. Изменения
общих lifecycle/storage/capacitance/analyzer consumers рассматриваются отдельно;
runtime/effective-factor matrix этим не закрывается.

| Этап | Подтверждено в ограниченной области | Что мешает закрыть этап целиком |
|---|---|---|
|0. Начальное объединение|Принято; последующие изменения объединяются children-first через merge commits|Новые features проходят свою приёмку отдельно|
|1. Доказательства и параметры|Есть реестры, исторические anchors и catalog coverage всех217 деклараций; это source coverage, не runtime matrix|Обновить semantics изменившихся consumers/helpers, inherited Rdk properties и оставшиеся audit unknowns; завершить runtime/effective-factor проверки|
|2. Сборки/runtime|Изолированные сборки, manifests, process ownership; приняты scoped gate/output и archive restoration fixes|Полная build/resource/fault matrix, общий срез и воспроизведение closure; не считать учёт ресурсов OS quota|
|3. Наблюдения/scorer|Строгие native observations, completeness/ID/finite checks и versioned metrics; legacy numeric reader не достраивает доказательства|Все legacy adapters, режимы/физические профили и единый итоговый verdict для всей области|
|4. Lifecycle/storage|Есть реальные native fixtures, graph/response readback и проверки boundaries|Полная fresh/reuse/Copy/Load/Build/growth/heterogeneous physics матрица и все compatibility paths|
|5. Export/import|Есть completed/stopped state transport, native storage/graph archive, boundary continuation и fresh destination controls|Все варианты моделей/физики/связей; полный mid-probe checkpoint не обещается|
|6. Общий контроллер|Общий native service, configured controller и topology adapters существуют|Принять оставшийся общий срез, завершить legacy/V2 A/B, дублирующиеся hooks и multirate verification|
|7. Алгоритмы|Measured bounded L/Ns/Rs search, N0 repeats, финальная проверка; C0 API принят, bounded C-search — кандидат|Полная bounds/quantization/nonmonotonicity/invalid-probe/physics/reset матрица, приёмка кандидата и stock measurement recovery|
|8. Recognition/PostTune/calibration|Versioned solo/recognition states, transactions, measured threshold confirmation и frozen controls работают в проверенных случаях|Все PostTune/inhibition/reset modes, commit/rollback/interruption и независимая оценка|
|9. Скрипты|Корневой пакет и CLI работают; migration245:243 retired+2 moved; три AsymRm adaptive guards приняты обоими серверами без wrappers|Остаются15 AsymRm Python,109 loose Reports source snapshots и прочие инструменты; four-tree803 inventory классифицирован, не является разрешением удалить всё|
|10. Запуск/provenance/publish|Есть owned processes, leases/budgets, fail-closed publisher и реальные coordinator controls|Полная effective-factor attestation, scheduler/cancel/recovery/publication fault matrix; declarative ConditionSpec binding её не заменяет|
|11. Научные проверки|Августовские saved-state replay и настоящий cold Train→Test воспроизвели4/8,5/8,6/8; есть N2 controls и временные отчёты|Разбор InvalidObservation нового V2 stock среза, legacy/V2 A/B, target в каждой позиции, order/ITI/reset и independent frozen matrix|
|12. Документация|Поддерживаемые сводки согласуются с receipts; исходные отчёты сохранены|Сквозная актуализация root/PulseLib/Bin/config/ClDesc/defaults и завершение миграции ссылок|

## Путь к итоговым выводам

1. Использовать завершённую оценку восьми фактических моделей и полный
   temporal cache как основу waveform/peak-assignment аудита. Train,64 пробы
   и render уже завершены; не повторять их ради обновления отчёта.
2. Разобрать invalid peak/burst assignment и проверить исправление реальными
   штатными пробами. Budget exhaustion не доказывает PhysicalInfeasible.
3. Использовать уже принятые августовские replay и cold Train→Test как
   историческую опору; выполнить legacy/V2 A/B и отдельные проверки
   перестановок, ITI, continuous/reset-per-trial. Повторять исходные запуски
   только при новой проверяемой причине, не из-за неточной сводки.
4. Проверить frozen модели и пороги, target во всех позициях, полные окна;
   независимость данных заявлять только при реально независимой оценке.
5. Завершить исходную матрицу режимов/физики, миграцию, документацию и общую
   приёмку children-first в develop через merge commits.

Общий native service, measured bounded поиск, N0 repeats, native export/import
и recognition transactions уже существуют. Их ограничения описаны в
[capabilities](ControllerCapabilities.ru.md),
[parameter contracts](ParameterControlContracts.ru.md),
[readiness](ExperimentReadiness.ru.md). Полная lifecycle/storage/growth и
legacy/V2 матрица остаётся открытой. Migration245 (243 retired+2 moved) не равна
всему inventory; остаются18 AsymRm Python и другие инструменты. Полная scheduler,
recovery, publication fault matrix и effective-factor attestation не закрыты.
Компонентные страницы PulseLib актуализированы.
[Пять свойств и общие тексты двух ClDesc](ClDescControllerContractReconciliation-20261107.ru.md)
сверены с исходниками и приняты в Bin/root develop; изменены только Description.
Compiled receipts сохраняют прежний Bin37ff: действующие runtime не обновлялись.
Все остальные ClDesc/config/defaults ещё не сверены. Исторические primary не удаляются ради компактного Git.

Предыдущая накопительная сводка сохранена в
[Git](https://github.com/aicommunity/Nmsdk/blob/b2517a3576f949c12acb402ce83ab595ebcbf0b1/Docs/StructTrain/TimeLearner/ImplementationStatus.ru.md).
Неудачные проверки остаются evidence своего среза, не переписываются под PASS.


Журнал промежуточных статусов и дополнительных scoped gates до этой сверки
сохранён в Git: `9348ff8497966900a7bdbf418f084189089b2722`, тот же путь.
Ссылки на первичные receipts и профильные отчёты остаются действующими.
Записи «выполняется» в историческом журнале не описывают текущие процессы.


## Дополнение 8 ноября: измерительный тракт и графики

ASan capture/codec:10 проверок,4 реальные пробы и4 independent packet checks
приняты по [квитанции](ResponseDomainEvidenceAsanVerification.json);
leak detection выключен. [Диагностический отчёт](ResponseDomainDiagnosticReport-2026-11-08.ru.md)
schema2 содержит все шесть сочетаний проба×сома для четырёх N2 контролей,
132 рисунка в кэше M40 и8 выбранныхPNG в Git. По5 renderer tests прошли на
обоих серверах. Это ограниченная приёмка измерений и визуализации, не Train
и не классификация. Причинная принадлежность пика и интеграция нового
измерителя в Train остаются открытыми; этап7 и исходная цель не завершены.


Normal [проверка revision provider в fixtures](NativeFixtureRevisionProviderNormalVerification.json)
принята по32 исходным тестам:22 invalidation/NoopBuild,8 N2 Typed/Full и2 N6
Dimensions schema2. Первая проба четырёх A/B-пар совпадает по CSV/native/model/
features. ASan-повтор с обоими N6 протоколами и auxiliary parity принят по34 тестам
на отдельном срезе root818dd80/Pulse3accbed. Подробная
[квитанция соседней ветки](https://github.com/aicommunity/Nmsdk/blob/6a98929759d0af8fcdc2f1fc980e9e7ca467e942/Docs/StructTrain/TimeLearner/NativeFixtureRevisionProviderAsanVerification.json)
не распространяется автоматически на последующий matched-omission код.
Это изменение fixtures, не алгоритма.


## Параллельная подготовка: matched omission и Windows

На ветке matched omission приняты35 selector tests,2 capture boundary tests,
10 regression capture/codec tests и10 native controls: два separated Valid,
четыре coupled Ambiguous, четыре stop/edit без assignment. Normal55 и
последующий native10 —57 уникальных проверок; отдельный
[ASan57](MatchedOmissionAsanVerification.json) прошёл на M40, detect_leaks=0.
Новый [независимый reader](MatchedOmissionReader.ru.md) прошёл11 тестов и
повторно пересчитал10 real groups, не вызывая C++ и не создавая новых симуляций.
Raw данные, закрытые leases и source hashes доступны в Git.

Это ещё не подключённый Train measurement path: перед интеграцией нужно
[разрешить различие full-trace и собственного окна](MatchedOmissionTrainingIntegration.ru.md).
Неоднозначные группы не повышены до Valid. CapturedReferences, bounded search,
final verification, полный composite export/import и научная матрица остаются
в работе. Ни тест reader, ни отсутствие ошибок ASan не доказывают классификацию.

Подготовка Windows .14 выполняется независимо в частном каталоге worker.
Последняя полная компиляция root818dd80/Pulse3accbed вернула0, но штатный
backend отверг запуск из-за дочернего процесса неизвестной identity.
[Сохранённый отказ](https://github.com/aicommunity/Nmsdk/blob/6a98929759d0af8fcdc2f1fc980e9e7ca467e942/Docs/StructTrain/TimeLearner/WindowsDomainBuildRejectionVerification.json)
не отменён; scientific worker не принят. Новые18 portability checks теперь
выполняются отдельным A6, описанным ниже. Последующая короткая проверка quiescent build имеет отдельный
результат и не переписывает этот отказ. Пользовательский C:/Projects/Nmsdk
в эти изменения не включён.


Усиление JSON identities/dimensions reader затем прошло20 тестов (11+9 новых)
и replay тех же10 groups на tool rootd37b01d2. Критерий и ответы моделей не
менялись. [Scoped receipt](MatchedOmissionReaderDimensionsVerification.json).


Windows .14: отдельная bounded попыткаa3 подтвердила `ninja: no work to do`,
но снова была отклонена штатным backend: после main exit остались conhost.exe
и powershell.exe. Обе process identities теперь сохранены; a2 PID9556 задним
числом не идентифицируется. Три runtime inventories не изменились; native tests
не запускались. [Квитанция a3](WindowsDomainNoopBuildRejectionVerification.json).
Installed VS18 VsDevCmd содержит guarded async PowerShell telemetry. Это
обоснование следующего контролируемого ENV изменения, а не доказательство
командной строки прошлого PID. A4 проверяет только процесс-локальный штатный
флаг VSCMD_SKIP_SENDTELEMETRY=1 до vcvars; backend/его guard не ослабляются.
A4 не исполнила child: штатный preflight отказал из-за нехватки памяти при
заявленных4GiB+256MiB reserve.
[Квитанция A4](WindowsDomainMemoryPreflightRefusalVerification.json).

Отдельная A5 затем прошла штатный backend: completed/valid, return0, все owned
процессы закрылись, оставшихся descendants нет. Ninja подтвердил no work,
три runtime и source closure не изменились. Явно изменены два условия: штатный
VS ENV flag и отдельная256MiB quota только для warm/no-op диагностики, обоснованная
ранее измеренным95MiB peak. Это не приёмка полной сборки с4GiB, не доказательство
единственной причины прошлых descendants и не scientific worker admission.
[Квитанция A5](WindowsDomainBoundedBuildA5Verification.json).

18 native portability checks запущены отдельным A6 после свежего preflight:
свободная RAM10915479552 bytes,57 прежних owned JobObjects отсутствуют,
source/runtime818dd80/Pulse3accbed совпали с accepted warmA5.
[Точное задание Windows18](WindowsDomainNative18PreparedManifest.json)
содержит task/worker/plan identity,18 test IDs, cooperative DLL capture и лимиты
3GiB+256MiB reserve. Первые13 cases прошли; terminal/evidence ещё ожидаются.
Повторной сборки и обновления исходников/runtime не было, пользовательский
C:/Projects/Nmsdk не затронут. Это отдельный portability gate, не FCC/matched
implementation и не общий scientific worker admission.

## Portable witness и single-owner setter: подготовка 8 ноября

[Production portable witness](MatchedOmissionPortable.ru.md) сохраняет всю N+2
группу, исходные/applied интервалы, policy/budgets, canonical primary и свежий
assignment. Метод назначения v1 не изменён; в Train он пока не включён.
На M40 tool root82de17c/Pulsee2c6311 подтверждены77 C++/40 Python;
исходная ошибка обёртки и независимая recovery-проверка описаны ниже.
На Elder root461cbcc/Pulsee2c6311 завершены80 C++/43 Python, первичные данные
и независимая проверка опубликованы. [Точные попытки и bindings](MatchedOmissionPortableJobs.json).

[Сверка calibration/PostTune](CalibrationPostTunePropertyReconciliation.ru.md)
исправила44 устаревших формулировки реестра, сохранив их исторические поля;
167 остальных записей неизменны. Это source/metadata review, не повышение
runtime acceptance.

Отдельный tiny patch Pulse2c3eb8d закрывает legacy SynapseResistanceStep writer
для native-owned модели. Прежнее значение возвращает true без child writes;
изменение отклоняется. Legacy N0/N1 сохраняют прежнюю семантику. Подготовлены10
real-storage ownership/lifecycle/import cases, включая zero-packet ExternalStop
frozen diagnostic import без фиктивного сертификата; все10 прошли на M40/ASan.
[Контракт и ограничения](NormalizationPropertyContracts.ru.md).

ClDesc двух learner в Bin918ae5e уточнены: Step — абсолютное сопротивление
дополнительных синапсов legacy N0, а не приращение. Изменены только Header и
Description; [XML semantic check](ResistanceStepClDescTextVerification.json)
подтверждает неизменность всех остальных значений. Завершённые codec gates
использовали Bin3b9ca28; новый отдельный guard gate использует Bin918ae5e.

При подготовке отдельной копии Bin исправлена унаследованная относительная
core.worktree-привязка только новой копии. Две созданные этим подготовительным
вызовом XML-копии из служебного каталога удалены после точной сверки с изолированной
копией и Git; старые файлы сохранены.
[Operation receipt](TimeLearnerBinWorktreeBindingCorrection.json).

Новый отдельный ASan job `s07-native-step-m40-a1` использует root4bfab020,
Pulse2c3eb8d/Bin918ae5e: все90 C++/43 Python приняты;28 CSV A/B совпали.
[Independent receipt](NativeResistanceStepAndCodecM40A1Verification.json)
подтверждает29 source hashes, actual loaded files,327 resource files по Git,
неизменность обоих runtime и16 kernel/lease closures. Сохранены11 исходных
operational needs_review и22 notices; научного PASS из них не создавали.
Проверки прежних снимков не переносились автоматически на guard.
Исходные этапы1–12 и научная матрица остаются частично выполненными;
только этап0 полностью принят.

После восстановления связи M40 проверен по исходному binding: все77 C++ и40
Python прошли,6 portable/10 fixture readers успешны,28 CSV совпали побайтно.
Original orchestrator terminal=false сохранён: в one-off worker переменная
runtime inventory была перезаписана baseline CSV bytes. Отдельная проверка
before/after/on-disk подтвердила неизменность runtime/resources, source hashes,
actual loaded files и kernel/lease closure.
[Recovery receipt](MatchedOmissionCodecM40A1RecoveryVerification.json).
Это приёмка численных/codec результатов с отдельно сохранённым отказом
обёртки, а не объявление исходного pipeline успешным.

На Elder normal80/Python43 завершены успешно. Evidence commit
`9cf4bfa0fcabe605dd83faa0d9fc188f67d52273` и
[независимая квитанция](MatchedOmissionCodecElderA1Verification.json) подтверждают
точные test IDs, шесть portable/десять fixture readers, 28 побайтных CSV A/B,
source/runtime/resources hashes и kernel/lease closure. Исходные десять
operational needs_review и двадцать provenance notices сохранены; их не
переименовывали в научный PASS. Первоначальный transport failure также сохранён.

Пользователь подтвердил, что отдельная ранняя вершина допустима при небольшом
остаточном влиянии на позднюю. [Уточнённая семантика и ограничения следующего
метода](PeakAssignmentClarification-2026-11-08.ru.md) исключают автоматическое
применение influence-exclusive v1 как Train-критерия.
