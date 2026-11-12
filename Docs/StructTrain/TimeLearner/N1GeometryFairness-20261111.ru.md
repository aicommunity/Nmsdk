# N1: независимый от recovery обход geometry/Rs — 11.11.2026

Адресная проверка production C++ завершена на обоих Linux workers:98/98 cases after, два заранее объявленных отказа before. Это controlled-observation проверка контроллера и кодека. Позднее приняты полный SDK build, native linking/storage/serializer и реальные N4 прогоны (см. уточнение12.11 ниже); отдельное физическое before/after сравнение именно этой правки ещё не выполнено. Этап7 и весь план не объявляются завершёнными.

## Дефект и изменение

В stock N4 Branch SDK22/Pulse165 бюджет128 search probes закончился на input2:64 кандидата и преимущественноL2 при временном остатке около−0.231s. [Исходный отчёт и полные первичные данные](https://github.com/aicommunity/Nmsdk/blob/1cdc0f366/Docs/StructTrain/TimeLearner/StockCold7MeasuredPilotOutcome-20261111.ru.md).

`Core/TimeLearner/BoundedTraining.cpp::NextDomainCandidate` раньше включал проход по geometry только для `AdvanceUnassignedBurst`. При `RetrySameCandidate` даже валидные наблюдения удерживали весь Rs-grid одной длины перед остальными длинами. Теперь native N1 выдаёт один ещё не проверенный Rs каждой legal geometry за проход независимо от recovery policy. Пересмотр эффективного domain, полный background/C0/source scope, ограничения банков Branch и deduplication сохранены.

```text
preserve the existing verified-current-candidate shortcut
for each bounded pass over legal geometry/attachment variants:
    obtain a fresh effective Rs domain from the native adapter
    select one unissued legal Rs for this geometry/scope
    apply through the existing edit boundary
    consume the measured anchor/input pair
    continue to the next geometry
if a pass issues no candidate:
    use the existing unresolved/final-verification logic
```

CapturedPerInput, anchorN−1, tolerances, N0, реальные invalid-observation retry/advance правила, reference/final all-input verification и Rdk lifecycle не изменены. Новый обход не утверждает монотонность и не превращает исчерпание бюджета в PhysicalInfeasible. Классы learner и legacy Calculate/Reset/Build остаются прежними.

## Проверенные исходники и результаты

| Область | Before | After |
|---|---|---|
|Root subject|`5ba0a2e81759a28f378117757aa3a5b91f1c57ab`|`40e28802c29014ec8a5af0f8763aa607ad9a986a`|
|PulseLib|`c10206d5e338792d42b58ab28e48e7364b07e481`|`5398a5a563d3e358165fa855cd70236032f5b542`|
|M40/GNU13/Qt6|96PASS+2expected FAIL из98|98/98PASS|
|Elder/GNU11/Qt5|96PASS+2expected FAIL из98|98/98PASS|

Оба Pulse subjects используют один production recovery-кодек; различие before/after — условие обхода N1. Baseline сохраняет исходную логику Pulse165, а не сам его старый SHA после механического выделения кодека. C++ sources целиком компилируются target `Test_PulseLib_TrainingAlgorithms`; тела production-функций в тестовые копии не извлекались. Те же test files включены в полный StorageComponents target.

Два before-отказа: `BoundedTrainingN1GeometryFairness/ValidDenseResistanceMeshDoesNotStarveOtherLengthsInEitherRecoveryMode` и `BoundedTrainingFairDomains/ValidMeasurementsVisitGeometriesIndependentlyOfRecovery`. Первый требуетL3/L4 в конечном бюджете12probes при dense Rs mesh и одинаковую последовательность для обоих recovery modes. Второй сохраняет полный Cartesian mesh и bounds и требует fair порядок в обоих режимах. Остальные96 cases проходят и до, и после. N0, invalid budgets, свежая финальная проверка, shared banks, Rs-domain context, C0/dormant scales, численные residuals/brackets и JSON negative controls входят в этот конкретный набор.

98 case IDs закреплены до запуска в declaration.json:72 прямых TEST в BoundedTraining включают один macro placeholder;4 `TrainingInvalidBudget` macro instances заменяют его, плюс23 cases трёх measured-search файлов. GTest discovery и JUnit сверены с этим независимым списком; env GTEST flags/sharding очищены, filter=* и repeat=1 заданы явно. Набор не заменяет всю обязательную mode/physics matrix.

Время outer owned jobs: M4070.581911s, Elder98.105743s. Actual loaded libraries зафиксированы для каждого C++ executable; все outer cgroups закрыты, leases released. Inner before execution честно сохраняет nonzero_exit, outer pair-test принимает именно ожидаемые два отказа. Число392 C++ executions на двух workers не называется392PASS.

[M40 receipt](ValidationPlans/M40N1GeometryDecisionABA4-20261111/actual-result.json), [Elder receipt](ValidationPlans/ElderN1GeometryDecisionABA4-20261111/actual-result.json). Исходные JUnit, stdout/stderr, cache/flags, loaded files и source/dependency inventories сохранены через Git в `Reports/StructTrain/TimeLearner/N1GeometryDecisionAB-20261111/{M40,Elder}`:38файлов на worker, Git packs128/141kB. Пересобираемые executables и object files остаются кэшем серверов; их hashes сохранены.

## Модульность и исходные ошибки

`CandidateRecoveryEvidenceJson.{h,cpp}` теперь содержит общую production-функцию сериализации решения. `TrainingEvidenceJsonValues.h` содержит единственные общие Text/Number/Count/Parameters/Capacitance helpers; исходный native serializer использует их же. Формат18fields, strict finite/count checks и API через ProbeEvidenceJson.h сохранены. Это устраняет зависимость decision-only тестов от NativeProbe/Rdk header graph. Численные и codec tests прошли; компиляция всего native serializer в новом SDK ещё открыта.

A1 отозван до запуска после проверки toolchain/native-domain flag. A2 завершился compile error из-за тяжёлого native include; он сохранён. A3 реально выполнил98cases: before97PASS/1FAIL, after97PASS/1FAIL. Новый regression тогда уже прошёл after, а единственный after-отказ требовал старого порядка RetrySameCandidate; тест усилен новым независимым контрактом с прежними mesh/bounds assertions. Исходные результаты не переименованы в PASS.

## Уточнение состояния12.11

После исходного controlled gate принят [fresh SDK36/36](ValidationPlans/M40RecordedN4Sdk36A5-20261112/NATIVE36-RESULT.ru.md), Root `448b153f2fea3486ff40f3a626b8f1110b9e3ee2` / Pulse `7b524b8d6c760c5ecfeea432b14b5f9d5045987d`. Два [полных N4 native roundtrip](ValidationPlans/M40RecordedN4NativeRoundtrip2A3-20261112/RESULT.ru.md) дополнительно проверили настоящий import/build/export и response, без нового обучения. Требование собрать и связать полный SDK больше не является открытым.

Исходные full-domain stock Train использовали Root `8362d58f4d6576a0c8b0cc7633270976dff1df7b`, Pulse `1110808f4ad1f67538dadc6fe1d3f097e00c0630`, Rdk `de4134235c0dcb8b91fd9a43b267348ad1a163ca`; [actual runtime closure](ValidationPlans/M40ObservationDomainTrainA1-20261112/fixture/runtime.json). Pulse539 — предок111, а NextDomainCandidate не менялась между этими версиями: старый interleave defect нельзя повторно переносить в открытые дефекты или приписывать им результаты поздних stock запусков. Classic invalid_observation/ambiguous и Branch budget_exhausted сохраняют свои исходные причины; сам ancestry не доказывает отдельный native fairness A/B.

## Следующая приёмка

Текущий physical gate: [before Classic](ValidationPlans/ElderN1ClassicBeforeTrainA1-20261112/RESULT.ru.md) завершился timeout во время финализации без полного model package/typed outcome. Это технический отказ, не доказательство отсутствия решения. [After A2](ValidationPlans/ElderN1ClassicAfterTrainA2-20261112/RUNNING.ru.md) выполняется с побайтно одинаковым native job и теми же budgets. A1 after не начал модель из-за capacity preflight; удалён только объектный кэш завершённых SDK builds, executable/physics/primary не менялись. Полное native A/B остаётся открытым; последующие подготовительные строки относятся к своим снимкам.

Подготовка12.11: обе исходные SDK before/after сохранились на Elder, новые сборки не требуются. Повторный runtime snapshot подтвердил чистые before Root5ba0a2e/Pulsec10206 и executable SHA; production Core diff до afterPulse5f1a4ac содержит только условие interleave в BoundedTraining.cpp. [Before1/1 с8 actual probes](ValidationPlans/ElderN1BeforeCold4Probes8A1-20261112/RESULT.ru.md) принят в техническом scope; outer закрыта/lease released/source unchanged. Все8 исходных графов и CSV побайтно совпали с after characterization на том же Elder. [Полный primary опубликован](N1BeforeColdPrimaryPublication-20261112.ru.md); independent DATA replay и matched Train A/B остаются открыты. [Исходная Classic половина](ValidationPlans/ElderN1ClassicBeforeTrainA1-20261112/PLAN.ru.md) подготовлена с общим controllerfd55a9936. На Elder около2.3GB свободно; последующие Train pairs выполнять с проверкой бюджета диска, сохраняя сжатые primary между сериями.

Остаётся native stock N4 before/after с одинаковой математической целью, явными budgets и полными временными traces, с изолированным объявленным различием порядка обхода. Поздние stock прогоны уже включают и другие controller/recovery изменения и не являются таким сравнением. Measured-window prediction29frames/segment остаётся отдельной проверяемой гипотезой; source prediction не подтверждает отсутствующий пик. Нового классификатора и нового научного8/8 здесь нет.

Ветки корня/PulseLib созданы от develop с --no-ff dependency merges; история не переписывалась. Merge в develop откладывается до соответствующей native приёмки.
