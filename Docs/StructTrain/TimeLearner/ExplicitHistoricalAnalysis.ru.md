# Явное чтение исторического Train analysis

Изменение подготовлено в отдельной ветке на integrated d936. Серверная приёмка ожидается; это не merge всей интеграции в develop.

По умолчанию audit_run_manifest требует точного равенства сохранённого анализа и результата текущего аудитора. Прежняя версия отчёта не считается результатом новой версии автоматически. Все model/runtime/process/artifact проверки выполняются до адаптации.

Разрешены только два явно названных перехода:

- learned-v2-no-capacitance: прежний completed Train manifest1 с training auditor2 без capacitance_state; текущий learned auditor3 или5, capacitance_state строго None, history отсутствует. Сохраняется прежний вызов model_spec_transport.prepare; остальные поля сравниваются точно.
- training-v3-no-capacitance-history: Train с training auditor3; текущий learned5 для completed или stopped4 для незавершённого обучения. Оба результата имеют capacitance_state, history отсутствует. Проецируется только auditor_version. Изменённое значение C не скрывается, оно должно точно совпасть с ранее записанным analysis.

Никакие manifests, package/model hashes, certificate, количество trials, исходные измерения, training status, runtime и verdict не переписываются. Неизвестные поля/версии и имеющаяся новая история C не проецируются. Native execution/import и научный verdict этим не подтверждаются. Старая learning state проверяется текущим production reader по всем исходным данным.

Публичный вызов:

```sh
python3 -m Scripts.StructTrain.TimeLearner analyze /absolute/path/to/train/run-manifest.json --format pipeline-run --historical-analysis training-v3-no-capacitance-history
```

Без флага сохраняется строгий отказ. Флаг применим только к analyze --format pipeline-run; managed pipeline continue/reconcile не получает автоматического historical adapter. Для приёмки актуального managed pipeline необходима свежая corpus на этой версии SDK, а не изменение старых analysis records.

Проверки:12 новых real-primary tests на прежних completed/stopped Classic/Branch Train receipts, включая оба ModelSpec wire versions, CLI, неправильный adapter/version, ложную сходимость, отсутствие/подмену capacitance, повреждение primary model и runtime. Дополнительно4 existing ModelSpecTransportPreparationTest используют исходные pinned Git primaries с auditor2. Тесты требуют реальных данных; skips не считаются приёмкой. Сборка/нейронные модели этим Python-набором не запускаются. Execution receipts должны быть сохранены до заявления исправления проверенным.
