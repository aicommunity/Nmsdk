# Поддерживаемый пакет TimeLearner

Запуск из корневого репозитория: `python -m Scripts.StructTrain.TimeLearner`.
Import не запускает эксперименты. Реализованы `inventory`, native-подмножество
`analyze`, `report`, `bundle`, `publish`, `history resolve` и анализ измерений
`calibrate run/select/confirm`. Runtime/process supervisor также имеют module CLI.
Сквозные prepare/train/export/evaluate, scheduler и полная миграция ещё не готовы.

```text
python -m Scripts.StructTrain.TimeLearner analyze record.json --format domain
python -m Scripts.StructTrain.TimeLearner analyze trial.json --format probe --trace trial.csv
python -m Scripts.StructTrain.TimeLearner analyze case_learned_state.json --format learned-solo
python -m Scripts.StructTrain.TimeLearner analyze case_stopped_state.json --format stopped-solo
python -m Scripts.StructTrain.TimeLearner analyze case_recognition_state.json --format recognition
```

`--output new.json` создаёт новый файл и отказывает при существующем пути.
Без этого параметра результат выводится в stdout. Ошибки дают structured
diagnostic в stderr и exit code 2. Code 0 означает завершённый анализ записи,
но не Exact, пригодность domain либо успешное распознавание: эти признаки
содержатся отдельно внутри `analysis`; `evaluation_verdict` остаётся null.
Ошибки содержимого имеют validity=invalid. Ошибка файловой операции, включая
существующий output, имеет execution=process_error / validity=unknown:
сбой записи не доказывает повреждение исходных данных.

Для исторической domain schema 1 требуется `--allow-legacy`; результат всегда
с `physics_verified=false`. Нельзя подставлять этот адаптер в другой формат.
Original primary CSV обязателен для отдельной probe; learned/stopped loaders
требуют связанные исходные пакеты по их versioned naming contract.
Recognition analysis требует исходный solo package с первичными пробами,
conversion record и declared frozen transport spec/observation/CSV schema 1.
Проверяет математику преобразования и неизменность остальных model properties;
unknown/incomplete transport не принимается. Spikes остаются unknown, а не 0;
это проверка переноса/состояния, не recognition selectivity verdict.

Для полных frozen trials общий строгий scorer доступен как
`analyze EVALUATION_SPEC --format recognition-evaluation --model RECOGNITION_PACKAGE`.
Исторический spiking CSV и полный production runner ещё не мигрированы.
Старые запускатели будут удалены после замены
их действующих функций и записи commit/blob в migration manifest.

`analyze <case_reconstruction.json> --format posttune-reconstruction` проверяет
фактический graph/heterogeneous C и полные parallel traces до/после native
реконструкции/rollback. Проверяются объявленная one-pass Dataset policy и
stimulus timestamps. Это evidence audit; native execution и научный PASS
команда не утверждает. Требуется полный комплект spec/observation/CSV файлов.

`analyze <case_transient.json> --format posttune-transient` проверяет закрытую
схему полного transient presentation, actual onsets/relative arrival windows,
сохранность training goal и raw presented ISI в каждом frame. Неполные окна,
NaN, неизвестные схемы и скрытая временная подмена запрещают valid result.
Native execution, training certificate и scientific PASS команда не утверждает.

`condition.py` — рабочий общий codec content references/ConditionSpec, matrix,
analysis и attempt identities. Это ещё не preflight/runner и не замена Bin queue.
`runtime.py` создаёт manifest schema 2: deploy/resource/compiler paths исключены
из content identity, полная provenance сохраняется. Историческая schema 1
не пересчитывается. Source 670f2ff79 прошёл 18 Python tests на каждом worker
и реальный relocation/startup A2 binary с суффиксом `.rs2`: production snapshot
сохранил fingerprint. Теперь runtime/process supervisor подключены к native
`calibrate run`; общая очередь всей кампании остаётся незавершённой.
Runtime capture включает RelWithDebInfo/Minsize и linker flags. Артефакты и ограничения:
[ConditionIdentities.ru.md](../../../Docs/StructTrain/TimeLearner/ConditionIdentities.ru.md).

`config_document.py` добавляет lossless edits существующих text leaves с полным
путём и обязательным expected-old. Numeric names `<00>` сохраняются. По семь
tests на workers и реальный native readback на M40 ASan прошли; BOM/declaration
дефект исправлен в Rdk. Это ещё не effective component preflight:
[ConfigDocument.ru.md](../../../Docs/StructTrain/TimeLearner/ConfigDocument.ru.md).

### Frozen owner observation audit

`python -m Scripts.StructTrain.TimeLearner analyze CASE_owner_recognition_state.json --format recognition-owner`
проверяет conversion/source proof, actual before/after owner/reference hashes,
полное paired waveform и negative controls. Требуются source trial JSON/CSV
и schema-2 owner observation; schema-1 prototype без hash readbacks не получает
достроенных значений. Это validation evidence, без scientific verdict и spikes.

`analyze trial.json --format recognition-trial --model recognition_state.json`
проверяет полную frozen-пробу по primary кадрам, включая реальные stimulus/LT
истории событий, counts/timestamps, onset, покрытие окна и model hashes.
Молчание может быть валидным отрицательным наблюдением. Отмена и пропуск кадров
остаются `valid_observation=false`; успешное чтение согласованного файла не
означает успешного распознавания. `evaluation_verdict` остаётся null.
Проверка одной пробы не доказывает полноту матрицы; для неё требуется ожидаемое
множество run/trial IDs и sample/label/pattern hash из job spec. Размещение
target первым в файле не требуется. Подробности и область серверной проверки —
Docs/StructTrain/TimeLearner/FrozenRecognitionTrials.ru.md в корне.

### Метрики и крупные графические отчёты

`analyze evaluation.json.gz --format recognition-evaluation --model model.json.gz`
оценивает объявленное полное множество trials по labels/IDs/hash паттерна.
Критерий окна ответа задаётся явно; early target и любой foil spike во всём
окне не скрываются. Reset policies выводятся отдельно. Глобальный scientific
verdict требует общего runner/provenance и здесь остаётся null.

`python3 -m Scripts.StructTrain.TimeLearner report evaluation.json.gz --model model.json.gz --output NEW_DIRECTORY`
создаёт переносимый diagnostic index.html, primary данные, analysis.json,
manifest и контрольные суммы. На каждую trial/soma пару — отдельные PNG
1920×960, SVG/PDF overview и zoom-панели максимум по 100 native ticks.
Рендерить на workers; требуется matplotlib. Существующий каталог не заменяется.
Открывать полный PNG или vector-ссылку для анализа деталей. Schema-1 units
помечены model units / SI unverified; финальная визуальная матрица не закрыта.
Подробности: Docs/StructTrain/TimeLearner/VisualReportRenderer.ru.md.

Обучающие native probes имеют отдельный адаптер без выдуманных target/foil labels:

```text
python3 -m Scripts.StructTrain.TimeLearner report probe.json --format probe --trace probe.csv --output NEW_REPORT
python3 -m Scripts.StructTrain.TimeLearner report report-spec.json --format probe-set --output NEW_REPORT_SET
```

`probe-set` проверяет явные trial IDs, сохраняет portable spec и использует общие
Y limits каждого soma по всем пробам. Доступны overview, 100-tick zoom и явно
подписанный detail для слабого ответа; actual input waveform берётся из CSV.
При отсутствии регистрации spikes count остаётся unknown. Полнота отдельного
subset spec не доказывает полноту кампании. Схема, данные, серверные проверки
и открытые ограничения: Docs/StructTrain/TimeLearner/NativeProbeVisualReports.ru.md.

Для явно неполной пробы используется `--format probe-diagnostic`. Набор с
schema 2 и `observation_policy=complete_or_partial` включает censored и
невалидные наблюдения с серыми неизвестными интервалами и явным качеством данных.
Пустое наблюдение не получает придуманную кривую; NaN ординаты остаются разрывами.
Полнота CSV не превращается в валидность измерения. Подробности и серверные
проверки: Docs/StructTrain/TimeLearner/PartialProbeVisualReports.ru.md.

Для полного текущего native test run используется объявленный контракт cases,
фаз и отдельных исполнений:

```text
python3 -m Scripts.StructTrain.TimeLearner report Scripts/StructTrain/TimeLearner/specs/repeat-boundary-native-v1.json --format native-test-run --artifacts IMMUTABLE_READBACK --output NEW_REPORT
```

`IMMUTABLE_READBACK` содержит `native.xml` и `native/`; выход находится вне
этого каталога. Проверяются все ожидаемые фазы, recorder counters и packets/CSV,
включая partial, warm и embedded fresh-process probes. Пропавшая фаза либо
orphan CSV не могут молча уменьшить ожидаемое покрытие. Это адаптер конкретного
native fixture suite, не замена общего experiment runner. Контракт и ограничения:
Docs/StructTrain/TimeLearner/NativeTestRunVisualReports.ru.md.

### Компактные первичные данные в Git

По выбранной пользователем политике полный PNG/SVG/PDF набор остаётся
воспроизводимым кэшем M40. В Git сохраняются lossless primary archive, модели,
конфиги, метрики/manifests и выбранные source-bound PNG:

```text
python3 -m Scripts.StructTrain.TimeLearner bundle pack-native-tests CONTRACT.json --artifacts IMMUTABLE_READBACK --selected-report COMPLETE_CACHED_REPORT --output NEW_BUNDLE
python3 -m Scripts.StructTrain.TimeLearner bundle verify BUNDLE
python3 -m Scripts.StructTrain.TimeLearner bundle extract BUNDLE --output NEW_EXTRACTED
```

`--maximum-bytes` задаёт явный budget uncompressed bytes для pack/verify/extract
(default 8 GiB). Превышение budget, повреждение payload/metadata, paths/links,
неучтённый файл или несовпадающий выбранный рисунок запрещают успешную проверку.
Из распакованных данных строится полный report версией renderer из manifest;
научный verdict не следует из наличия архива. Контракт и scope:
Docs/StructTrain/TimeLearner/CompactArtifactBundles.ru.md.

### Git closure publication

`python3 -m Scripts.StructTrain.TimeLearner publish publication.json --root CHECKOUT --output NEW_RECEIPT.json`
публикует подготовленные commits всех сабмодулей, затем корня, без force и
переписывания истории. Проверяет committed gitlinks/.gitmodules, чистые exact
checkouts, локальные branch tips и фактические remote tips. Любая ошибка
останавливает дальнейшую публикацию; receipt отделён от научного verdict.
Spec/receipt хранить вне публикуемого checkout. Полный контракт и ограничения:
Docs/StructTrain/TimeLearner/GitClosurePublisher.ru.md. Это ещё не сквозной
experiment runner, очереди или доказательство полноты артефактов эксперимента.

### Процесс задания

`python3 -m Scripts.StructTrain.TimeLearner.process_runner --runtime-manifest runtime.json --working-directory RUNTIME --output NEW_ATTEMPT --wall-seconds 60 -- ARGUMENTS`
запускает объявленный executable, проверяет runtime, сохраняет PID/start/boot
identity, mappings, логи и результат. Timeout/cancel сигнализирует принадлежащему
заданию процессу через pidfd. Cancel — файл NEW_ATTEMPT/cancel.request.
`inspect_attempt` возвращает unknown при исчезновении процесса без результата;
не перезапускать job автоматически из-за обрыва наблюдения. Пока ownership
охватывает только launched executable, не fork/daemon tree. Контракт и
оставшиеся ограничения: Docs/StructTrain/TimeLearner/OwnedProcessSupervisor.ru.md.

### Измеренный порог

```text
python3 -m Scripts.StructTrain.TimeLearner calibrate select SPEC.json --measurements SEARCH.json --source-solo CASE_learned_state.json --output NEW_SELECTION.json
python3 -m Scripts.StructTrain.TimeLearner calibrate confirm SPEC.json --measurements SEARCH.json --source-solo CASE_learned_state.json --selection NEW_SELECTION.json --confirmation FRESH.json --output NEW_CONFIRMATION.json
python3 -m Scripts.StructTrain.TimeLearner report EVALUATION.json --format threshold-candidate-evaluation --model CANDIDATE.json --output NEW_CACHE
```

Это анализ реальных native measurements и диагностические рисунки. Команды
не исполняют Train, не устанавливают calibrated state в learner и не подтверждают
native import. Положительное подтверждение требует полной свежей матрицы с
отдельным run ID; silence, пропуски и search reuse не превращаются в успех.
Выбранный порог сам по себе ещё не является результатом калибровки.

SEARCH/FRESH — descriptor `timelearner_threshold_measurement_set`, schema 1:
`measurements` содержит `candidate`, `evaluation` (относительные пути внутри
каталога descriptor) и `execution` (attempt_id, clock_id, stage, selection_sha256).
Подтверждающий descriptor содержит ровно один measurement. Первичные observations
допускают JSON.gz; источники learned-state проверяются по настоящим sibling CSV.
Ошибки дают code 2 без положительного результата; NonSeparable или BudgetExhausted
являются допустимыми результатами анализа, различимыми в JSON при code 0.
Существующие выходные файлы не заменяются.

Обычный recognition-evaluation scorer намеренно отвергает threshold candidates:
для них существует отдельный calibration scorer. Candidate report явно помечен
диагностическим, не сертифицирует обучение или scientific Test. Подробный контракт:
Docs/StructTrain/TimeLearner/NativeThresholdCalibration.ru.md.

`analyze ASSESSMENT.json --format native-calibration-assessment --evaluation EVALUATION.json --model CANDIDATE.json --source-solo CASE_learned_state.json`
сопоставляет native response assessment с первичными observations и общим scorer.
Проверяются полный набор, label/ID, reset policies, все spikes и response windows;
true/false вместо числовых полей отклоняются. Raw observation auditor v2 требует
ровно один отсчёт на native tick и различимый dt. Статус исполнения simulator
и commit калиброванной модели этой командой не подтверждаются.

`analyze CALIBRATED.json --format calibrated-state --source-solo CASE_learned_state.json`
проверяет proof сохранённого `timelearner_calibrated_recognition_state`:
две успешные полные матрицы выбранного candidate, fresh run, raw observations,
source CSV и точное сохранение физического графа. Это анализ сохранённых данных;
команда не исполняет native import, не проверяет всю сетку и не запускает Test.

`recognition-evaluation` и обычный `report` принимают такой calibrated package,
повторно проверяют proof и оценивают новые полные observations тем же scorer.
Calibration run нельзя выдать за новый frozen evaluation run. Результат отдельно
содержит calibration evidence consistency и свежие response metrics; statistical
independence и partition separation автоматически не подтверждаются.
Сам отчёт остаётся диагностическим и не создаёт новую калибровку.
Native selection/commit/rollback доступен через `calibrate run` ниже. Его
адресная приёмка не заменяет полный PostTune и научную матрицу режимов.

Renderer entry points заранее проверяют headless matplotlib/Agg и Pillow до
создания report directory. Недостающий backend даёт структурированный отказ,
не оставляя partial report из-за этой ошибки. Manifest сохраняет фактический
Python executable и версии matplotlib/Pillow. На M40 используется существующий
`/media/user/Data/TimeLearnerRefactor/plot-venv-a1/bin/python`; system Python
этого сервера не содержит matplotlib. Interpreter нового worker должен быть
явно выбран и проверен; старый системный путь не является его настройкой.

### Native calibration transaction evidence

`analyze TRANSACTION.json --format calibration-transaction --source-solo CASE_learned_state.json`
проверяет полный записанный grid через общий scorer, sole-edit derivation и
source primary CSV. Свежая confirmation привязана к выбранному кандидату,
источнику, всему завершённому поиску и заранее объявленному design.
Частичный grid не даёт calibrated verdict; NonSeparable отличается от
BudgetExhausted. Cancelled/Failed/RecoveryRequired — diagnostic-only; проверка
не подтверждает физический rollback или подлинность native исполнения.

Это анализ фактических результатов `NativeThresholdCalibrationTransaction`.
Для запуска служит отдельный `calibrate run`; полный Train→Test pipeline и
интеграция общей очереди остаются открытыми.

`report TRANSACTION.json --format calibration-transaction --output CACHE_DIR`
строит все завершённые candidate matrices и fresh confirmation: каждый
паттерн и все soma channels, фактические входные импульсы, native-resolution
overview/zoom/series в PNG/SVG/PDF. Пороговые данные остаются calibration
diagnostics. Незавершённые пробы сохраняются как первичные данные, но не
выдаются за полную реакцию. Backend и raw evidence проверяются до создания
каталога. Полный отчёт предназначен для M40 cache; в Git сохраняются compact
primary и выбранные рисунки согласно общей политике.

### Production native calibration

```text
python3 -m Scripts.StructTrain.TimeLearner calibrate run JOB.json \
  --source-solo SOURCE_learned_state.json --runtime-manifest runtime.json \
  --wall-seconds 600 --output NEW_ATTEMPT
python3 -m Scripts.StructTrain.TimeLearner analyze \
  NEW_ATTEMPT/run-manifest.json --format calibration-run
python3 -m Scripts.StructTrain.TimeLearner report \
  NEW_ATTEMPT/run-manifest.json --format calibration-run --output NEW_M40_CACHE
```

JOB schema 1 содержит полный source recognition package, явные thresholds,
maximum_candidates, ordered NativeCalibrationRequests, response criterion,
одну частоту дерева, maximum_model_ticks и canonical SHA. Preflight проверяет
исходные primary CSV/JSON; worker сохраняет их snapshot, исполняет стандартную
Console через pidfd supervisor и связывает итоговую модель с полным grid,
fresh confirmation, runtime/process и hashes кода анализа. Повторное использование
output запрещено. Подменённые declarations/model/provenance отклоняются даже
после пересчёта внешних hashes.

Model-tick budget и wall timeout различаются. Первый даёт диагностическую отмену
с восстановлением source; незавершённый процесс не получает calibrated claim.
Portable audit проверяет согласованность, не подлинность чужих execution records.
Калибровка не повышает source Train до Exact и не подтверждает independent Test.
Source этих контрольных моделей имеет search_unresolved. Runtime mappings —
стартовый снимок процесса, без обещания полного позднего plugin census.
Контракт, ограничения и адресная приёмка:
[NativeCalibrationWorker](../../../Docs/StructTrain/TimeLearner/NativeCalibrationWorker.ru.md).
