# Joint C-search / threshold: подготовка и восстановление ресурсов04.11

Неудачная normal a1 попытка root `9f92a40b97b5868b84b156e38b91903e6b0d8176`
не дошла до configure, build или native model. Цепочка Git alternates была
слишком глубокой; рекурсивные lazy fetch исчерпали TasksMax128. Ошибка относится
к доставке исходников. Научного verdict нет.

Исходный worker1561839/start334038317 и вся его cgroup явно остановлены.
Резерв ресурсов оставался held до адресной проверки API recovery на обоих
серверах. Затем `recover_closed_worker` заново проверил точное соответствие
владельца unit binding, UID/boot и отсутствие всех процессов. Фактически
прочитанный ledger подтвердил released и reserved slots/memory/disk=0.
Ручной SQL и автоматическое освобождение по heartbeat не применялись.

Proof `85a14d10aa96769ce17b34e1c619b04200d5ce8a` содержит31 первичный файл,
включая исходные журналы, request/binding, closure, recovery event и ledger.
[Независимая сверка](JointPreparationRecoveryVerification.json) проверяет
archive/member hashes и точного владельца. Отдельная a2 попытка launcher
остановилась до создания службы из-за ошибочного bootstrap directory;
её журнал также сохранён. Эти ошибки не выдаются за проверки алгоритмов.

## Новая работающая попытка a3

Подтверждены живые worker1667159/start334215550 и supervisor1667124.
Unit `timelearner-54be2b07-74d3-4c3e-95f2-29566e985ba3.service` имеет
фактические лимиты8GiB/128 tasks, один compiler, wall budget21600s.
Оба процесса относятся только к этой попытке. Configure завершился,
SDK действительно компилируется. Итогового native verdict пока нет.

SDK root9f92a40b и Pulse `cc97149c90ce98ff24ca688452f4a40d54e0e63d`
доставлены самостоятельными shallow Git packs без alternates. Они содержат
все текущие code blobs и trees; Docs/Reports в этих двух repositories
намеренно не материализованы. Это SDK code delivery, не замена полноценной
проверки origin-only scientific artifact closure. Остальные шесть gitlinks
клонированы по локальному Git transport с `--depth1`, без alternates.
Все семь HEAD и чистота сверены. GTest и llama.cpp взяты из объявленных
неизменяемых offline sources; их версии/аргументы CMake сохраняются отдельно.

Физический source directory носит прежнее имя
`/home/user/timelearner-refactor/source-csearch-threshold-joint-normal-a2`:
использован уже доставленный снимок, прежний launcher его не изменял.
Build/runtime/readbacks имеют отдельное имя `*-joint-normal-a3`.
Декларированы42 совместных native controls; полный304-case набор этой
попыткой ещё не выполняется. После компиляции требуется проверка primary
данных и читателей. Само начало сборки не является приёмкой joint algorithms.

На M40 первоначальный ASan K1 root69789b8cb/Pulse84e456d продолжает работу
в своём SDK. Его targeted gate сообщил34/34 без failed IDs, теперь идёт262-case
regression. Полная независимая приёмка K1 и119 readers ещё не завершены.
K1 не проверяет новый joint root9f92a40b/Pulsecc97149c.
