# Подключение whole-cgroup execution к native workers

Статус: реализация в отдельной ветке; серверная приёмка ещё не выполнена.
Исходные этапы1–12 остаются частичными. Уже работающие runtime не изменяются.

`native_pipeline_worker.run_job(..., process_policy=...)` и
`native_calibration_worker.run_job(..., process_policy=..., post_tune=...)`
принимают отдельную эксплуатационную политику. CLI train/preflight/export/
evaluate/diagnostic-evaluate/probe/calibrate run/posttune получает
`--process-policy Scripts/StructTrain/TimeLearner/specs/native-process-policy-cgroup-v1.json`.
Пример задаёт8GiB/128tasks и обязательный cooperative capture; реальные лимиты
нужно согласовать с ресурсным резервом задания. Это OS cap, не глобальная
очередь и не доказательство доступности всех объявленных ресурсов.

Научный JobSpec/condition hash, модель, временные/амплитудные допуски и native
C++ schema не меняются. Policy сохраняется отдельно в input/process-policy.json
и run manifest: pipeline schema4, calibration/PostTune schema2. Её нельзя
незаметно заменить legacy scope. Отсутствие policy сохраняет прежние API и
manifest formats для воспроизведения старых заданий. Новые проверенные runs
должны объявлять cgroup policy; автоматический перевод всех внутренних
pipeline/experiment orchestrators остаётся отдельным незавершённым пунктом.
Fallback после ошибки запуска запрещён.

Native process и все descendants запускаются через проверенный contained_runner.
Completion требует окончания всей группы, а не только main PID. Timeout и
cancel.request прекращают принадлежащую заданию группу; frontend crash оставляет
наблюдаемую unit для recovery. Cooperative ready/ack обязателен во всех native
операциях, включая быстрый export/preflight. Build/Reset/Calculate не меняются.

Общий portable auditor сверяет signed request/binding, runtime fingerprint,
actual memory/task/swap readback, original argv/cwd, exact main PID/start/boot,
cooperative ready/ack, actual loaded mappings, terminal status и whole-group
closure. Архив разбирается без local /proc/systemd/SDK; original paths сравниваются
между собой. Это внутренняя согласованность evidence, не authentication
произвольных записей о kernel и не scientific/native_execution attestation.
Отрицательная попытка с неполным launch/closure не получает native analysis.

До merge необходимы: серверные policy/portable tamper tests на реальных
сохранённых C++ process records; адресные реальные production preflight/probe,
Train/export/evaluate, calibration и PostTune с новым backend; сохранение
legacy adapters; timeout/cancel и отказ launch/capture. Надпись «реализовано»
не заменяет эту runtime-приёмку.
