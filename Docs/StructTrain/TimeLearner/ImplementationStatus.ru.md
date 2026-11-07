# Состояние реализации TimeLearner — 08.11.2026

**Полностью принят только исходный этап 0. Этапы 1–12 выполнены частично.**
Полный объём сохраняется в [плане](RefactoringPlan.ru.md). Технический PASS,
merge и научная разделимость — разные утверждения; 8/8 не является условием
завершения. Эта страница заменяет накопительную сводку. Исторические попытки
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
установлены точные state/model hashes; отдельные full/omit/single ещё требуются.

Исправлен отдельный [дефект повторного учёта общей вершины в сертификате](AssignedVertexCertificateGuard-2026-11-07.ru.md):
контролируемый counterexample воспроизведён до изменения; после него23/23
production C++ unit checks прошли на Elder/normal и M40/ASan. Диагностическое
чтение schema1/2 сохранено. Полный SDK Elder теперь собран:23/23 нового
CMake target,21/21 native storage/training и7/7 reader checks прошли.
[Новый native-контроль с графиками обеих сом](AssignedVertexNativeControlReport-2026-11-07.ru.md)
подтверждает отказ общей вершины. ASan SDK batch M40:build и23 unit прошли,
но physical21 прерван timeout на последнем case; без финального JUnit и runtime
capture группа не принята. Неуспешная попытка сохранена целиком, начат отдельный
job для shared-vertex и Branch20k с независимыми capture и бюджетами.
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
|9. Скрипты|Корневой пакет и CLI работают; migration238:236 retired+2 moved; последние16 LTZ drivers приняты обоими серверами без wrappers|Остаются22 AsymRm Python и прочие инструменты; limited Bin inventory126 не равен полному глобальному inventory|
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
legacy/V2 матрица остаётся открытой. Migration238 (236 retired+2 moved) не равна
всему inventory; остаются22 AsymRm Python и другие инструменты. Полная scheduler,
recovery, publication fault matrix и effective-factor attestation не закрыты.
Компонентные страницы PulseLib актуализированы.
[Пять свойств и общие тексты двух ClDesc](ClDescControllerContractReconciliation-20261107.ru.md)
сверены с исходниками и приняты в Bin/root develop; изменены только Description.
Compiled receipts сохраняют прежний Bin37ff: действующие runtime не обновлялись.
Все остальные ClDesc/config/defaults ещё не сверены. Исторические primary не удаляются ради компактного Git.

Предыдущая накопительная сводка сохранена в
[Git](https://github.com/aicommunity/Nmsdk/blob/b2517a3576f949c12acb402ce83ab595ebcbf0b1/Docs/StructTrain/TimeLearner/ImplementationStatus.ru.md).
Неудачные проверки остаются evidence своего среза, не переписываются под PASS.


[Legacy ISI-template analyzer](IsiTemplateValidationNormalVerification.json):
корректный baseline воспроизвёл4 regression failures при5 passing controls;
исправленный Pulsefe382a0 прошёл12/12 на M40. Baseline/fixed primary и source
hashes опубликованы. [Адресный ASan](IsiTemplateValidationAsanVerification.json)
того же root87/Pulsefe также прошёл12/12 на M40; libasan фактически загружен,
detect_leaks=0. Второй сервер и весь analyzer scope ещё открыты.
MatchMode1 сравнивает вход с шаблоном, не доказывает ответ нейрона и не объясняет
InvalidObservation native V2 stock Train.


[Native channel diagnostics](NativeChannelDiagnostics.ru.md): root18d4d/Pulsefe,
M40:12 native controls,4 реальных Off/On пробы и18 readers прошли. Observer
не изменил CSV и исходную волну. Записаны фактические Exc/Inh/Feedback/LT:
до второго входа Classic имеет2 LT events, Branch1. Это не новая классификация
или исправление assignment. Адресный ASan того же SDK также прошёл12 native
controls,4 пробы и18 readers; libasan подтверждён в5 процессах, detect_leaks=0.
[Совместный channel render](NativeChannelJointVisualVerification.json) завершён:
5 сом,216 views; четыре выбранных PNG просмотрены по отдельности и сверены с Git.
Второй сервер и вся interruption/intervention/profile матрица нового режима
остаются открытыми. Первая compile failure сохранена в evidence.


[Одноимпульсная диагностика](SinglePulseCharacterizationContract.ru.md):
native-кандидат Pulse302124b/rootb5cfae4 прошёл на M40
[37/37 native функций и13/13 readers](SinglePulseCharacterizationNativeVerification.json)
без skips. Проверены Classic/Branch, N=1/2/4/6,2000/20000Гц, физический
selector≠0, точное восстановление burst stimulus/soma после диагностики и
ошибок callbacks, JSON roundtrip и запрет training certificate для schema4.
Все267 members трёх архивов и779+777+364 source hashes сверены с Git;
группы закрыты, leases released. Первая попытка16/21 с20 assertions о коллизиях
имён сохранена. Вторая дала37/37, но wrapper ошибся каталогом readers:
исправлен только путь,13 readers выполнены отдельно без повторения native37.
Оригинальные failed terminals не переписаны под PASS.
[Адресный ASan](SinglePulseCharacterizationAsanVerification.json) root5d0b80/Pulse302
прошёл37 native,4 Console и42 Python checks на M40; Elder и полный
cancellation/connected/replacement scope остаются открытыми. [Console job4 и paired stock study](SinglePulseCharacterizationConsoleVerification.json)
root5d0b80a прошли четыре реальные пробы и42 Python tests на M40. Один импульс
дал3 положительных максимума Classic Soma1 и2 Branch Soma1, при2/1 LT events;
первые180 samples до второго burst onset совпали с исходной пачкой.
[Научный отчёт](SinglePulseCharacterizationScientificReport-2026-11-07.ru.md)
отделяет это наблюдение от причинной гипотезы и классификации. Исправленный
builder воспроизвёл baseline digest defect и прошёл положительные controls.
Это ещё не исправление assignment и не новое успешное обучение.


[Single-pulse temporal report](SinglePulseCharacterizationVisualVerification.json)
завершён:5 сом,193 views,583 cache files на M40; четыре выбранных PNG
сверены с Git и просмотрены индивидуально. Слабый Branch максимум требует
локального Y; общий масштаб контекстного окна для него недостаточен.
Полный ручной просмотр cache не заявляется. Это не новая классификация.


[Storage FeedbackGain](StorageFeedbackProfiles.ru.md): rootb54330482/Pulsed09613c,
M40 normal18/18 native и13/13 readers без skips. Проверены inherited custom
профили, сохранность prototypes/live instances, body/LT разделение, growth,
Build/Reset/XML с индивидуальными Rs/C, invalid/collision и реальная динамика
Classic/Branch2000/20000Гц. Все161 primary members и781 source hashes сверены;
процессы закрыты, lease released. Engineering threshold1e-6 одинаков в controls;
это не causal intervention в stock0.0117 и не новое обучение. ASan/второй сервер,
полная матрица и baseline-equivalent stock reconstruction открыты.


[Effective graph delta auditor](FeedbackInterventionContract.ru.md) проверен
на M40:10/10 reader controls,11 primary members и368 tool source hashes
сверены с Git. Исходные два actual imported stock graphs привязаны к прежним
Console primary. Разрешены только объявленные image renames и uniform gain;
порог, физика каналов, индивидуальные Rs/C, связи, порядок и частота должны
совпадать полностью. Это data-consistency audit, а не native intervention,
image closure proof, baseline waveform equivalence или научный verdict.


[Inherited-image feedback profiles](FeedbackInterventionContract.ru.md):
rootabf13d2b/Pulse73f0365 прошли M40 normal22/22 native и15/15 readers.
В реальных fixture-моделях original/explicit2 дали одинаковые волны/LT events;
production auditor подтвердил полный effective graph, кроме объявленных image
renames. Для explicit0 сохранены все остальные поля и меняется реальный отклик.
200 primary members и783 source hashes сверены, процессы закрыты/lease released.
Это engineering1e-6 с fixture-морфологией; archived stock0.0117 intervention,
ASan нового API, второй сервер и XML новых образов остаются открытыми.


[Полный physical graph import через feedback images](FeedbackInterventionContract.ru.md):
root8978f104a/Pulse32ea8ae прошли M40 normal24/24 native и27/27 readers.
225 primary members и783 source hashes сверены с Git. Подтверждены individual
C/Rs, native roundtrip, unchanged source, отказ image-gain mismatch и
противоречивому/неполному source XML. Внутреннее наследование gain не ослабляет
обычную archive completeness. Процессы закрыты/lease released; пять прежних
runtime не изменились. Первая compile failure сохранена отдельно. Candidate
waveform/archived stopped-state intervention не выполнялись; controller
history/certificate не переносились. ASan этого API, Elder и полная матрица
остаются открытыми. Это уточняет этапы4/5/7, не закрывает их целиком.


[Установка полного графа в свежий контроллер](PreparedModelInstallNormalVerification.json):
rootc5a32/Pulse2726 прошли M40 normal26/26 native и29/29 readers без skips.
234 primary members и785 source hashes сверены; процессы закрыты/lease released,
семь прежних runtime не изменились. Fresh controller не наследует references,
search/history или certificate; full graph и индивидуальные параметры сохранены.
Это не waveform proof и не новое обучение. Console profile protocol пока не
подключён; ASan этого API, Elder и полная матрица открыты. Этапы4/5/7 целиком
не закрыты. Failed-a1 сохранён отдельно.


[ASan одноимпульсного native/Console контура](SinglePulseCharacterizationAsanVerification.json):
root5d0b80a/Pulse302124b, M40:37 native,4 реальные Console пробы и42 Python
проверки без skips. Все618 primary members и781 source hashes сверены с Git;
libasan загружен в пяти native процессах. Группа закрыта/lease released, два
предыдущих ASan runtime не изменились. Producer задаёт detect_leaks=0; runtime
manifest не сохраняет ASAN_OPTIONS, поэтому эта настройка подтверждается
архивным producer, не process environment readback. Это не leak check,
не проверка последующих storage/graph/prepared-owner API и не новое обучение.
Упоминания «ASan открыт» выше для single-pulse среза заменены этой адресной
проверкой; Elder и остальная матрица остаются открытыми.


[Profile probe admission](FeedbackProfileProbeAdmissionVerification.json): root367b811,
M409/9 Python tests без skips на archived Classic/Branch sources. Проверены
schemas2/3/4 compatibility и schema5 builder/negative factors. Все7 primary members
и432 tool hashes сверены с Git; процессы закрыты/lease released. Новый Console
profile path подключён в коде, но compiler, execution auditor actual records,
paired baseline waveform и actual gain0 intervention ещё не проверены.


[Actual stock feedback intervention](FeedbackProfileConsoleNormalVerification.json):
root844b278/Pulse1f97, M40 normal26 native +29 прежних readers; все12 Console
проб завершены/аудированы,4 baseline waveform pairs exact. Все1555 members и789
source hashes сверены с Git; восемь прежних runtime неизменны, группа закрыта,
lease released. В initial11 readers9 admission иnegative control прошли, но
positive test после аудита12 проб прочёл JSON array object-only loader; original
terminal остаётся failed. Исправлены только test read; [отдельные2 readers](FeedbackProfileConsoleReaderVerification.json)
прошли без native repeat,9 members/434 tool hashes и1315 неизменных native input
files сверены. Combined scoped gate принят; это не приёмка всего SDK или плана.
FeedbackGain0 устранил дополнительные положительные максимумы в двух выбранных
состояниях при неизменных input/threshold/остальной физике. Это диагностическое
вмешательство, не новое обучение или классификация; менять default physics
либо CapturedPerInput на этом основании нельзя. Отчёт/visual QA продолжаются;
ASan нового API, Elder и полный mode/profile scope открыты.


[Диагностика missing при исходном пороге100](HighThresholdSinglePulseJobs.json)
запущена на M40 из отдельного tool snapshot с прежним immutable compiled SDK.
Это selector архивных training100/Retry состояний, не threshold intervention.
Запланированы4 actual burst/single probes; результат ещё не принят. Временные
[отчёты feedback12](FeedbackProfileTemporalReportJobs.json) строятся параллельно;
5 chart controls прошли, ручная visual QA остаётся открытой.


[Feedback temporal report](FeedbackProfileVisualVerification.json) завершён:
30 trial/soma pairs,1213 views+2 matched-tail details,3669 cache files проверены,
полный cache403646846B на M40. В Git6 выбранных PNG1468877B; все6 просмотрены
индивидуально. Сверены70+8 primary members и373 unique tool hashes; оба workers
closed/leases released. Ручная QA всего cache не заявляется. [Читаемый научный
отчёт с изображениями](FeedbackProfileScientificReport-2026-11-07.ru.md) отделяет
causal intervention от обучения/классификации и показывает изменение LT Output.

[Relative clock comparator](RelativeClockAlignment.ru.md): исправлен actual
replay false failure при source begin855.486с. Signals/model совпали точно;
ошибка была только в учёте cancellation roundoff. Пять actual-corpus controls
прошли на M40,9 primary/437 tool hashes/20 input bindings сверены. Допуски
обучения и физика не менялись. Исходный high attempt сохранён failed; Branch2
уже выполнены, Classic2 ещё не выполнены. Это не новый успешный Train.


[Training100 burst/single diagnostic](HighThresholdCombinedVerification.json)
завершён:2 новые Classic пробы и2 unchanged reused Branch. Сверены633 primary,
375 tool hashes и2088 Branch bindings; group closed/lease released, runtime
не изменился. Exact Train replay иfirst-prefix совпадение подтверждены в обеих
топологиях. Одиночный импульс имеет1 maximum на выбранной соме, штатный burst —3
на4 inputs. Механизм missing этим ещё не установлен. Mechanical analyze_pair
A/B сохранил все поля двух прежних low summaries. Нового обучения нет. [Отчёт](HighThresholdSinglePulseScientificReport-2026-11-07.ru.md),
полный temporal cache/selected QA ещё строятся.


[Training100 temporal report](HighThresholdTemporalVerification.json) завершён:
4 cases/10 trial-soma pairs,393 views,1187 cache files проверены; cache131740593B
на M40. В Git6 PNG1381204B, все6 просмотрены индивидуально. Сверены29 primary
members/375 tool hashes; group closed/lease released. [Читаемый отчёт](HighThresholdSinglePulseScientificReport-2026-11-07.ru.md)
показывает single peak иburst3/4 иявно отделяет гипотезу наложения от доказанного
механизма. Визуальная приёмка всего cache и новая классификация не заявляются.


## Последние принятые изменения 07.11

[Размерная матрица single maximum](SingleImpulseMaximumDimensionMatrix.ru.md)
подтверждена normal иASan: по9 native IDs и10 readers, по16 физических условий
Classic/Branch ×N1/2/4/6 ×2000/20000 и6 fault captures. Это диагностический
одиночный импульс, N1 fixture/threshold100. Реальное обучение полной пачкой,
N0/полная physics matrix этим не закрыты; Console ASan принят отдельно ниже. Последний ASan
worker завершён, whole group closed/lease released; повтор не запущен.

[Миграция16 LTZ drivers](LtzDriverRetirement.ru.md) вошла в Bin/root develop
через merge commits. Production history238 и restored-path negative прошли
на обоих серверах. Все архивные исходники238 записей и288 actual tool hashes
каждого worker сверены независимо; configs/models/primary не изменены.
Остаются два LTZ copy helpers с внешними callers и17 Python tools этого
каталога, другие группы scripts также требуют review. Stage9 partial.

Уточнение пользователя о слившейся общей вершине применяется как консервативная
рабочая политика: её нельзя выдать за два независимо подтверждённых пика
закреплённых импульсов. Это unresolved assignment, а не доказательство
PhysicalInfeasible или отсутствия вклада импульса. Научная неопределённость
сохранена; одиночный отклик с меньшими добавочными максимумами — другой случай.
Все исходные этапы1–12 по-прежнему частичны, цель полного плана активна.


[ASan Console replay4](SingleMaximumConsoleASanVerification.json) принят:
4 actual processes,5 design tests, exact archive/A-B traces, actual libasan maps,
459 compact primary members/384 tool hashes/424 manifest artifact bindings.
Runtime неизменен, whole group closed/lease released. Это одиночная диагностика,
не Train, classification или полная принадлежность пиков пачки. Предыдущие
указания об открытом адресном ASan Console gate заменены этим receipt.


08.11: две раздельные ASan-проверки (shared vertex и Branch20k) прошли,
но общий freeze gate отклонён: runtime изменился только в трёх EventsLog paths.
[Receipt](AssignedVertexASanSplitVerification.json). Исправление владельца
тестового WorkDirectory прошло4 native ASan проверки; обе runtime неизменны,
контрольная waveform побитово идентична. [Receipt](TestLogOwnershipASanVerification.json).
Это не приёмка Windows-пересборки или полного этапа2.
Новая интегрированная ASan-сборка schema6 выполняется на M40; параллельно
готовятся14 диагностических high-threshold проб по точным состояниям
[постановки](HighThresholdSubsetStudyDesign.json), без запуска Train.

Подготовка high-threshold завершена на M40:14 jobs, точные selectors Classic0
и Branch2, source files сверены с исходными Git manifests. Ни одной новой
native-пробы подготовки не запускала. Summary Branch67,9MB потребовал явного
лимита128MiB на member при прежнем общем лимите512MiB; исходный отказ сохранён.
Повторные истории обучения в новый компактный архив не включены, остаются
ссылки на исходные Git commits и полные file bindings.
[Задания подготовки](HighThresholdSubsetPreparationJobs.json).

Компактный пакет подготовки767f579e передан через Git и независимо сверён:
55 members,1300 bindings исторических файлов,14 jobs; архив1,11MB без
повторных source histories. [Receipt](HighThresholdSubsetPreparationVerification.json).
Фактические high-threshold subset пробы ещё не запускались.


Интегрированная ASan-проверка b711/Pulse609 завершена:71 unit,10 physical
и7 reader checks прошли. Runtime текущей и прежней сборок неизменны,
все группы закрыты и reservation снята. Evidence dae5697b (494 members,383616B);
это не Console gate того же задания и не полная приёмка этапа7.
После этой проверки запущен [high-threshold replay](HighThresholdSubsetStudyJobs.json):
сначала обе full-пачки сравниваются с опубликованными историческими трассами.
Без совпадения к остальным условиям перехода нет. Это диагностика stopped
состояний, без Train, классификации и сертификата закреплённого пика.

ASan evidence dae5697b независимо сверён:494 members,138 source hashes,
81 JUnit cases и8 restoration packets. [Receipt](IntegratedSubsetASanVerification.json).
Первая контрольная high-threshold full-проба Classic завершена: recorded input
и все soma samples точно воспроизвели историческую пачку; относительные clocks
совпали с ограниченным учётом roundoff. Остальная серия ещё выполняется.

High-threshold A1 остановлен проверкой самого worker: base model_revision
сравнивался с expected effective revision Branch. При этом native prepared
содержит правильный effective7ae9b857, initial/base96ea48df также правильный.
Это ошибка orchestration assertion, не изменение модели. A1 closed/released.
A2 проверяет обе оси раздельно и повторно использует два завершённых full-control
process packets только после проверки исходных и скопированных manifests.
Остановка A1 не переоценивается как успешное выполнение серии.


Рендер c2656f39 на опубликованном Console corpus принят:6 cases/12 figures,
400 source hashes сверены с Git,25 archive members проверены; две выбранные
overview-фигуры прошли визуальную QA. Caption и source_conditions различают
base и measured/effective model revisions. Primary не менялись, новых native
симуляций этот рендер не выполнял. [Receipt](StimulusSubsetTemporalVerification.json).
High-threshold A2 подтвердил обе исторические full-пачки точно и завершил
первые две omit-пробы Classic; оставшаяся серия выполняется.


High-threshold subset A2 завершён:14/14 условий, обе full-пачки точно
воспроизводят исторические данные, отсутствуют heartbeat/model/restore errors.
Повторная проверка и публикация всего primary выполняются; новый научный
отчёт с графиками ещё не готов. Train, классификация и assigned-peak certificate
в этой серии не выполнялись.
Потоковая упаковка ffb35ddf принята на реальном corpus:16 tests,700 файлов,
6 native/manifest audits,104,4MB →1,26MB. Все inner hashes сверены с исходным
Git primary; [receipt](StreamingPrimaryVerification.json).
