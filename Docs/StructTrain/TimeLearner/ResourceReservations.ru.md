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

Подготовлены14 адресных проверок: совместные readers и запрет redeploy;
parent/child overlap и независимый sibling; heartbeat/expiry; crash владельца;
чужой token; два реальных конкурентных writers; symlink alias/его смена;
создание нового runtime; transaction rollback; неизвестные schema/worker;
недопустимые запросы. Численных моделей эти tests не запускают. До проверок
на обоих серверах реализация не имеет runtime acceptance.
