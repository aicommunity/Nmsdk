# Cold7 Console2: инженерная runtime-проверка

На M40 завершены2/2 сквозных production Console cases без failures/errors/skips: Classic и Branch. Это новый cold Train, полный export/import recognition model, измерительная калибровка с реальным подтверждением порога, fresh frozen Test, silent negative control и changed-threshold rollback с повторной проверкой восстановленной модели. Outer832.120134s, exit0, diagnostics clear; независимо проверены16 native units и4 released managed leases. [Полный исходный результат](ValidationPlans/M40Cold7Console2ControllerA4-20261110/actual-result.json), [все native closures](ValidationPlans/M40Cold7Console2ControllerA4-20261110/all-managed-units-closure.json).

| Условие | Значение |
|---|---|
| Python tool/test source |260eda04ac93c6a083deb0dff1514bcbd2a2bd1e|
| Compiled Console root |f2f8e611d51f1b4f23ef0471ddfc7618e68a59ea|
| PulseLib / Rdk |165d49da7e65cd6ac59bca2812ce52884ddd50c2 / de4134235c0dcb8b91fd9a43b267348ad1a163ca|
| Physical inputs / rate |N=2 /2000Hz|
| Normalization |N0, CapturedPerInput|
| Sync / amplitude abs / relative |0.2 /1e-5 /0|
| Original target ISIs |[0.01,0.08]s|
| Foil |last ISI×1.5, т.е.[0.01,0.12]s|
| Conversion / optional modes |identity; C-trim/PostTune/auto-calibration Off|
| Protocol |reset_per_trial, target/foil/foil/target, complete windows|
| Calibration |historical same-matrix, real measured grid и fresh confirmation|

| Topology |Calibration|TP|FP|FN|TN|
|---|---|---:|---:|---:|---:|
|Classic|calibrated|2|0|0|2|
|Branch|calibrated|2|0|0|2|

[Условия и counts из реальных файлов](ValidationPlans/M40Cold7Console2ControllerA4-20261110/actual-scope-and-counts.json). Два предъявления target и два предъявления одного foil не являются четырьмя независимыми паттернами/обучениями. Модели и выбранные пороги фиксировались перед каждой frozen matrix; independent_partition_verified=false, scientific_verdict=null. Стандартный SyncTolerance0.02 не изменён; N4, N1 normalization, nonidentity conversion, C-trim/PostTune, robustness и обязательная матрица плана этим контролем не закрываются.

Начальные сохранённые packages давали initial declarations и immutable profile images, а не learned-state seed. Train создал новые source packages; при переносе проверялся весь actual state и semantic model fingerprints. Boolean Build/Reset/Calculate не использовались как error propagation. Старые ownership/Qt/session-expectation отказы и controller OOM256MiB сохранены; successful A4 controller cap2GiB объявлен отдельно от native4GiB и managed capacity6GiB. Это прохождение после исправления постановки и бюджета, а не устранение научной трудности подбором допуска.

Перед отчётами зафиксированы1144 regular primary files,882648635bytes и16 redundant glog aliases. [Fingerprint inventory](ValidationPlans/M40Cold7ConsoleReports2-20261111/primary-inventory.json). Две полные visual/report проверки запущены отдельно: все паттерны/сомы/candidates/confirmation, фактические входы, overview+zoom без downsampling. Full report cache — M40 Data; compact primary и выбранные рисунки должны быть опубликованы в Git после проверки. Пока их публикация и фактическая visual QA открыты; metadata не заменяет primary.

Общий план и этапы1–12 не считаются завершёнными; full native119 на двух Linux workers также остаётся отдельным незавершённым gate. Августовские4/8–6/8 сохраняют исходную доказательность, новая серия D не запускалась.
