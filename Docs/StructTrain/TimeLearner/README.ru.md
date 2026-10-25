# Структурное обучение TimeLearner

Этот раздел содержит поддерживаемую спецификацию рефакторинга двух компонентов:
Classic (`NNeuronTimeLearner`) и Branch (`NNeuronTimeLearnerBranch`).

- [План и условия приёмки](RefactoringPlan.ru.md).
- [Исходная точка и ход реализации](ImplementationStatus.ru.md).
- [Решения и обязательные контракты](Decisions.ru.md).
- [История и доказательства](Evidence.ru.md).
- [Машинный inventory исходников](source_inventory.json).
- [Контракт наблюдений и оценки](ObservationContract.ru.md).
- [Readback фактического графа модели](ModelInspection.ru.md).

Inventory перечисляет declarations, исходные выражения defaults и исторические
script blobs. Это не runtime readback. Поле `semantic_review=pending` не означает
выполненную проверку поведения.

Рабочие инструменты переносятся в `Scripts/StructTrain/TimeLearner`. Устаревшие
запускатели удаляются после замены production-пути; wrappers на старых местах
не сохраняются. Для восстановления истории используются repository, commit и blob
из migration manifest.
