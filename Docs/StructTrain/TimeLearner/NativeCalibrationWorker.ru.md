# Production запуск native-калибровки

Console исполняет объявленный threshold-grid на сохранённой recognition-модели.
Это подэтап этапов 8–10, не замена Train, PostTune, общей очереди экспериментов
или полной матрицы моделей. Runtime-приёмка перечислена в CurrentStatus.

## Компоненты и lifecycle

`App/NeuroModelerConsole/TimeLearnerCalibrationJob.{h,cpp}` использует стандартный
UAppCore.Init, storage и Environment. Режим вызывается до PostInit/автозапуска
пользовательского проекта. Он несовместим с --config, запуском вычислений,
инспекцией, сохранением проекта и генерацией ClDesc в одном вызове.
Непустая уже существующая модель не уничтожается: запуск отклоняется.
Код GTest и ConsoleLikeInit не используется.

`Scripts/StructTrain/TimeLearner/native_calibration_worker.py` выполняет preflight,
сохраняет собственную копию входов и первичных данных, запускает Console через
production process_runner с pidfd и wall timeout, проверяет модель и весь grid,
записывает переносимый RunManifest.

```text
strict parse + digest
check source primaries and declared calibration design
snapshot job and all solo primary JSON/CSV; validate snapshot again
verify immutable runtime; launch owned Console process
  native storage import; Build/Init/Reset for imported graph
  full effective export readback
  construct common transaction; validate capabilities/design
  reserve fresh output directory
  Advance between ordinary model ticks
  native model Calculate once; Environment clock step once
  commit confirmed model or retain explicit negative/diagnostic status
  export full model; bind job/model/transaction byte hashes
verify runtime again
audit complete matrices against primary source
write RunManifest with runtime, process, scorer code and artifact closure
```

Bool Build/Reset/Calculate не используются как каналы ошибок; Init имеет штатный
void-интерфейс и guard IsInit, поэтому инициализация parent не повторяет AInit
у уже инициализированного learner. Worker не
вызывает Calculate learner или детей отдельно от model scheduler. Driver
выполняет собственные native imports/сбросы физики по существующему контракту.
Исправляющих записей параметров на каждом тике нет. Mid-probe checkpoint не обещан.

## Job schema 1

Kind — timelearner_native_calibration_job, schema_version — 1. Точные поля:

| Поле | Содержание |
|---|---|
| owner_class | NNeuronTimeLearner или NNeuronTimeLearnerBranch, согласованный с source |
| implementation_id | Версия реализации из source package |
| frequency_hz | Целая единая частота дерева, совпадающая с source |
| maximum_model_ticks | Целый бюджет model loop: 1…10⁹ |
| source_recognition | Полный recognition package с solo source и storage definitions |
| thresholds | Объявленный порядок конечных уникальных порогов, не более 256 |
| maximum_candidates | Бюджет prefix сетки: 1…256 |
| specification | protocol, data_partition_id, attempt_id, clock_id, criterion |
| trials | Полный упорядоченный массив NativeCalibrationRequest |
| sha256 | CanonicalModelDataSha256 всего объекта без поля sha256 |

Specification и requests используют те же strict codecs PulseLib, что persisted
proof. Неизвестные поля, дубли ключей (включая escaped), неправильные типы и
повреждённые числа отклоняются. Request содержит run_id, trial_id, sample_id,
label, pattern_hash, pattern_isi, duration, maximum_samples, reset_policy,
record_threshold_potential. Входной run_id — метка declaration; driver назначает
реальные search/confirmation IDs. Criterion содержит anchor=onset/last_stimulus,
begin_offset, nullable end_offset, reject_target_outside_window. Для каждой reset
policy нужны target и foil. Название frozen_independent_calibration не доказывает
независимость данных: нужна отдельная проверка происхождения выборок.

## CLI, остановка и артефакты

```text
python3 -m Scripts.StructTrain.TimeLearner calibrate run JOB.json \
  --source-solo SOURCE_learned_state.json \
  --runtime-manifest runtime.json --wall-seconds 600 --output NEW_ATTEMPT

python3 -m Scripts.StructTrain.TimeLearner analyze \
  NEW_ATTEMPT/run-manifest.json --format calibration-run

python3 -m Scripts.StructTrain.TimeLearner report \
  NEW_ATTEMPT/run-manifest.json --format calibration-run --output NEW_M40_REPORT_CACHE
```

Прямой native интерфейс: `NeuroModelerConsole --app-ini INI
--timelearner-calibrate JOB.json --timelearner-output NEW_NATIVE_DIRECTORY`.
Package CLI дополнительно проверяет первичные данные и связывает runtime/process.

Cancel.request (имя файла — `cancel.request`) в native output проверяется между
тиками и вызывает отмену transaction. Maximum_model_ticks даёт отдельную причину
model_tick_budget_exhausted. Wall timeout/принудительную остановку учитывает
process_runner; отсутствие полного native результата не становится калибровкой.
Повторное использование output запрещено.

Native directory содержит job.json, transaction.json, model.json, execution.json.
Execution связывает точные байты первых трёх файлов; model.json — полный effective
export. Для Calibrated он равен committed package, для корректного отрицательного
исхода — восстановленному source. RunManifest дополнительно связывает все
snapshot/primary/process/native artifacts, исходную Git closure runtime и hashes
production Python-модулей анализа. Portable reader проверяет файлы, первичные
JSON/CSV, объявленный grid, fresh confirmation и соответствие модели.

Reader проверяет согласованность записанной provenance, а не подлинность любого
чужого процесса: native_execution_verified=false сохраняется. Model proof schema 1
по-прежнему не содержит весь grid; полный выбор проверяется через RunManifest и
transaction, не при загрузке отдельного model.json.

Статус Train сохраняется без повышения. Calibrated не означает Exact обучения,
independent Test или научный PASS. Digest calibration specification не подменяет
полный ConditionSpec кампании. Train/export/evaluate, общая очередь/publisher,
полный PostTune и физическая матрица остаются открытыми требованиями плана.

Report проверяет полный RunManifest и первичные данные до создания output,
после чего строит все завершённые candidate/confirmation matrices общим
renderer: каждая проба и каждая сома, фактические входы, overview и 100-tick zoom
без прореживания. Run-binding.json отдельно фиксирует проверку первичных данных;
обычный transaction renderer сам по себе её не обещает. Полные PNG/SVG/PDF —
в M40 cache; Git хранит primary archive, метаданные и выбранные изображения.

Runtime mappings process_runner снимаются при старте процесса. Они не являются
полным census всех потенциально загруженных позднее plugin libraries. Этот
предел provenance сохраняется до отдельного расширения production runner.
