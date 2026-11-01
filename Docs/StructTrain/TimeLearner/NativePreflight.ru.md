# Эффективная проверка перед cold Train

Рабочая реализация отдельного native preflight; совместная normal/ASan приёмка
пока не завершена. Normal-корпус уже проверен, источники приведены ниже.
Команда использует тот же training job schema1/2 и тот же путь создания owner,
регистрации immutable storage profiles, Build/Init/Reset, проверки параметров
и semantic graph identity, что и production Train.

```text
python3 -m Scripts.StructTrain.TimeLearner preflight JOB.json \
  --runtime-manifest RUNTIME.json --wall-seconds 120 --output NEW_DIRECTORY
```

Console-вход — `--timelearner-preflight JOB.json --timelearner-output NEW_DIRECTORY`.
Он несовместим с Train, project execution и inspection options. Запрос не является
новой разновидностью обученной модели; сам JOB остаётся training declaration.
`--source-solo` для preflight запрещён, как и для cold Train.

Перед первым Calculate общий путь проверяет допустимость search domain для
эффективных параметров, реальные каналы через AssessNativeIntegration и
неизменность identity при read-only assessment. Во время подготовки controller
должен оставаться Idle, без reference probes, observations, references или
certificate; probe executor также Idle. Модельное время не должно измениться.
Preflight возвращается до создания EvidenceWriter и до установки запроса Train.

Положительный native результат содержит только job.json, initial-state.json и
execution.json: effective graph/parameters, integration channel bounds, нулевое
число тиков и отсутствие начатого обучения. Runner сохраняет source/runtime,
owned process и загруженные файлы штатным путём. Portable audit проверяет
согласованность артефактов; он не удостоверяет происхождение произвольного
внешнего файла и не выдаёт научный verdict.

Проверка настройки ещё не подтверждает наличие измеримого пика, сходимость,
качество распознавания или пригодность всех будущих кандидатов роста. После
каждого изменения физики/геометрии остаются обязательными production проверки
интегратора и новые измерения. Optional C-trim и прочие неподдержанные modes
нельзя объявить работающими только из-за появления команды preflight.

План проверки: реальные schema1/2 jobs Classic/Branch, N0/N1; отсутствующие
и неверные поля, legacy-фактор в V2 declaration, пустые окна, несовпадение
частот, нулевой measurement budget, запрет старта Train; реальные one-tick
Train controls для общего подготовительного пути; rehashed corruptions
clock/training flags/parameters/integration/extra certificate. Сборки и тесты —
на Elder/M40, без локальной численной приёмки. Полные этапы2/4/9/10 открыты.

## Normal evidence

На Elder root `ec24ae157fff785ead8a38bc658c55bd18e5ae0c` прошёл14 реальных
schema1/2 jobs Classic/Branch,N0/N1,2inputs,2000Hz; отклонены6 неверных
деклараций, включая legacy SyncTolerance в V2 JSON. Два one-tick Train получили
идентичный initial-state с preflight и остановились по заявленному бюджету,
а не завершили обучение. Все10 actual-data/corruption checks прошли без skips.

Primary commit `aded6d28f0a16327fb536e3090c3cd5db93158bc`:
[отчёт и все входы/исходы](../../../Reports/StructTrain/TimeLearner/s09-native-preflight-current-normal-a1/README.md).
Проверены все276 members и outer hashes; сжатый архив108128 B. ASan и полная
размерная/физическая матрица пока не приняты. Ни один исход не является
доказательством научной классификации.

## Подготовка размерной матрицы

Для следующей проверки добавлен production `prepare SPEC.json --output NEW_DIR`.
Он не выполняет модель. SPEC schema1 имеет kind
`timelearner_native_matrix_preparation`, четыре полных cold templates в
`templates` (ключи Classic-N0,Classic-N1,Branch-N0,Branch-N1), массивы
`input_counts` и `frequencies_hz`, положительные `isi_seconds`, `probe_duration`,
`window_width`, N0 `n0_candidate_repeats`2..128 и непустой `run_prefix`.

Для каждого N сохраняются параметры и bounds последнего опорного входа исходного
template; копируется только первый неопорный вход. Storage profile definitions
не меняются, никакой fallback C не подставляется. При N=1 остаётся исходный
опорный вход. Inhibition templates отвергаются до явного определения remapping;
live finalization templates также не превращаются неявно в cold templates.
Допуски амплитуды/синхронизации не масштабируются при смене N или частоты.
Проверяются clipping окон, уникальность осей и ограничение sample budget.

Output содержит specification.json, jobs/*.json и signed manifest. Поля
runtime_checked/effective_model_checked/training_started остаются false;
подготовленные jobs требуется реально проверить через preflight.

Две первые попытки дополнительного размерного запуска не запустили модели:
ошибочный импорт verify_runtime, затем несовпадение QT_QPA_PLATFORM с сохранённым
runtime. Их исходные receipts сохраняются; это setup failures, не отрицательные
результаты моделей. Генерация jobs переносится из одноразового launcher в prepare;
его серверная приёмка и повтор размерной проверки ещё впереди.

Следующая попытка с production prepare6896144a3 прошла18 Python checks, но
первый настоящий Console preflight отклонил windows в виде массивов:
native codec требует объекты begin/end. Это ошибка генератора, выявленная
до построения модели, а не физическая неудача. Исправлены output и проверка
формата относительно реальных templates; обязательный повтор всех32 native
cases остаётся незавершённым. Python checks отдельно не доказывают native codec
compatibility; исходный отказ сохраняется вместе с остальными setup attempts.

После исправления codec все18 Python checks прошли. Первая маленькая модель
завершила native preflight, но parent не успел прочитать mappings до выхода;
pipeline отверг её с pipeline_loaded_runtime_missing. Эта попытка не принята.

## Подтверждение actual runtime для быстрых jobs

Добавлен optional Console/supervisor обмен после окончания native job. Console
публикует capture-ready с PID/start_ticks и ждёт ACK не более10 секунд. Parent
проверяет owned identity, непосредственно читает /proc/exe и /proc/maps,
проверяет inode/hash mapped files и только затем подтверждает capture. Child
не передаёт выдуманный список библиотек; public loaded_files_captured требует
настоящего наблюдения parent. Это point-in-time snapshot, не утверждение о
полном времени жизни всех когда-либо загружавшихся библиотек.

Для preflight runner включает этот обмен; для остальных execute-вызовов default
остаётся прежним. Зарезервированный capture directory назначает supervisor.
Ожидание происходит после native работы, не вызывает Calculate/Reset/Build
и не изменяет model time. Wall budget включает ожидание. Portable audit проверяет
request paths, PID/start_ticks и обе receipts; исторические passive snapshots
читаются по прежнему контракту. Серверная приёмка этого изменения ещё не выполнена.
