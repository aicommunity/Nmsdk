# Полная группа процессов в native gate

Статус: адресная серверная приёмка выполнена на Elder и M40. Работающие задания
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

## Приёмка

Source `5c72b70b54f6ff9ae911f2ba7089eb7a8ffc3f3c`:
на каждом worker77/77 Python controls без failures/errors/skips. Это11 новых
runner controls,9 прежнего process_runner,8 JUnit/environment readers и49
reservations/budgets/contained/recovery controls. Дополнительно реальный
native-gate schema3 выполнил2 существующих C++ codec/storage cases на
неизменяемом SDK `b82f76e2fe543acf25d6c3076abbd864f965b3a8`:
normal Elder и ASan M40. Это не новый SDK build и не coupled C-search проверка.

На каждом сервере сверены275 Python source blobs,28 уникальных unit attempts,
27 kernel limit readbacks и27 final test closures; дополнительный native gate
имеет собственный whole-group closure. Actual native maps содержат hash
объявленного executable; ready/ack совпадают с первоначальным main identity.
Отдельный readback подтверждает MainPID0 при живых потомках до timeout.
[Независимая сверка](ContainedRunnerVerification.json) проверяет все422/420
members новых primary archives и исходные предыдущих попыток.

Proofs `df72d059f9540c6237f5cf680d2748bba228eb42` и
`dbbacf0c1be37c67479d9da5288c111e9209c870`. Сжатые primary имеют45508/50660
bytes; предыдущие отказанные попытки также сохранены в Git.

Первый a1 запуск не принят:70 tests и один skipped reader class из-за
необъявленного actual JUnit fixture. a2 правильно отказал до запуска native
program: manifest старого runtime ссылался на прежний root/Rdk, тогда как его
исходный каталог уже обновлялся. Выбрана согласованная b82 runtime/source
комбинация, без изменения provenance guard. a3 на Elder выявил настоящую
гонку чтения /proc/exe → /proc/maps при выходе main; M40 этот срез прошёл.
Теперь только точное отсутствие executable mappings классифицируется как
incomplete capture, и наблюдение cgroup продолжается. Другие integrity errors
сохраняют отказ. a5 повторно прошёл всю матрицу с реальным descendant readback.
Ни старые результаты, ни исходные критерии не переписаны.

Уточнение границы приёмки: воспроизведён [разрыв lease owner и managed unit](WorkerUnitGraphBaseline.ru.md).
Закрытие одной worker cgroup не доказывает завершение отдельно запущенных
user-systemd units. До учёта всего зарегистрированного графа такой recovery
нельзя считать разрешением освобождать общий SDK/runtime нового pipeline.
Прежние tests сохраняют силу для своего конкретного охвата.
