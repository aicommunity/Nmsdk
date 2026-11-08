# Диагностика достижимости последнего final callback

Исходная отрицательная попытка M40: `eaa4350defa80c932ececaafa58b5373112fc75d`, источник Root `cc23d9fff8baba3c5dca89f5e2a0131d7ad1c237` / PulseLib `88ea9c7ab3583da601b1f01ec84bf6f122875a34`. Выполнено 13 из 248 тестов: 12 PASS и один FAIL; остальные 235 не выполнялись. Исходные Classic/Branch PreparedStop прошли. У BranchLastCompositeSinkCannotCrossRealGroupDeadline callback со sleep не достигнут: slept=false, elapsed=0. Полное время теста 35.594 с не определяет, какая группа исчерпала 15-секундный бюджет. Это не подтверждение проверки deadline после callback.

Добавлены два отдельных fixture-only теста:

- `NativeCompositeDeadlineDiagnostic/ClassicUnchangedLastFinalReachability`;
- `NativeCompositeDeadlineDiagnostic/BranchUnchangedLastFinalReachability`.

Они сохраняют исходную физику (2000 Гц, 64 синапса), ServicePlan, математические допуски и штатный инженерный лимит группы 300 с. Sleep отсутствует, системное монотонное время не заменяется. Никаких изменений production-кода, прежних 248 тестов или ожидаемого результата не внесено.

При production-передаче TIMELEARNER_COMPOSITE_OUTPUT каждый тест создаёт новый `deadline-reachability/classic.json` либо `branch.json`. Записываются actual группы с purpose, input/run/group ID, consumed/state/reason, временем начала/окончания, реальными счётчиками и объявленным wall-лимитом; отдельно события before/after consume с фактическим временем и признаком последнего final. Итог содержит outcome/reason и факт входа в последний callback. Даже при провале EXPECT первичные данные записываются до утверждений.

Диагностическая приёмка требует фактического last-final entry и Exact штатного сценария. Она не проверяет пересечение deadline и не заменяет прежние slow-sink тесты. По её данным отдельно выбирается инженерный бюджет; затем необходимы Classic/Branch targeted slow-sink controls с настоящим sleep, пересекающим объявленный deadline. До этого полный 248 gate остаётся непройденным. Файл CompositeCancellationDeliveryGateInventory.json относится к замороженному cc23; его прежние SHA и критерии здесь не переписываются.
