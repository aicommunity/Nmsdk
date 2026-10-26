# Структурное обучение TimeLearner

Этот раздел содержит поддерживаемую спецификацию рефакторинга двух компонентов:
Classic (`NNeuronTimeLearner`) и Branch (`NNeuronTimeLearnerBranch`).

- [План и условия приёмки](RefactoringPlan.ru.md).
- [Исходная точка и ход реализации](ImplementationStatus.ru.md).
- [Сверка полноты всего плана](PlanCompletionAudit-2026-10-25.ru.md).
- [Решения и обязательные контракты](Decisions.ru.md).
- [История и доказательства](Evidence.ru.md).
- [Машинный inventory исходников](source_inventory.json).
- [Контракт наблюдений и оценки](ObservationContract.ru.md).
- [Readback фактического графа модели](ModelInspection.ru.md).
- [Lifecycle/storage: ход проверки и оставшиеся ограничения](Stage04-Progress.ru.md).
- [Перенос модели: выполненная часть и оставшиеся проверки](Stage05-Progress.ru.md).
- [Semantic model identity и проверка фактического графа](ModelIdentity.ru.md).
- [Native ModelArchive: формат, API и ограничения](ModelArchive.ru.md).
- [Единый владелец native graph API: проверенный перенос в PulseLib](ModelGraphOwnership.ru.md).
- [Явные stimulus-порты и native lifecycle внешних связей](ModelBoundary.ru.md).
- [Удаление образов: два ASan дефекта и проверка исправления](StorageCleanup.ru.md).
- [Classic live rebuild: Init нового нейрона и открытый вопрос частот](LiveRebuildInit.ru.md).
- [Общий и индивидуальный шаг: контракт создания поддеревьев](FrequencyContract.ru.md).
- [Общий контроллер: подготовка baseline и оставшиеся изменения](Stage06-Progress.ru.md).
- [Общий измеритель проб, native soma и storage-зависимости](ProbeMeasurement.ru.md).
- [Нативный исполнитель проб Classic/Branch: рабочий подэтап и gates](NativeExecution.ru.md).
- [Фактические события генератора, пустая история и Multi dimensions](../../../Libraries/Nmsdk-PulseLib/Docs/Analysis/TimeLearnerPulseEvents.ru.md).
- [Финальная верификация всех входов и привязка сертификата](FinalVerification.ru.md).
- [Явные физические storage-профили](../../../Libraries/Nmsdk-PulseLib/Docs/Analysis/TimeLearnerStorageProfiles.ru.md).

Inventory перечисляет declarations, исходные выражения defaults и исторические
script blobs. Это не runtime readback. Поле `semantic_review=pending` не означает
выполненную проверку поведения.

Рабочие инструменты переносятся в `Scripts/StructTrain/TimeLearner`. Устаревшие
запускатели удаляются после замены production-пути; wrappers на старых местах
не сохраняются. Для восстановления истории используются repository, commit и blob
из migration manifest.
