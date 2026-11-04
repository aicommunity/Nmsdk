# Явное восстановление резерва завершённого worker

Статус: адресная серверная приёмка выполнена на Elder и M40.
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
существующих reservation/contained tests также повторно выполнены.

## Проверенный срез

Source `adc1f6227144360097b378a33e1db564794e0442`: по49/49 на каждом
сервере, без failures/errors/skips:15 reservations,15 budgets,13 contained
processes,6 recovery. В каждом архиве223 файла,273 исходных Python blobs
сверены с Git,18 закрытых cgroups,17 kernel limit readbacks и3 сохранённых
recovery events с повторно прочитанными released ledgers. Нейронных прогонов0.

Proofs `989d03fab5133d2b37d7a90b4f904082e574cee0` и
`035832fca10aa1747f9e3bf78dcd560fdcd6ea0f`; подробная независимая сверка
в [ClosedWorkerRecoveryVerification.json](ClosedWorkerRecoveryVerification.json).
Первый запуск a1 имел13 ошибок сохранения доказательств из-за повторного
обнаружения импортированного класса тестов; не принят. a2 прошёл49/49;
в a3 дополнительно сохраняются реальные recovery events и ledger readbacks.
Исходные архивы a1/a2 включены в новые proofs, без изменения результатов.

В Elder proof также сохранён сжатый журнал удаления1832 старых CMake `.o`
в четырёх закрытых сборках:815872568 bytes. Зависимости `_deps`, готовые
библиотеки, исходники, модели и результаты не удалялись. Перед удалением
проверены реальные пути, CMakeCache, открытые handles и mappings процессов.

Уточнение границы приёмки: воспроизведён [разрыв lease owner и managed unit](WorkerUnitGraphBaseline.ru.md).
Закрытие одной worker cgroup не доказывает завершение отдельно запущенных
user-systemd units. До учёта всего зарегистрированного графа такой recovery
нельзя считать разрешением освобождать общий SDK/runtime нового pipeline.
Прежние tests сохраняют силу для своего конкретного охвата.
