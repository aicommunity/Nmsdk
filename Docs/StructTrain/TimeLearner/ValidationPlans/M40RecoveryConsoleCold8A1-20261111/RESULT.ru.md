# Настоящий Console cold8:2/2

На M40 два server-only cases Classic/Branch прошли без failures/errors/skips. Actor/Python source3a64bbf09fb906844d9943ee3c4b0589300bcfda, native SDK8362d58f4d6576a0c8b0cc7633270976dff1df7b/Pulse1110808, runtime fingerprint61f3e2f0937f8f0bc70e0d40d907c0ba30d86f2030c7b79b2671343cadb374a0.

Обе модели прошли настоящий public preflight, холодный Train (Exact), export/import, полный frozen Test, measured-grid threshold calibration с реальным подтверждением, silent-candidate rejection и повторный native Test восстановленного графа. Source profiles регистрируются PrepareModelArchive; learned graph не используется как seed Train.

| Модель | Train | Калибровка | TP | FP | FN | TN |
|---|---|---|---|---|---|---|
| Classic N2/N0 | exact | calibrated |2|0|0|2|
| Branch N2/N0 | exact | calibrated |2|0|0|2|

Это **один target и один foil, каждый предъявлен дважды**, с reset-per-trial. Калибровка historical same-matrix; независимая data partition не проверена. Explicit SyncTolerance0.2, остальные declared tolerances сохраняются. N2 результат не подтверждает N4/default0.02, перестановки/другой ITI или научную общую разделимость. Обе Train execution5 завершились с recovery_delivery_count0: настроенная policy присутствовала, но её фактическое вмешательство этим Train не проверено.

Silent candidate дал nonseparable и полный откат; новый процесс воспроизвёл исходные samples/spike_count после восстановления. Model/threshold frozen в соответствующем evaluation. Source и fixture before/after побайтно совпадают, controller cgroup закрыт, original lease released, diagnostics clear. [Result](completed/worker/validation/result.json), [integrity](readback-integrity.json), подробные per-model results находятся в completed/worker/native-console-cold8. Полный compact primary corpus, независимый повторный анализ и графики ещё требуются.
