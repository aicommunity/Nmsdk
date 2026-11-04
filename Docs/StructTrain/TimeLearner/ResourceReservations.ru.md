# Резервирование каталогов worker

Этап10, первый слой общей очереди. `resource_reservations.py` хранит leases
в локальном SQLite WAL с FULL synchronous и атомарным BEGIN IMMEDIATE.
Сетевые filesystem/NFS не поддерживаются. База привязана к worker hostname
и schema1; смена schema/worker запрещает дальнейшие операции.

API `Reservations(database)`:

- `reserve(job_id, resources, ttl_seconds=30)` получает уникальный token и
  сохраняет PID/start ticks/boot ID/UID/executable управляющего процесса.
- Resource задаёт дерево `path` и `access=read|write`. Пути нормализуются
  с разрешением symlinks; конфликтуют также родители и потомки дерева.
  Read/read разрешён; наличие хотя бы одного write запрещает пересечение.
- `validate_paths(token)` обязателен перед файловой операцией: сменившийся
  alias не даёт использовать старое разрешение для другого каталога.
- `heartbeat(token)` и `release(token,note=...)` разрешены только исходному
  процессу-владельцу, а не любому процессу, узнавшему token.
- `inspect()` отдельно показывает истёкший heartbeat и фактический статус
  владельца по /proc. Истечение времени, исчезновение PID и новая загрузка
  ОС сами по себе **не освобождают** ресурсы.

ID попытки сохраняется и после release. Повторный reserve с тем же job_id
не является retry: он отвергается. Новый повтор должен иметь собственный ID
и происхождение. Ни release, ни живой PID не создают execution/training/
scientific verdict.

Предполагаемые потребители: checkout source требует write source; сборка —
read source и write build/deploy; неизменяемый runtime используется с read.
Lease должен охватывать всю операцию, включая использующих эти пути children.
Нельзя закрывать его сразу после Popen. Все изменяющие файлы участники должны
использовать один ledger; неприсоединившиеся ручные writers этот API не блокирует.

Это ещё не dispatcher и не полный scheduler. Обязательная последующая работа:
публичный job spec/CLI, интеграция с production Train→Test и ConditionSpec,
реестр всех принадлежащих процессов, количественные memory/disk/slot budgets,
cancel, передача/инспекция после сбоя и доказуемое закрытие abandoned leases,
обе worker policies и Git publisher gates. Пока такой recovery не реализован,
abandoned lease остаётся held. Таймаут SSH не даёт права повторить задачу.

Подготовлены15 адресных проверок: совместные readers и запрет redeploy;
parent/child overlap и независимый sibling; heartbeat/expiry; crash владельца;
чужой token; два реальных конкурентных writers; symlink alias/его смена;
создание нового runtime; transaction rollback; неизвестные schema/worker;
недопустимые запросы и повреждённые held records. Численных моделей эти tests не запускают.

Приёмка source `637e2638805b240b8cc9a11a519569a781e93e6b`: все15 tests прошли
на Elder и M40, без failures/errors/skips. Это обычные Python/SQLite/process
controls, не ASan или numerical tests. Source blobs и все10 членов каждого
архива проверены независимо. Proofs:
`3685d33dc945eb39e87df8787cb534f3ad43a23d` (Elder) и
`25c391992a8e3d8bd97956f40661c4fafb0db4e1` (M40), разделы
`Reports/StructTrain/TimeLearner/s10-resource-reservations-{elder,m40}-a2`.
[ResourceReservationsVerification.json](ResourceReservationsVerification.json)
фиксирует386 Git source hashes на worker и фактические версии Python/SQLite.
Это приёмка reservation API; подключение его к production worker и вся
остальная очередь по-прежнему обязательны и не заявляются завершёнными.


## Атомарные количественные бюджеты schema2

`Reservations(database, capacity=policy)` выбирает schema2. Policy содержит
строго три положительных целых поля: `slots`, `memory_bytes`, `disk_bytes`.
Каждый `reserve(..., demands=...)` задаёт те же три поля: минимум один slot,
неотрицательные целые bytes, без bool/float или неявных единиц. В той же
SQLite-транзакции проверяются все конфликты каталогов и сумма demands всех
held leases. Неуспешная попытка не занимает ни ID, ни каталог, ни capacity.
Граница разрешена точно; превышение хотя бы одного измерения отвергается.

Capacity неизменна для существующей базы: она записывается вместе с worker
и schema и проверяется при каждой транзакции. Входные и возвращённые словари
не позволяют поменять учёт уже записанного резерва. `inspect()` возвращает
capacity, reserved и available. Даже истёкший lease или завершившийся owner
продолжает занимать capacity до корректного закрытия; автоматического retry
после timeout SSH нет.

Дисковый бюджет привязан к **реальному filesystem** базы (`st_dev`). Все write
каталоги должны находиться на нём; новый каталог проверяется по ближайшему
существующему предку, затем повторно через `validate_paths`. Read-источники
могут лежать на другом диске. Нельзя занять свободное место Data для записи
на почти полном системном диске. Перенос базы на иной filesystem не меняет
привязку автоматически и отвергается. Jobs с записью на нескольких volumes
пока не поддерживаются этим слоем; создание второго ledger ради обхода
ограничения нарушает правило одного общего worker ledger и общий учёт RAM.
Временные файлы компилятора/библиотек тоже должны входить в декларацию будущего
runner; этот API не перехватывает произвольную запись в `/tmp`.

Schema1 по-прежнему поддерживает прежний API без budget claims. Capacity и
demands в неё молча не добавляются. Старый клиент не может открыть schema2,
а schema2-клиент — schema1. Автоматической миграции или замены работающей базы
нет: перед будущим переводом общего worker ledger нужно подтвердить закрытие
всех старых owners/children и отдельно оформить перенос политики. Работающий
K1 продолжает использовать свой исходный schema1 code/ledger.

Это учёт **заявленных** ресурсов, не cgroup/OS quota, измерение actual RSS или
диспетчер. Нужны ещё actual worker policy по измерениям, production JobSpec/
ConditionSpec, полный owned process graph, cancel/recovery и Train→Test wiring.
Снимать lease при одном закрытом родительском процессе вместо всех потребителей
нельзя. Текущий API не подтверждает ни выполнение модели, ни её научный результат.

Source `63d7d6285ee8c8aa38221206037ce92ce50372e2` прошёл30/30 controls на
Elder и M40:15 прежних плюс15 budget/schema/filesystem tests, включая два
реальных конкурента с различными каталогами и настоящий `/dev/shm` filesystem.
Нет failures/errors/skips, численные модели не запускались. Независимо сверены
10 archive members и387 Git source hashes на worker; compressed archives
22712/22916 bytes. Proofs:
`cf00368b16818ec3224b1f2555056f5c9f5bb0ef` и
`58da4861160fbce9101dafac7ce71cc744b562e0`.
[ResourceBudgetsVerification.json](ResourceBudgetsVerification.json) хранит
точные hashes, runtime и counts. Предыдущий28-case срез до привязки диска не
используется как доказательство filesystem-защиты. Весь этап10 остаётся открытым.
