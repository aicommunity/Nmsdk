# Блокировка publisher и явное восстановление после сбоя frontend

Candidate устраняет PID-only ownership у блокировки публикации на Linux.
Общий для связанных worktrees Git common directory содержит постоянный
`timelearner-publication.guard`. Kernel flock удерживается publisher и
передаётся его Git subprocess через pass_fds. Guard inode не удаляется;
живой Git push не должен позволять повторный publisher или recovery после
завершения только Python frontend.

Нормальный `publish` сохраняет children-first, exact Git closure, проверку
всех declared artifact bytes, запрет force и отказ при ошибке child push.
Существующая lock directory автоматически не удаляется.

Явная команда:

```text
python -m Scripts.StructTrain.TimeLearner publish-recover --root REPOSITORY --output NEW_RECEIPT.json
```

Она не делает push. Требует свободный kernel guard, известную строгую запись
owner, совпадение host/boot/guard device+inode и отсутствие прежней идентичности
PID/start_ticks. Старый owner сохраняется атомарным переименованием lock
directory в уникальный recovery directory внутри Git common dir. Неизвестные
файлы, symlink, старый PID-only формат, иной boot/host/inode или живой владелец
означают отказ. Reboot recovery старого boot этим API не разрешён.
На Windows и других платформах без Linux /proc обычная публикация сохраняет
прежний консервативный directory lock; новый recovery там не поддерживается.

Это защита участвующих локальных процессов, наследующих locked descriptor,
а не распределённая транзакция Git-серверов и не универсальное обнаружение
произвольных detached процессов. Remote refs проверяются отдельно после push
и после всей closure. Полный scheduler journal, reboot/recovery matrix,
semantic ConditionSpec binding и production queue остаются открытыми.

Перед приёмкой требуются production publisher tests на обоих серверах:
прежние publication/fault controls, linked-worktree exclusion, отказ recovery
старого lock и реальный receive-hook scenario. В последнем frontend убивается
при живом Git push; recovery/publish обязаны отказать, затем public CLI recovery
сохраняет owner и повторная публикация без force завершает exact closure.
Приёмка пока не выполнена; этап10 остаётся частичным. Модели не запускаются.
