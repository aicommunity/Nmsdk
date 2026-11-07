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
при четырёх фактических импульсах. Причинная физическая интерпретация и
исправление assignment ещё открыты.
[Точный replay двух low/Retry candidate](StockWaveReplay.ru.md) после полного
import/Reset воспроизвёл все soma/input samples и ambiguous. Шесть серверных
проверок прошли. [Первый импульс](StockFirstPulse.ru.md): до второго onset
Classic уже имеет3 положительных максимума, Branch —1; четыре адресных tests
прошли. Это ограничивает предположение «один максимум на импульс», но не
определяет правило выбора response wave. Replay cache251 view завершён;
causal waveform decomposition и отдельные single-pulse controls открыты.

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
Оригинальные failed terminals не переписаны под PASS. ASan, Elder и полный
cancellation/connected/replacement scope открыты. [Console job4 и paired stock study](SinglePulseCharacterizationConsoleVerification.json)
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
