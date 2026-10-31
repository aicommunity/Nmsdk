# Native Train → export → frozen evaluation

Это проверяемый подэтап этапов 5, 8–10. Он добавляет настоящий холодный Train
в production Console и отдельные операции переноса и оценки. Полный план,
общий scheduler/ConditionSpec, PostTune и обязательная матрица остаются открытыми.
Калибровка описана отдельно в [NativeCalibrationWorker](NativeCalibrationWorker.ru.md).

## Запуск и владение моделью

Компоненты Console: `TimeLearnerTrainingJob`, `TimeLearnerTransportJob` и общий
`TimeLearnerJobSupport`. Они используют стандартный `UAppCore.Init` и создают
модель через storage/Environment до PostInit проекта. Одновременно разрешена
одна из операций train/export/evaluate/calibrate; project execution/inspection
с ними несовместимы. Уже существующая непустая модель не уничтожается.

Общий helper устанавливает частоту дерева до создания owner. Build/Reset
вызываются штатно; их bool не используются как диагностика. Init является void.
Model.Calculate вызывается один раз на native tick, после него Environment
продвигает модельное время на шаг. Контроллер не рассчитывает вложенную модель.

Холодный Train принимает `ConfiguredNativeTraining` и до включения обучения
проверяет действительную структуру, storage-профиль и начальные L/Ns/R.
`profile_archives` поставляют определения class images; обученный instance
из этого архива не импортируется. Начальная структура берётся из configuration.
Она может иметь L>1 и не обязана отличаться от корректного шаблона.

Нативный сервис добавляет первой попытке суффикс `/session/1`. Исходный ID
попытки остаётся в execution.json; экспортированная configuration содержит
полный session ID. Python-аудит допускает именно это преобразование ID,
сравнивая все остальные поля configuration без изменений.

## Ограничения первого контура

- Только явно объявленный ControllerVersion=2 и единая частота дерева.
- Classic/Branch и N0/N1, CalculateMode 0/1 и learner StructureBuildMode 0/1.
  Набор runtime-проверенных комбинаций ниже; это не вся декартова матрица.
- `optional_modes` обязателен: sync_capacitance_trim=0,
  post_train_tuning=false, auto_calibrate_threshold=false. Нативный default
  PostTune=true явно переопределяется перед Build; скрытого запуска нет.
- Train не обещает продолжения с середины пробы. Сохраняется завершённое
  обученное состояние либо отдельное диагностическое stopped state.
- Wrapper evaluate принимает проверенный `per_trial_windows`. Нативный вариант
  continuous stream ещё не принят как production-путь этого wrapper.
- Независимость Test от training/calibration data не устанавливается
  автоматически: independent_partition_verified остаётся false.

## CLI

Все операции запускаются только на назначенных Linux workers через jump host.
Источники, конфиги и результаты передаются через Git. Каталог output должен
отсутствовать; существующий результат не перезаписывается.

```text
python3 -m Scripts.StructTrain.TimeLearner train train-job.json \
  --runtime-manifest runtime.json --wall-seconds 600 --output train-run

python3 -m Scripts.StructTrain.TimeLearner export export-job.json \
  --source-solo train-run/native/train_learned_state.json \
  --runtime-manifest runtime.json --wall-seconds 600 --output export-run

python3 -m Scripts.StructTrain.TimeLearner evaluate evaluation-job.json \
  --source-solo train-run/native/train_learned_state.json \
  --runtime-manifest runtime.json --wall-seconds 600 --output evaluation-run

python3 -m Scripts.StructTrain.TimeLearner analyze evaluation-run/run-manifest.json \
  --format pipeline-run
```

Job имеет строгий набор полей и canonical SHA256 без собственного поля sha256.
Декларации сохраняются в input/job.json. Schema и точные поля заданы в
`native_pipeline_worker.py` и соответствующих native Read-функциях.
Для export source_solo должен быть фактическим completed package предыдущего
Train; source_recognition для evaluate — фактическим результатом export либо
подтверждённой калибровки. Шаблонный fallback отсутствует.

Export применяет conversion_spec к неизменяемому solo package, не выполняет
Calculate и возвращает полную recognition-модель. Stopped diagnostic state
не принимается вместо completed solo. Frozen evaluate проверяет полный export
модели до и после каждой пробы; неподтверждённый threshold candidate запрещён.

## Данные и статусы

Train сохраняет подписанный initial-state.json до начала обучения, все реальные
CSV отсчёты и JSON наблюдения, summary, полный model package и execution.json.
Обученные файлы именуются train_learned_state/summary и train_state_trial_N;
диагностические — train_stopped_state/summary и train_stopped_trial_N.
Потенциалы пишутся потоково, SHA CSV вычисляется без чтения всей трассы в память.

Evaluate сохраняет job, model, model-after, evaluation spec и полные observations
каждой пробы. При прерывании expected design остаётся полным; пропущенные пробы
не исчезают из матрицы. Неполная оценка не получает metrics/PASS.

Python использует production process_runner с pidfd, runtime before/after и
wall budget, сохраняет собственную копию source primary JSON/CSV, формирует
RunManifest. Portable audit перепроверяет замыкание файлов, подписи, исходную
модель, параметры холодного старта, дизайн, нативные часы, результат scorer,
аргументы запуска, owned executable и схему всех записанных executable mappings.
Это проверка согласованности данных; native_execution_verified=false.
Launch-time mapping snapshot не доказывает полный список поздно загруженных
plugins. Общий scheduler, leases и полная provenance-приёмка остаются открытыми.

`completed` процесса, completed_boundary Train, `exact/search_unresolved`,
validity наблюдений и качество распознавания остаются разными величинами.
SearchUnresolved сохраняется в export и не повышается до Exact после Test.
Фиксированный порог может дать валидный all-silent отрицательный результат.
Worker-limit/cancel не создают сертификат завершённого обучения.

## Scoped проверка

Native root `d5ef1fa18221f2ffb3e8efdeb32cccff059226e0`:
normal и ASan выполнили по 4 cold cases / 12 операций, Classic/Branch × N0/N1,
2000 Гц, два входа, target+foil. N0: CalculateMode=1/StructureBuildMode=0;
N1: 0/1. Все четыре исхода search_unresolved, все frozen observations valid.
ASan использован с detect_leaks=0: это не проверка утечек.

Normal owned CLI reader `cfb09d3c2fa7e5eaa52d0387b663bd6a55a1c610`
прошёл 12 операций и 12 portable audits. Первый reader 27fc5e3 завершился
отказом из-за неверного ожидания session ID; исправление не меняло native
бинарник. Контроль c8bb72b: 6/6, 12.967 s, без skips, включая rehashed cold
readback, удаление target из дизайна, повреждение mapping и подмену команды;
реальный one-tick Test сохраняет полный expected design и возвращает status 2.

Компактный [normal primary bundle](../../../Reports/StructTrain/TimeLearner/s09-native-pipeline-normal-a1/README.md)
содержит 211 файлов / 371128 bytes; отдельная механическая extraction-проверка
содержит 47 файлов / 694388 bytes. Публикация остальных CLI/ASan/controls и
новые графики этого контура отслеживаются в CurrentStatus. Это не replay августа,
не полные 8 паттернов и не приёмка всех этапов.
