# Состояние реализации TimeLearner — 06.11.2026

**Полностью принят только исходный этап0. Этапы1–12 выполнены частично.**
Эта сводка описывает текущее состояние; исторические подэтапы и их численные
итоги следует читать по неизменяемым receipts. Наличие кода, отдельный PASS,
merge и научная разделимость — разные утверждения. Требования целиком сохранены
в [плане](RefactoringPlan.ru.md); результат8/8 не является условием его завершения.

## Принятый код и проверяемый срез

| Источник | Состояние |
|---|---|
|Root develop, проверенная отправная точка этой сводки|837b0c7aad7c6d1973325319a750ce8da8f0f070|
|PulseLib в develop|0ec9193e6620ae2439329eece5ecd6d6f167c70a|
|Bin в develop|3d5fc67c33f7be9ad3806db0b00b9d92588049bb|
|Rdk в develop|10e9d05aa658dd2203c89bc84ba9166595b50014|
|Проверяемый compiled SDK|Root2e0618110a9abb48b94f6edc6b63c51f829ec810 / Pulse12d8c8a41c998ae1516496f716a0ae0f3d312b3e; ещё не общий принятый C++ срез|

[Матрица возможностей](ControllerCapabilities.ru.md) отделяет принятые API от
кандидата: N0 repeats и native learned-state import уже реализованы и адресно
приняты; автоматический bounded C-search и часть общих lifecycle hooks находятся
в кандидате. Legacy SyncCapacitanceTrim>0 отклоняется обоими native путями;
новый C-search задаётся отдельной декларацией. Версии Controller, ModelSpec,
cold configuration, learned package, observation и scorer не взаимозаменяемы.

На кандидате normal304 и адресные ASan8 прошли. Полный ASan lifecycle A3
выполнил133 cases:132 passed,1 assertion failure при записи файла в отсутствующий
output/native. [Исправленный production gate](NativeGateOutputDirectory.ru.md)
проверен тем же оригинальным тестом на прежних normal/ASan binaries и принят.
A4 остановилась до C++ из-за неполного tool snapshot; свежая A5 использует
согласованный tool bb288399bdb66aaadb3db7ec5f01c76cd9bd57ae и выполняется отдельно.
До полного verdict, первичных данных и closure это не ASan133 PASS кандидата.

Отдельно подготовлен [общий бюджет невалидных проб](AttemptInvalidObservationBudget.ru.md):
baseline root7cc/Pulse12d и fixed roota2df/Pulse2c7 используют идентичные новые
регрессии. На M40 baseline воспроизвёл превышение бюджета:4 test functions
завершились32 ожидаемыми assertions, Exact и присутствующим сертификатом;
полный34-member primary опубликован и746 source files сверены с Git.
Fixed SDK прошёл4/4 новых и74/74 смежных tests. Native physical/transport gate
дал21/23: два configured Train исчерпали sweeps до ожидаемого сертификата.
Тот же набор23 на прежнем SDK дал те же21/23; все252 CSV и7 precondition
summaries побайтно совпали. Оба первичных отрицательных результата сохранены;
отказы этих fixtures не объясняются budget fix в данном A/B. Это pending общая
приёмка, не merge в develop.
ASan A5 относится к Pulse12d и не
подтверждает новое изменение Pulse2c7. Увеличение бюджета повторов само по себе
не устраняет stock burst ambiguity.

Следующий [configured transport25](ConfiguredTransportPreconditions.ru.md)
прошёл25/25 на той же Pulse2c7: исходные0.02 Train сохранены как diagnostic
stopped-state controls, добавлены отдельные completed controls с явным0.2.
Четыре изолированных old/new процесса подтвердили совпадение28 cold CSV и
двух precondition summaries с абсолютным временем. Старый21/23 verdict не
переписан. Общие23/25 процессы имеют82 отличающихся CSV, поэтому их полная
временная эквивалентность не заявляется. Pending C++ SDK ещё не принят целиком.

Отдельный [WIP candidate recovery](UnassignedBurstCandidateRecovery.ru.md)
добавляет opt-in продвижение bounded search после строго классифицированного
unassigned burst и C++ cold/summary envelope5. Default retry и final all-input
gate сохраняются. Новые C++ tests ещё не выполнялись. Python declaration,
preflight и ConditionSpec binding сначала проверены33/33 tests на каждом сервере.
Следующий primary-classifier срез прошёл48/48 на обоих серверах, включая
исходные stock invalid JSON/CSV и их повреждения; он не подтверждает переходы
поиска. Полный primary audit5 ещё явно отклоняется. M40 SDK Pulse70f прошёл116/116
C++ controls; проверены834 primary members,748 source hashes и process/lease
closure. Все284 CSV прежнего default25 subset побайтно совпали;18 startup JSON
отличаются только StepDuration telemetry. Последующий typed journal Pulsea34
и standalone history auditor ещё не проверены и не входят в этот PASS.
Этот срез не принят в develop; научного результата он не добавляет.

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
|9. Скрипты|Корневой пакет и CLI работают; migration220:218 retired+2 moved; пять XML patchers приняты без wrappers|Остаются24 AsymRm Python и прочие инструменты; limited Bin inventory126 не равен полному глобальному inventory|
|10. Запуск/provenance/publish|Есть owned processes, leases/budgets, fail-closed publisher и реальные coordinator controls|Полная effective-factor attestation, scheduler/cancel/recovery/publication fault matrix; declarative ConditionSpec binding её не заменяет|
|11. Научные проверки|Сохранены августовские4/8–6/8; есть N2 engineering controls и читаемые временные отчёты|Stock cold retrain и legacy/V2, target в каждой позиции, order/ITI/reset и independent frozen matrix|
|12. Документация|Поддерживаемые сводки согласуются с receipts; исходные отчёты сохранены|Сквозная актуализация root/PulseLib/Bin/config/ClDesc/defaults и завершение миграции ссылок|

Подробности принятых изменений: [native model](NativeModelBuilder.ru.md),
[learned-state API](NativeLearnedState.ru.md),
[семантика параметров](ParameterControlContracts.ru.md),
[поиск](ParameterSearchContracts.ru.md),
[пять retired overlay tools и220 records](AsymRmOverlayRetirement.ru.md),
[двухсерверное восстановление primary](PortablePrimaryRestoration.ru.md).

## Последние результаты и их пределы

В проверяемой ветке завершён coordinator schema1/schema2:16/16 production cases,
40 различных actual native phases;1456 CSV сверены попарно. Это эквивалентность
orchestration на объявленных случаях, не независимые научные повторы и не вся
матрица learner. [Исходная приёмка и scope](https://github.com/aicommunity/Nmsdk/blob/ec15c06b1a52917b7a1a49abbddbd095e4b6bb7f/Docs/StructTrain/TimeLearner/PipelineConditionFullMatrixAcceptance.ru.md).

Ранее более широкая восьмипаттерновая N2 LT проверка дала target-detecting5/8:
TP1/FP3/FN0/TN4, со статусом NonSeparable на проверенной сетке порогов.
[Этот результат и его первичные данные сохраняются](ScientificResults-2026-11-03.ru.md).

Два последних N2 LT engineering случая дали каждый TP2/FP0/FN0/TN2 после same-matrix
калибровки на более узком наборе: повторяются один target и один foil.
Этим не устранены прежние FP на близких отвлекающих паттернах. Их четыре предъявления содержат повторные target/foil; они не
являются stock4-input/8-pattern или independent evaluation. Сохранены primary,
модели,46 выбранных PNG и полный воспроизводимый cache214 trial/soma /2620 views.
[Отчёт и пределы visual QA](https://github.com/aicommunity/Nmsdk/blob/ec15c06b1a52917b7a1a49abbddbd095e4b6bb7f/Docs/StructTrain/TimeLearner/PipelineConditionPilotVisualReport.ru.md).

Штатный stock Train пока останавливался на невалидных измерениях: закрытое окно
не гарантирует однозначного burst/peak assignment. Повтор того же кандидата
при большем invalid budget не устраняет детерминированное слияние волн.
Такой результат не доказывает PhysicalInfeasible или общую невозможность
классификации. Следующий научный приоритет — корректное измерение/ограниченное
восстановление поиска в исходной физике, затем cold/frozen сравнение протоколов.

[Готовность экспериментов](ExperimentReadiness.ru.md) задаёт порядок допуска.
Предыдущая накопительная версия этой сводки сохранена в
[Git snapshot](https://github.com/aicommunity/Nmsdk/blob/ec15c06b1a52917b7a1a49abbddbd095e4b6bb7f/Docs/StructTrain/TimeLearner/ImplementationStatus.ru.md).
Её старые слова «ещё не реализовано» относятся к состоянию своего подэтапа.
Исторические измерения и критерии не переписываются под новые результаты.
