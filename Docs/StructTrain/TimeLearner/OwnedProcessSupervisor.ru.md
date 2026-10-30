# Владение процессом исполнения

Подэтап 10, ветка stage10/owned-process-supervisor. Модуль process_runner.py
запускает один объявленный executable, регистрирует его identity и управляет
таймаутом/отменой. Это слой исполнения, не готовый экспериментальный runner,
очередь ресурсов или доказательство завершённого Train.

## Контракт

```text
python3 -m Scripts.StructTrain.TimeLearner.process_runner --runtime-manifest runtime.json
  --working-directory RUNTIME --output NEW_ATTEMPT --wall-seconds 60 -- ARGUMENTS
```

Используется runtime schema 2 из runtime.py. Проверяются content fingerprint,
executable, app.ini, compiler, resolved libraries и переданные loaded-file
records. Фактическое loader environment должно совпасть с manifest.
Пути приложения и runtime берутся из manifest; имена .rs1/.rs2/.e05b не
считаются отдельными неподконтрольными типами программ.

Attempt directory создаётся исключительно новым. В нём сохраняются runtime.json,
request.json, stdout.log/stderr.log, owned-process.json, loaded-files.json при
доступности и result.json. JSON записывается через соседний pending файл,
fsync и atomic replace. Отсутствующий result не достраивается из кода выхода
старого shell. Логи не ограничены размером: лимит хранения остаётся задачей
полного scheduler/resource policy.

При запуске сохраняются PID, Linux boot ID, process start ticks, реальный
executable path/hash и runtime fingerprint. Открытый pidfd закрепляет конкретный
процесс для сигналов. Timeout использует monotonic wall time, отдельно от model
time; model_time здесь null. Cancel request — появление cancel.request в attempt
либо явно указанного --cancel-file. Существующий запрос отмены до запуска
отвергается, а не теряется.

По timeout/cancel отправляется SIGTERM через pidfd, затем при необходимости
SIGKILL тому же процессу после grace period. При обработке ошибок Popen остаётся
владельцем unreaped child, поэтому cleanup не ищет процесс по имени. Сигналы
всему серверу, чужим PID и по маске executable не используются.

Снимаются реальные executable mappings /proc/PID/maps. Если процесс успел
завершиться раньше, provenance остаётся incomplete_loaded_files; отсутствие
readback не превращается в подтверждение runtime closure. Подтверждённая
подмена executable/mapped file является ошибкой runtime. После завершения
повторно проверяются исходные manifest files: изменение app.ini/бинарника/
библиотеки делает результат process_error с invalid_or_incomplete_runtime.
Mapped files — point-in-time capture, не доказательство полного набора plugins,
загруженных позднее; полный production runtime gate ещё обязателен.

result.execution: completed только при exit 0 без обнаруженной runtime ошибки;
nonzero exit — process_error; timeout и явная отмена имеют собственные статусы.
scientific_verdict всегда null. Даже completed с incomplete_loaded_files не
может автоматически становиться валидным результатом эксперимента.

inspect_attempt — read-only диагностика. При наличии result возвращает его;
без него сравнивает boot ID/start ticks/executable с живым процессом. При
несовпадении или исчезновении возвращает unknown, а не completed. После
восстановления связи нужно инспектировать прежний attempt, не перезапускать
его только из-за timeout наблюдения.

## Область и открытые ограничения

ownership_scope сейчас launched_executable_only. Отдельные дочерние процессы,
fork/daemon и полное дерево задания ещё требуют cgroup/иного проверенного
ownership механизма. Для проверки neural workers, которые запускают дочерние
бинарники, текущего слоя недостаточно. Не заявляется полное убийство process
tree по timeout.

Также остаются resource reservation/queue/lease, crash recovery supervisor,
restart/cancel после восстановления отдельного worker, защита полных resources
и библиотек на всём жизненном цикле, связывание с ConditionSpec и Train→Test,
полная worker policy и Git publication только после всех experiment gates.
Само наличие execute API не закрывает эти требования.

## Проверки

Source f7a862c645845a15e51d69d60184ca66f21aef09 прошёл 7/7 на каждом worker.
Используются реальные /bin/sleep и /bin/sh, скопированные под suffix-именами:
живое identity, actual mappings, timeout, отмена, nonzero exit и stdout/stderr,
отказ изменения исходного runtime/повторного attempt, unknown/stale state и
SIGKILL для процесса с игнорированием TERM. Отдельный посторонний sleep остаётся
живым при таймауте принадлежащего заданию процесса. Это infrastructure controls,
не нейронные эксперименты и не независимые научные повторы.

Source 9195208a9 добавляет runtime mutation во время работы и настоящий module
CLI. На обоих workers прошли 9/9 адресных и 35/35 совместных
process/runtime/condition/publisher tests без skips/failures/errors; все process
statuses 0. Reports: Elder f80ea87d8502902d3086d98fa0129a8df42d8918;
M40 37588a9c6b3f411250cf77d48acbd2737c0fd6d6. В каждом пакете локально
проверены все 9 stored / 7 raw hashes, включая декомпрессию. Подэтап готов
к приёмке в полном runner. Объединён в develop: 54e9fa8ece12e43571814ca04704e7529b23b4cd; полный этап 10 остаётся незавершённым.
