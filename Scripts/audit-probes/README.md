# Оставшиеся изолированные component probes

Исторические TimeLearner generators, review scripts и fixed-threshold launcher удалены из текущего дерева. Исходники и результаты прежних аудитов сохраняются в Git и отчётных документах: [manifest и причины](../../Docs/StructTrain/TimeLearner/AuditProbeRetirement.ru.md). Не восстанавливайте executable wrappers на старых местах.

В этом standalone CMake остаются audit_existing_gui и audit_counterexamples. Первый использует реальные тесты GUI link-router/scope-path из Rdk; второй линкует NNeuronPostTrainTune/GUI и старые извлечённые NPatternResponseAnalyzer/NAxoneDelay/NAperiodicLink тела через generate_probes.py. Это смешанные изолированные component probes с адаптерами; они не подтверждают lifecycle/storage, Train→Test или актуальную сходимость TimeLearner. Этот пакет ещё требует отдельного review по непрямым зависимостям.

Нынешнее изменение удаляет только два target audit_training_core и audit_branch_update и их configure dependencies/execute_process. Сохранившийся префикс CMake байтово соответствует прежнему. Нового результата GUI/counterexamples под этим commit не заявляется. Исторические counts13 GUI,9 CE без A12 и8 Branch относятся к прежним конкретным аудитам, а не к текущему общему PASS.

Актуальные TimeLearner tools находятся в Scripts/StructTrain/TimeLearner, реальные fixtures — в Tests/Integration/Libraries. [Текущая карта приёмки и незавершённых требований](../../Docs/StructTrain/TimeLearner/PlanCompletionAudit-2026-11-04.ru.md). Старые extracted-body probes не заменяют эти fixtures и не объявляются эквивалентными им.
