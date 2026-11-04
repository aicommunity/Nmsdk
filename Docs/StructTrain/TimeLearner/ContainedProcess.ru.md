# Учёт полного дерева локального задания через user-systemd

Этап10: `contained_process.py` добавляет отдельный API `start/inspect/stop/adopt`.
Он использует реальный cgroup v2 пользовательской службы systemd на Elder и
M40. Старый `process_runner.execute` и его исторические схемы не изменены.
Работающие K1 и прочие задания на новый backend не переводились.

## Контракт

`start(manifest, arguments, working_directory, output, memory_bytes=...,
tasks=..., maximum_wall_seconds=...)` принимает прежний runtime manifest2
и явно заданные RAM/task/wall limits. Создаётся новый immutable output directory
и UUID имени службы; повторное использование output отвергается. Start
проверяет файлы runtime до запуска и ещё раз перед разрешением реального exec.
Это **не** новое подтверждение фактически загруженных библиотек: runtime maps/
cooperative capture ещё нужно соединить со штатным native pipeline.

Сначала записывается signed launch intent. В службе стартует маленький launcher,
который сообщает свой PID/start_ticks и ждёт ACK. Контроллер проверяет MainPID,
фактическую принадлежность к cgroup, InvocationID и реальные `memory.max`,
`memory.swap.max`, `pids.max`. Binding и kernel readback записываются до ACK;
затем launcher через exec становится указанным executable с тем же PID.
Аргументы передаются массивом, модельные конфиги не переписываются. Loader
keys задаются явно; только ASAN_OPTIONS и TIMELEARNER_* разрешены дополнительно.

Служба имеет Restart=no, RemainAfterExit=yes, KillMode=control-group,
MemorySwapMax=0, самостоятельный RuntimeMaxSec и ограниченное время остановки.
Ни MainPID=0, ни выход родителя сами по себе не закрывают задание: populated
из `cgroup.events` учитывает потомков, включая создавших новую session.
`inspect()` возвращает отдельно `all_processes_closed`; execution не становится
completed по одному пустому cgroup. Успех Train и научный verdict не выводятся.

`stop()` проверяет сохранённый InvocationID перед остановкой только своей службы,
после чего требует пустоты всей группы. Другие процессы и поиск по имени binary
не используются для остановки. Смена invocation, повреждённый request/binding,
недоступный manager или изменение worker epoch запрещают положительную приёмку.
Отсутствие записанной службы и её сохранённой группы после ранее созданного
binding может подтвердить закрытие, но не успешное выполнение программы.

При исчезновении frontend служба продолжает существовать под user manager,
а её deadline действует самостоятельно. `adopt()` позволяет новому контроллеру
привязать существующий staged launcher после сбоя прежнего до binding; такой
adopt **не создаёт ACK и не запускает модель**. Действующий прежний контроллер
не вытесняется. Если записанного связывания/живого staged launcher недостаточно,
API выдаёт ошибку; отсутствие данных не достраивается в доказательство закрытия.

## Что этим не завершено

Это lifecycle/containment primitive, а не полный scheduler или заменённый
production runner. Он ещё не связывает user service с одним атомарным
JobSpec/ConditionSpec/lease journal и не разрешает чужому процессу освободить
abandoned reservation. Старые leases без containment автоматически не
освобождаются. Остаются crash windows при записи/связи journal, cancel всей
цепочки Train→Test, loaded-library provenance, executable/model capability
preflight, worker policy и вся fault/publication matrix. Бюджет диска и slots
ведёт отдельный reservation API; MemoryMax/TasksMax здесь реально применяет ОС.

Cgroup охватывает локальные процессы этой службы и их потомков; внешние
сервисы/удалённые операции нуждаются в отдельной явной декларации. Методы
Rdk, их scheduler и физическая динамика нейрона этим API не меняются.

## Адресная приёмка

Source `0e19681db6cdacd03c223c3fa5210e627b47da3e`:12/12 tests на Elder и
M40, failures/errors/skips0. Использовались реальные system binaries,
пользовательские службы и kernel cgroups; нейронные модели не запускались.
Проверены `.rs1/.rs2/.e05b`, пути с пробелами, stdout/stderr/nonzero exit,
потомок с новой session, выход родителя при живом потомке, потеря frontend,
adopt после сбоя до binding, самостоятельный timeout, отказ изменённого
invocation/request/output и сохранность постороннего процесса.

На worker сохранены135 archive members,421 hashes исходников,11 уникальных
служб,11 terminal membership receipts и10 kernel-limit readbacks. Один
staged-crash case остановлен до нормального readback/ACK; invalid requests
не создали службы. Все11 групп закрыты; ни одному не присвоен научный PASS.
[Независимая проверка](ContainedProcessVerification.json) сверяет primary
hashes, Git sources, подписи request/binding, actual limits и final membership.
Proofs: `596301043967d832a00b23052e1d7679a8dec101` и
`ec9315c60d99f11485be6af41a7d680847e78837`. Отсутствие утечек и весь этап10
этими проверками не принимаются.
