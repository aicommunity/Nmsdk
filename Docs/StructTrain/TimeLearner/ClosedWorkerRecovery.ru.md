# Явное восстановление резерва завершённого worker

Статус: реализация в отдельной ветке; серверная приёмка ещё не выполнена.
Это часть этапа10, а не приёмка всего scheduler.

`Reservations.recover_closed_worker(token, contained_directory, note=...)`
применим только к lease, владельцем которого был первоначальный main PID
службы `contained_process`. Сравниваются PID, start ticks, boot ID, UID и
request/binding. Живой, неизвестный либо относящийся к другой загрузке владелец
не допускается. Свежий `contained_process.inspect` должен подтвердить отсутствие
всех процессов в соответствующем cgroup. Закрытая дочерняя служба внешнего
controller не подтверждает завершение этого controller и не позволяет recovery.

В одной SQLite write transaction сохраняются полный recovery event и перевод
lease в released; `recovery_history()` читает события. Исходные schema1/schema2
и capacity policy сохраняются. Повторный recovery отклоняется как not-held.
Истечение heartbeat, исчезновение SSH, кэшированный closure-файл и отсутствие
только main PID недостаточны. Чужой unit и прежняя загрузка запрещены.

Это административное освобождение ресурсов с обязательной причиной, а не
доказательство успешного выполнения или научного результата. Поля
`scientific_verdict=null` и `successful_execution_attested=false` явные.
Автоматическая очередь, восстановление старых outside-controller leases,
межсерверные locks и полное восстановление журнала запуска ещё не реализованы.

Серверные проверки используют настоящий user-systemd, cgroup2 и production
SQLite API: живой осиротевший child; остановка всей группы; восстановление и
перечитывание capacity; schema1; неверный закрытый unit; внешний controller;
живой владелец; пустая причина; другой boot; повторный recovery. Полные наборы
существующих reservation/contained tests также подлежат повторному выполнению.
