# Структурное обучение TimeLearner

Этот раздел содержит поддерживаемую спецификацию рефакторинга двух компонентов:
Classic (`NNeuronTimeLearner`) и Branch (`NNeuronTimeLearnerBranch`).

Работа возобновлена пользователем 28.10.2026. [Историческая точка остановки и сохранённые проверки](ResumeAfterPause-2026-10-27.ru.md).

- [План и условия приёмки](RefactoringPlan.ru.md).
- [Приёмка 28.10: full post-fix gate, native completed state и child merges](PooledFullAcceptance.ru.md).
- [Исходная точка и ход реализации](ImplementationStatus.ru.md).
- [Актуальный статус всех этапов на 29.10: принятый develop, scoped проверки и оставшаяся работа](CurrentStatus-2026-10-29.ru.md).
- [Историческая сводка 27.10 и последующие дополнения](CurrentStatus-2026-10-27.ru.md).
- [Предшествующий аудит 27.10 и история дополнений](PlanCompletionAudit-2026-10-27.ru.md).
- [Исходная сверка 25.10 и журнал последующих дополнений](PlanCompletionAudit-2026-10-25.ru.md).
- [Решения и обязательные контракты](Decisions.ru.md).
- [История и доказательства](Evidence.ru.md).
- [Первоначальный Git inventory (исторический снимок)](source_inventory.json).
- [Контракт наблюдений и оценки](ObservationContract.ru.md).
- [Readback фактического графа модели](ModelInspection.ru.md).
- [Lifecycle/storage: ход проверки и оставшиеся ограничения](Stage04-Progress.ru.md).
- [Native component order: подтверждённый выход за границу и исправление Rdk](ComponentOrderBounds.ru.md).
- [Pooled property bindings: full-suite отказы, исправление Rdk и проверки](PooledPropertyBindings.ru.md).
- [EnableTrainingAudit: воспроизведённый Default defect и отличие от stock reuse](AuditFlagDefault.ru.md).
- [Перенос модели: выполненная часть и оставшиеся проверки](Stage05-Progress.ru.md).
- [Остановленное обучение: диагностический перенос без сертификата, текущая проверка](StoppedTrainingState.ru.md).
- [Эффективные N1 области: дефект mesh и текущая реализация preview](DynamicResistanceDomains.ru.md).
- [Независимая проверка физических оснований N1 decisions, рабочий подэтап](DomainDecisionEvidence.ru.md).
- [False sampling gaps при большом absolute clock: full failures и исправление](AbsoluteClockSampling.ru.md).
- [Semantic model identity и проверка фактического графа](ModelIdentity.ru.md).
- [Типизированный наблюдатель фактической ревизии и native A/B скорости](ModelRevisionObserver.ru.md).
- [Native ModelArchive: формат, API и ограничения](ModelArchive.ru.md).
- [Единый владелец native graph API: проверенный перенос в PulseLib](ModelGraphOwnership.ru.md).
- [Явные stimulus-порты и native lifecycle внешних связей](ModelBoundary.ru.md).
- [Удаление образов: два ASan дефекта и проверка исправления](StorageCleanup.ru.md).
- [Classic live rebuild: Init нового нейрона и открытый вопрос частот](LiveRebuildInit.ru.md).
- [Общий и индивидуальный шаг: контракт создания поддеревьев](FrequencyContract.ru.md).
- [Общий контроллер: подготовка baseline и оставшиеся изменения](Stage06-Progress.ru.md).
- [Native builder/adoption: проверенный C++ API, lifecycle и границы приёмки](NativeModelBuilder.ru.md).
- [Configured ControllerVersion=2: cold JSON/XML, checks и ограничения](ConfiguredNativeController.ru.md).
- [Семантика трёх новых configured properties в обоих learner](ConfiguredPropertyContracts.ru.md).
- [Семантика исходных управляющих свойств и class selectors: 16 записей](LegacyControlPropertyContracts.ru.md).
- [Семантика цели, структуры и времени: ещё 29 исходных записей](TimingAndTargetPropertyContracts.ru.md).
- [Семантика диагностик: 38 исходных записей](DiagnosticPropertyContracts.ru.md).
- [Нормализация и повторные измерения: 34 исходные записи](NormalizationPropertyContracts.ru.md).
- [Порог, PostTune и калибровка: 44 исходные записи](CalibrationPropertyContracts.ru.md).
- [C-trim, physical overrides и торможение: 35 исходных записей](PhysicsPropertyContracts.ru.md).
- [Cold reset, experiment dispatch и logging: 15 исходных записей](ResetAndLoggingPropertyContracts.ru.md).
- [Текущий прогресс semantic property review](PropertyReview.json).
- [Полнота code catalog: 211 исходных и 6 новых свойств](PropertyReview.coverage.json).
- [Общий измеритель проб, native soma и storage-зависимости](ProbeMeasurement.ru.md).
- [Нативный исполнитель проб Classic/Branch: рабочий подэтап и gates](NativeExecution.ru.md).
- [Полная последовательность волн и physical input ownership: schema 3](BurstAssignment.ru.md).
- [Явный выбор назначенной волны в широком окне](AssignedWaveSelection.ru.md).
- [Общий ограниченный поиск, фактические банки и границы приёмки](BoundedTraining.ru.md).
- [Native изменения L/Ns/Rs, preview и сохранность чужих связей](NativeModelEdits.ru.md).
- [Общая native-служба capture/search/final verification и аудит первичных данных](NativeTrainingService.ru.md).
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

- [Native Solo→Recognition: storage/import, conversion и границы проверки](NativeRecognitionState.ru.md).

- [PostTune: native graph reconstruction, actual parallel transport и открытая candidate transaction](PostTuneNativeRebuild.ru.md).

- [PostTune: неизменяемая цель и actual transient stimulus](PostTuneTransientStimulus.ru.md).

- [PostTune: рабочая реализация отката графа и оставшаяся транзакция](PostTuneBoundaryTransaction.ru.md).

- [Миграция скриптов: удаления и точные Git-источники](ScriptMigration.ru.md).

- [Август: точные Git-источники моделей, CSV и отдельные commits отчётов](HistoricalEvidenceAnchors.ru.md).

- [ConditionSpec и раздельные identities: рабочий codec, приёмка ещё открыта](ConditionIdentities.ru.md).

- [Точка продолжения 29.10: точные sources, завершённые A2 и ожидающие проверки](ResumeCheckpoint-2026-10-29.ru.md).

- [Lossless Rdk configs, numeric tags, native readback и UTF-8 BOM finding](ConfigDocument.ru.md).

- [M40: перенос завершённых runtime и подтверждённая очистка дублей](M40Storage-2026-10-29.ru.md).
