# N1 geometry/Rs fairness — 11.11.2026

Основание: stock N4 Branch SDK22/Pulse165 завершился valid budget_exhausted после128 search probes;64candidate states остались на input2 и преимущественноL2, timing residual около−0.231s. Полные данные сохранены в [исходном отчёте](https://github.com/aicommunity/Nmsdk/blob/1cdc0f366/Docs/StructTrain/TimeLearner/StockCold7MeasuredPilotOutcome-20261111.ru.md).

Подготовлен production-controller regression `BoundedTrainingN1GeometryFairness.ValidDenseResistanceMeshDoesNotStarveOtherLengthsInEitherRecoveryMode`. Он использует настоящий BoundedTrainingSession/ProbeRecorder, валидные управляемые unit observations и native-domain interface; это проверка порядка решений, не доказательство физической сходимости. Проверяет Classic/Branch, RetrySameCandidate/AdvanceUnassignedBurst, длины3/4 в конечном бюджете и неизменность anchor.

Baseline root содержит новый test и исходный Pulse165. Следующий root commit закрепляет исправленный Pulse: один unissued Rs на legal geometry за проход независимо от invalid-recovery policy, повторная native domain assessment остаётся обязательной. CapturedPerInput, bounds/tolerances, reference/final verification, Rdk lifecycle не меняются. Branches созданы от develop с --no-ff dependency merges; rebase/squash/cherry-pick не использовались.

Проверки before/after и реальные native A/B ещё не выполнены. До их приёмки рекомендация V2 и завершение этапа7 не заявляются.
