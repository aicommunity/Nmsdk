# Состояние реализации TimeLearner — 07.11.2026

**Полностью принят только исходный этап 0. Этапы 1–12 выполнены частично.**
Полный объём сохраняется в [плане](RefactoringPlan.ru.md). Технический PASS,
merge и научная разделимость — разные утверждения; 8/8 не является условием
завершения. Эта страница заменяет накопительную сводку. Исторические попытки
и отрицательные результаты сохранены в Git и отдельных receipts.

## Проверенные срезы

| Срез | Подтверждено и ограничения |
|---|---|
| Принятый root develop | `2fbf982ffe6a5882e03dfdf6438eac042161fc12` |
| Принятые PulseLib / Bin / Rdk | `0ec9193e6620ae2439329eece5ecd6d6f167c70a` / `fc67a3b0958e8becdfbe1cd3f0e4e054d966d54f` / `10e9d05aa658dd2203c89bc84ba9166595b50014` |
| Общий ASan SDK | root2e061/Pulse12d: 133/133; не подтверждает последующие изменения |
| Baseline recovery SDK | root84d6/Pulse416: normal118 и адресный ASan19 приняты; stock Train/evaluation завершены |
| Fair-domain compiled SDK | root36f598/Pulse8f057: normal137/137 и адресный ASan38/38 на M40; общая приёмка в develop ещё открыта |
| PulseLib documentation HEAD | `2f6b57253bd7ae380a19320ef3835a2701cb4d30`; Core совпадает с tested8f, но receipts сохраняют фактический SHA сборки |
| Worker-limit Python SDK | rooteae3: 26/26 на каждом сервере; не проверка нейронного обучения |

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

Новая matched серия s07-stock-fair-domains-normal-a2 выполняется после шести
design checks, preregistration и восьми cold preflight. На момент
[timestamped наблюдения](FairDomainStockProgressObservation.json) завершены6/8
Train, все InvalidObservation; тот же worker жив по PID/start ticks.
Полный verdict и последующая оценка новых моделей ещё отсутствуют.
[Оценка и полный render](FairDomainStockEvaluationJobs.json) поставлены в очередь;
ожидающий процесс подтверждён живым, native evaluation ещё не началась.
Допуск требует полного closure Train, released lease и успешного аудита серии.
[Условия и история](FairDomainStockComparisonJobs.json): исходный NSPNeuronGen
без дополнительной LTMembrane, C-trim/PostTune/калибровка выключены. Старые
baseline ответы не подставляются вместо результатов новой серии.

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

| Этап | Подтверждено в ограниченной области | Что мешает закрыть этап целиком |
|---|---|---|
|0. Начальное объединение|Принято; последующие изменения объединяются children-first через merge commits|Новые features проходят свою приёмку отдельно|
|1. Доказательства и параметры|Есть реестры, исторические anchors и source/property review|Завершить semantic review всех публичных параметров, режимов и прежних аудитов; устранить remaining unknowns|
|2. Сборки/runtime|Изолированные сборки, manifests, process ownership; приняты scoped gate/output и archive restoration fixes|Полная build/resource/fault matrix, общий срез и воспроизведение closure; не считать учёт ресурсов OS quota|
|3. Наблюдения/scorer|Строгие native observations, completeness/ID/finite checks и versioned metrics; legacy numeric reader не достраивает доказательства|Все legacy adapters, режимы/физические профили и единый итоговый verdict для всей области|
|4. Lifecycle/storage|Есть реальные native fixtures, graph/response readback и проверки boundaries|Полная fresh/reuse/Copy/Load/Build/growth/heterogeneous physics матрица и все compatibility paths|
|5. Export/import|Есть completed/stopped state transport, native storage/graph archive, boundary continuation и fresh destination controls|Все варианты моделей/физики/связей; полный mid-probe checkpoint не обещается|
|6. Общий контроллер|Общий native service, configured controller и topology adapters существуют|Принять оставшийся общий срез, завершить legacy/V2 A/B, дублирующиеся hooks и multirate verification|
|7. Алгоритмы|Measured bounded L/Ns/Rs search, N0 repeats, финальная проверка; C0 API принят, bounded C-search — кандидат|Полная bounds/quantization/nonmonotonicity/invalid-probe/physics/reset матрица, приёмка кандидата и stock measurement recovery|
|8. Recognition/PostTune/calibration|Versioned solo/recognition states, transactions, measured threshold confirmation и frozen controls работают в проверенных случаях|Все PostTune/inhibition/reset modes, commit/rollback/interruption и независимая оценка|
|9. Скрипты|Корневой пакет и CLI работают; migration222:220 retired+2 moved; семь исторических XML patchers приняты без wrappers|Остаются22 AsymRm Python и прочие инструменты; limited Bin inventory126 не равен полному глобальному inventory|
|10. Запуск/provenance/publish|Есть owned processes, leases/budgets, fail-closed publisher и реальные coordinator controls|Полная effective-factor attestation, scheduler/cancel/recovery/publication fault matrix; declarative ConditionSpec binding её не заменяет|
|11. Научные проверки|Августовские saved-state replay и настоящий cold Train→Test воспроизвели4/8,5/8,6/8; есть N2 controls и временные отчёты|Завершение оценки нового V2 stock среза, legacy/V2 A/B, target в каждой позиции, order/ITI/reset и independent frozen matrix|
|12. Документация|Поддерживаемые сводки согласуются с receipts; исходные отчёты сохранены|Сквозная актуализация root/PulseLib/Bin/config/ClDesc/defaults и завершение миграции ссылок|

## Путь к итоговым выводам

1. Завершить полную новую Train серию, аудит и matched code comparison;
   оценить фактические модели и построить все trial/soma графики.
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
legacy/V2 матрица остаётся открытой. Migration222 (220 retired+2 moved) не равна
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
