# Полная группа процессов в native gate

Статус: кандидат, серверная приёмка ещё не выполнена. Работающие задания
используют свои прежние immutable source/runtime и этим кодом не изменяются.

`contained_runner.execute` объединяет проверенный `contained_process` с
фактическим runtime capture. Сохраняются stdout/stderr, manifest, точный
PID/start ticks, invocation/cgroup, kernel limits, конечное состояние службы
и отдельный whole-group closure. Положительный exit main процесса недостаточен,
пока жив его потомок. Отмена/timeout останавливают только эту invocation
с подтверждением отсутствия всех её процессов. Потеря frontend оставляет
наблюдаемую службу; `inspect_attempt` не превращает это в completed.

Загруженные файлы читаются из настоящего native PID после exec, а не из
подготовительного Python helper. Optional cooperative capture использует
прежние ready/ack identity fields; неверный PID/start ticks запрещает ack.
Fast exit без capture оставляет provenance incomplete и не допускается
native gate как достоверная runtime observation. После завершения повторно
проверяется неизменность объявленного runtime. Модельное время не подменяется
wall time; scientific verdict всегда null.

Результат этого backend имеет schema2 и ownership_scope=bound_cgroup.
Прежний process_runner/schema1 не изменён. `native_gate` schema1/2 сохраняют
старые контракты; schema3 явно требует `process_limits={memory_bytes,tasks}`
и boolean `cooperative_runtime_capture`. Wall budget должен быть1–86400s.
Перед положительной оценкой JUnit schema3 дополнительно проверяет полный
closure. ASAN_OPTIONS и TIMELEARNER_EXECUTION_OUTPUT явно передаются unit;
loader environment берётся из immutable runtime manifest.

Это подключение native gate, а не полная миграция всех Train/Test workers,
очереди, leases, condition projection и publisher. Автоматическое возобновление
прерванного научного опыта не вводится. Новые neural результаты и полный
рефакторинг на основании инфраструктурных tests не принимаются.
