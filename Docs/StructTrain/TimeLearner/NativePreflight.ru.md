# Эффективная проверка перед cold Train

Адресно приняты production `preflight` и декларативный `prepare`: реальные
normal/ASan проверки на Elder/M40, одинаковые начальные модели и сохраняемая
фактическая runtime closure. Приёмка ограничена описанными ниже fixtures;
полные этапы2/4/9/10 и поддержка всех физических профилей остаются открытыми.

## Общий native путь

```text
python3 -m Scripts.StructTrain.TimeLearner preflight JOB.json \
  --runtime-manifest RUNTIME.json --wall-seconds 120 --output NEW_DIRECTORY
python3 -m Scripts.StructTrain.TimeLearner prepare SPEC.json --output NEW_DIRECTORY
```

Console-вход — `--timelearner-preflight JOB.json --timelearner-output NEW_DIRECTORY`.
Он несовместим с Train, project execution и inspection options. JOB остаётся
training declaration schema1/2; `--source-solo` запрещён, как и для cold Train.
Общий с Train путь создаёт owner, регистрирует immutable storage profiles,
выполняет штатные Build/Init/Reset, читает effective parameters и semantic graph.
Проверяются search domain и реальные каналы через AssessNativeIntegration.
Read-only assessment не должен менять identity. Контроллер и probe executor
остаются Idle: без references, observations, certificate или начатого Train.

Preflight возвращается до EvidenceWriter, IsNeedToTrain и Calculate. Native
output содержит только job.json, initial-state.json и execution.json, ноль
модельных тиков и неизменные часы. Не вводятся вложенный Calculate, особый
«будящий» Build, fallback C или новый смысл публичных lifecycle bool.

Portable audit проверяет согласованность primary data и receipts, но не
удостоверяет подлинность произвольных внешних файлов. Корректное создание
модели не доказывает измеримый пик, сходимость, качество классификации либо
устойчивость всех будущих кандидатов роста. После изменения физики/геометрии
по-прежнему обязательны оценка интегратора и свежие измерения.

## Декларативный prepare

SPEC schema1 имеет kind `timelearner_native_matrix_preparation`, четыре полных
cold templates `Classic-N0`, `Classic-N1`, `Branch-N0`, `Branch-N1`, уникальные
целочисленные массивы input_counts/frequencies_hz, положительные isi_seconds,
probe_duration/window_width, n0_candidate_repeats2..128 и непустой run_prefix.

Для каждого N сохраняются параметры и bounds последнего опорного входа;
повторяется первый неопорный. При N=1 остаётся исходный опорный вход. Storage
profiles, классы, физика и численные допуски не меняются. Заявленная частота
применяется через ModelSpec и согласованный stimulus profile. Окна записываются
штатными объектами begin/end, проверяются clipping и sample budget. Inhibition
и live-finalization templates отвергаются до явной реализации remapping.

Output: specification.json, jobs/*.json, signed manifest. Генерация не исполняет
модель: runtime_checked/effective_model_checked/training_started остаются false.
Каждый job требует отдельного native preflight. Скрипт не масштабирует допуски
амплитуды/синхронизации автоматически при смене размерности или частоты.

## Фактический runtime быстрых процессов

Optional Console/supervisor обмен выполняется после native job, перед разрушением
AppCore. Console публикует capture-ready с PID/start_ticks и ждёт ACK до10 секунд.
Parent сверяет owned identity, непосредственно читает /proc/exe и /proc/maps,
проверяет inode/hash mapped files и только затем подтверждает capture. Child
не подставляет список библиотек. Это point-in-time snapshot, не полный census
всех библиотек за время жизни процесса. Wall budget включает ожидание.

Для preflight runner включает обмен; default других execute-вызовов сохраняется.
Capture directory назначает supervisor; caller не может подменить reserved arg.
Ожидание не вызывает Calculate/Reset/Build и не меняет model time. Audit проверяет
полный argv, directory, PID/start_ticks и обе receipts. Старые passive snapshots
читаются по прежнему контракту. Повреждённый ACK/identity блокирует приёмку.

## Серверная приёмка

На каждом worker прошли14 положительных schema1/2 preflights, отклонены6 неверных
деклараций: четыре native configuration failures и две descriptor errors.
Покрыты legacy-фактор в V2, пустые окна, frequency mismatch, нулевой measurement
budget, unsupported C-trim и неверный owner. Два настоящих one-tick Train controls
имеют те же initial graphs и остановлены по бюджету: это не завершённое обучение.
20/20 actual-data/prepare/corruption checks на каждом worker, без skips.

Production prepare создал32 jobs на каждом worker:
Classic/Branch × N0/N1 × N=1/2/4/6 × 2000/20000Hz. Все32 реальные native preflights
приняты с0 model ticks. Проверены фактическое число параметров и частота каждого
узла дерева. Все46 initial semantic identities, параметры и configuration hashes
равны между workers; равны все32 prepared job hashes. Одинаковый Branch graph для
нескольких размерностей сам по себе не доказывает равенство задач: declarations
и массивы индивидуальных параметров проверяются отдельно.

Normal binary root `d2bf789f2a6e744fedcd29aefc3ed405eaea0fc8`, Python analysis и
ASan binary root `f198767189494d7ffb5096afebc14edf858aad55`. Console source tree
одинаков: `b85cd2663c76e3eb17222e318ce903f1ced3e38f`. PulseLib Core tree одинаков
для numeric ecf35a6 и принятого develop456a5ab. Различия поздних child commits
документальные; исходные source/runtime manifests сохранены без переименования.
Все52 ASan process loaded-files snapshots содержат реальную libasan.

- Normal primary commit `81a0f9d9a9aab7f2ef839bfe5a0c6f8b6bebd3b0`:
  [824 проверенных members,258004 B](../../../Reports/StructTrain/TimeLearner/s09-native-preflight-current-normal-a2/README.md).
- ASan primary commit `12402b21f686398069f4ecfb0165de117357bcbf`:
  [820 проверенных members,257144 B и crossworker comparison](../../../Reports/StructTrain/TimeLearner/s09-native-preflight-current-asan-a1/README.md).

В Git сохранены сжатые primary, входы, actual graphs/parameters, process/runtime
receipts, ready/ACK, подготовленные jobs и метрики. Временных кривых здесь нет:
preflight не рассчитывает отклик. Отчёты реального Train/Test по-прежнему должны
показывать соматический потенциал с входными импульсами в читаемом масштабе.

## История отказов и ограничения

Первый normal корпус без cooperative capture: commit
`aded6d28f0a16327fb536e3090c3cd5db93158bc`,276 members/108128 B,10 reader checks.
Это прежний ограниченный снимок, не текущая размерная приёмка.

[Setup baselines](../../../Reports/StructTrain/TimeLearner/s09-native-preflight-setup-baselines-normal-a1/README.md),
commit `b7081f59debacbb217a428b1e7645f17cbcfac2a`,128 проверенных members:
ошибочный import, loader environment mismatch, неправильный windows codec,
пропущенный fast-exit mapping и неверно адресованные setup metadata. Последние
восстановлены побайтно из Git: все276 прежних файлов совпали; изменённые receipts
сохранены до восстановления. Уникальные научные данные не удалялись.

Normal primary также сохраняет первоначальный отказ аудитора с устаревшим
ограничением на6 argv вместо нового допустимого8. ASan comparison сохраняет
ошибку reporter field name и её исправление без изменения моделей. Эти отказы
не учитываются как успешные испытания. При публикации ASan Git отклонил неверно
выбранную уже существующую destination branch; результат опубликован в отдельную
ASan branch без замены удалённой истории.

Не проверены этим подэтапом: все inhibition/heterogeneous profiles, multirate,
все режимы C-trim/PostTune, полная scheduler recovery/publication matrix,
измерения после роста, legacy/V2 A/B и независимая классификация. Ноль Calculate
не заменяет эксперимент на модели; научный verdict во всех receipts — null.


## Актуальная версия worker-аудита (02.11)

Новый pipeline run manifest schema2 также анализирует структурированный
exit2 training job schema1. Process error и diagnostic incomplete boundary
сохраняются; valid означает consistency данных, не успех обучения. Старые
manifest schema1 сохраняют прежнюю политику. Команда preflight-regression
исполняет декларативный maintained root workflow14+6+2 с environment до
runtime snapshot. Реальные проверки и exact sources/limits:
[StructuredTrainingExit](StructuredTrainingExit.ru.md).
