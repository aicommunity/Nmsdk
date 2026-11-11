# N1: независимый от recovery обход geometry/Rs — 11.11.2026

Адресная проверка production C++ завершена на обоих Linux workers. Исправленный код проходит98/98 cases на каждом; исходный порядок воспроизводит два заранее объявленных отказа. Это проверка общего контроллера и кодека на управляемых наблюдениях, без физических нейронных моделей; native SDK/Console A/B ещё требуется. Этап7 и весь план не объявляются завершёнными.

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

## Следующая приёмка

Собрать полный SDK с новым Pulse и проверить native linking/serializer/storage и фактические controlled Console cases. Затем native stock N4 before/after с одинаковой математической целью, явными budgets и полными временными traces. Measured-window prediction29frames/segment остаётся отдельной проверяемой гипотезой; source prediction не подтверждает отсутствующий пик. Нового классификатора и нового научного8/8 здесь нет.

Ветки корня/PulseLib созданы от develop с --no-ff dependency merges; история не переписывалась. Merge в develop откладывается до соответствующей native приёмки.
