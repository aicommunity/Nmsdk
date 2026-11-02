# Сохранённые nonexact completed-модели: воспроизведение новым кодом

Новый BudgetExhausted для свежего поиска не меняет смысл сохранённых ранее
`timelearner_completed_state` schema1 с `training_outcome=search_unresolved` и
отрицательным сертификатом. Они имеют свой старый протокол и версию алгоритма.
Нельзя пересчитать их исторический training outcome по сегодняшней причине
остановки либо объявить их Exact.

Maintained команда `legacy-completed-replay SPEC --output NEW_DIRECTORY`
использует настоящий `NativeLearnedState/FreshProcessImport` в отдельном owned
процессе на каждый case. Это проверка сохранённого состояния и отклика, без
нового Train, калибровки, изменения параметров или recognition/classification.
Controller checkpoint посреди пробы не восстанавливается: модель проходит
штатный native import/Build/Init/reset и затем полную frozen probe.

Spec `legacy-completed-boundary-replay-v1.json` фиксирует четыре Classic/Branch
× N0/N1 состояния из A14. Original evidence commit:
`0b556b9dde5338625525707eee2ad96956e4c237`. Данные читаются из доступного
согласованного Git snapshot `07167d55125ced4eeff72703a718203e8c90bfc7`.
При создании spec проверено побайтное равенство всех12 gz blobs в этих двух
commits; записаны stored/raw SHA256. Рабочие snapshots/runtime имеют отдельные
версии и не выдаются за исходный код A14.

До первого native запуска проверяются все declarations, stored/raw hashes,
тип completed/nonexact, полнота golden observation и microsecond clock.
Начало воспроизведения берётся из сохранённого observation, с проверкой
представимости в native microseconds. Each gate хранит explicit fixture env,
точный входной package, golden CSV/probe, argv, owned PID identity, runtime,
loaded files, JUnit и фактические данные нового процесса. Ошибка любого case
не становится PASS; остальные независимые cases остаются диагностируемыми.

Положительный результат требует полного declared JUnit без skip, совпадения
семантического model revision и всего сохранённого сертификата, frozen
`IsNeedToTrain=false`, независимого audit фактической complete native probe и
побайтного равенства всего CSV с golden trace. Нет автоматически расширяемого
амплитудного или временного допуска. Scientific verdict всегда null.

Elder initial driver `b499bb9224666ff90e999f8d7c82121c7ca2d127`:4/4 passed
на combined C++ root07167d551/Pulse fca7141; данные пока ожидают публикации и
независимых reader tests. ASan-подтверждение ещё ожидается. Это ограниченный
saved-state replay, не проверка всего legacy алгоритма обучения, всех старых
архивов, частот, профилей или нового frozen recognition протокола.

Reader tests требуют `TIMELEARNER_LEGACY_REPLAY_DIR` (каталог result реального
завершённого replay). Они проверяют реальные четыре inputs/outputs/receipts,
а также отказ до создания output при повреждении stored/raw hash, дублировании
case ID, неизвестной/boolean schema и попытке перезаписи существующих данных.

## Подтверждённый подэтап

На обоих workers4/4 native replay и5/5 independent reader tests, без skip.
Normal primary `f6a975f0aab5113f86855a26f170cb0060f21ea6`:88 members,
274,649 bytes. ASan primary `1c7ee355b13323b43594eeef36e6bf37dba355a6`:
88 members,287,604 bytes. После Git fetch локально проверены outer SHA256SUMS,
hash каждого архива и всех members. ASan loaded-file capture содержит libasan.
Первый publication preflight ошибочно ожидал source_closure.root.commit вместо
штатного root.head; failed-closed попытка сохранена в primary. Модели не
перезапускались из-за ошибки упаковки.

Существенное ограничение: штатный FreshProcessImport предъявляет **active
input0**. Проверяется весь его CSV и все записанные soma channels, но не все
входы, target/foil матрица или legacy training dispatcher. Импорт заново
проверяет сохранённый сертификат по всем embedded reference/final packets;
это не новое физическое измерение всех входов. Остальные входы/recognition,
другие архивы/частоты/профили и public diagnostic evaluation остаются в плане.
Августовские4/8–6/8 этими CI случаями не переоцениваются.
