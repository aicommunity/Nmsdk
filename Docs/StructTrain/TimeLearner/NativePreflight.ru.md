# Эффективная проверка перед cold Train

Рабочая реализация отдельного native preflight; приёмка пока не завершена.
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
на Elder/M40, без локальной численной приёмки. На этом снимке эти проверки
ещё не выполнены; полные этапы2/4/9/10 остаются открытыми.
