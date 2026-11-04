# Native workers + managed-unit resource registry integration

Статус: отдельная объединённая ветка, адресные runtime checks pending.
Ветка объединяет source1fd77d34f worker hooks и schema3 source34394c301 через
merge commits. Исходные native SDK/gitlinks, физика и learner algorithms не
меняются. Принятые baseline/M4061 и portable15 evidence сохраняются.

Policy schema1 остаётся прежним bounded-cgroup protocol для чтения прошлых
запусков. Новые связанные attempts используют schema2 policy с reservation
(database, capacity, token) реального schema3 lease. Он принадлежит тому же
процессу, который вызывает native worker; незаметной передачи token другому PID
нет. `policy_for_reservation(registry, token, memory_bytes=..., tasks=...)`
проверяет context и создаёт только эксплуатационную policy, без изменения
научного JobSpec/hash. Для CLI такой файл создаёт coordinator с правильным
owning process; self-allocation/delegation общего scheduler ещё pending.

contained_runner передаёт context в contained_process до native submission.
Зафиксированы и проверяются original intent, owner/controller PID/start/boot,
actual unit binding, родительский/дочерний caps и выделенный budget.
process/reservation-context.json хранит переносимую связь с lease и intent.
Portable auditor сравнивает её с policy, signed request/binding и runtime
records; живой локальный SQLite на машине анализа не требуется. Это evidence
consistency, не authentication произвольных файлов и не scientific verdict.

Подготовлены два actual public CLI preflight controls Classic N0/Branch N1,
использующие реальные immutable Console и прежние cold job templates. Проверка
требует model_ticks0/training_started=false, корректный manifest v4, bound
managed intent и release только после closure. Переподписанная подмена lease
в скопированном run должна отклоняться. Эти controls не подменяют Train/export/
evaluate/calibrate/PostTune, которые ещё требуют отдельных actual runs и matrix.
Прежние15 policy/portable tests дополнены двумя schema2 validation checks.

Рекомендуемость backend и завершение исходного этапа10 пока не присваиваются.
Активные K1/normal304 runtime не обновляются, их реестры не мигрируют.


Дополнительный контроль до запуска: direct contained_process path повторно
проверяет исходные aliases reservation перед регистрацией intent и каждой
сменой его состояния. Если symlink после reserve указывает на другой каталог,
submission запрещён с reservation_path_alias_changed. Подготовлен реальный
Linux symlink test: native unit и intent не создаются, исходный alias
восстанавливается перед release. Это новая правка после source343; прежние
61/61 её не проверяли. Требуется повторная suite62 (13 новых +49 прежних) и
отдельные19 policy/preflight checks. Локально выполнен только разбор AST,
серверная runtime-приёмка этой правки пока отсутствует.
