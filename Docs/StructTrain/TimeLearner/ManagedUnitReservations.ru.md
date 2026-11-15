# Managed-unit leases, registry schema3

Статус: отдельная ветка, серверная приёмка pending. Исправляется fault baseline
WorkerUnitGraphBaseline.ru.md; код не присваивает приёмку по самому факту наличия.

Явный `Reservations(database, capacity=..., managed_units=True)` создаёт только
новую схему3. Capacity/demands имеют slots, memory_bytes, disk_bytes, tasks.
Никакой автоматической миграции schema1/2 нет. Старый API отказывает при schema3;
owner identity/PID/start_ticks сохраняют прежний реальный смысл без маркеров.
Реестры работающих K1/normal304 не изменяются.

Managed reserve требует controller_directory реальной содержащей caller unit.
Фактические memory.max/pids.max/swap прочитаны из kernel и сохранены; parent PID/
start/binding должны совпадать с lease owner. Новые managed units учитываются
сверх cap контроллера, который уже включает его обычных fork descendants.
Сумма этих caps не может превышать зарезервированные memory/tasks. Регистрация
ещё не запущенных units также потребляет бюджет; отсутствие heartbeat не
освобождает его. Заявленные limits не выдаются за фактическое потребление.

`contained_process.start(..., managed_reservation=(registry, token))` выполняет:

```text
validate immutable runtime and ownership context
register unique unit/attempt/directory intent in SQLite (before creation/launch)
write signed native request
commit submitted state before manager call
create real unit and obtain helper binding + actual kernel limits
commit bound state before native start.ack
```

До submission ошибка явно abort-ит незапущенный intent. После неоднозначного
submission unit остаётся reserved; отсутствие полной binding/closure не
переклассифицируется в освобождение. Release/recovery свежо проверяет все
зарегистрированные units и их cgroups. Живой/pending/unknown участник оставляет
lease held. Recovery также требует точный закрытый controller binding и его
kernel group. Его receipt включает весь проверенный managed-unit graph.

Targets должны лежать внутри принадлежащего lease write output; alias,
повторная registration и превышение суммарного бюджета запрещены. Registry
inspect показывает записанные состояния, прямо помечая их declarations, а не
свежей runtime-аттестацией. Global budgets и OS caps остаются разными сущностями.

Двенадцать подготовленных real Linux tests проверяют границы controller/units,
RAM/tasks, unused intents, duplicate/escape, реальную filesystem failure до
submission, старые API и повторяют parent-closed/child-live fault. Также нужно
пройти все49 legacy reservation/budget/contained/recovery controls, сохранить
primary и завершить normal/ASan production worker integration. Подключение к
native_process_policy и общему scheduler ещё pending. Build/Calculate/Reset,
образы storage, математическая цель и научные tolerances не меняются.
