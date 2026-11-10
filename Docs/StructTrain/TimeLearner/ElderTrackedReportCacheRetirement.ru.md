# Освобождение tracked Reports caches старых SDK Elder

Операция относится только к18 объявленным старым агентским SDK в
`/home/user/timelearner-refactor/source-*`. Пользовательские
`/home/user/Nmsdk` и `/home/user/tl-agent/Nmsdk`, исходники, сборки, runtime,
Git objects/refs и stash не удаляются. Каждый untracked report сохраняется.

В этих рабочих копиях обнаружены65–80 тысяч tracked Reports files на SDK.
Удаление распакованного файла допускается только при совпадении его Git blob
hash с индексом/HEAD, наличии соответствующего blob в object store и
повторной проверке размера, inode, mtime, типа и SHA256 перед unlink.
Файлы не считаются бесполезными научными данными: убирается лишь их
дублирующая materialization, а канонические Git bytes остаются доступны.

[Точный producer как неисполняемый provenance text](ValidationPlans/ElderReportCacheRetirement-20261110/producer.py.txt)
зафиксирован до соответствующего прохода. Новые active launchers в Docs/Bin
не создаются. Используется штатный `Reservations.open_existing`, write leases
на выбранные SDK/common Git dirs и отдельный output. Held lease не игнорируется
по истечении TTL. Старые SDK проверяются по cwd/exe/fd пользовательских
процессов; PAM/SSH/ssh-agent исключены явно и записываются как непроверенные
служебные helper paths, а не как доказательство полного proc audit.

## Попытки

- A1 остановлен на защищённом ssh-agent до первого удаления:0 files.
- A2 остановлен собственным SIGINT до первого удаления:0 files. Причина —
  перевод накопительного million-file inventory на поочерёдное хранение.
  Owner PID/start_ticks проверены; finally освободил lease.
- A3, producer commit `bf5715d525321469f74719a9d38f755d5ab7ec8b`, выполняется
  в `readbacks/s02-elder-tracked-report-cache-retirement-a3`. Все18 inventories
  проверены перед первым unlink; каждый сохраняется отдельно в gzip.
  Память резервируется512MiB, self-HWM guard400MiB, не более100000 files на
  один SDK. Наблюдавшийся self-HWM около127MiB не является финальным peak.

На момент этой записи финальный terminal A3 и его компактная Git-публикация
ещё отсутствуют. Объём фактически освобождённого диска и полная приёмка
очистки будут определяться terminal, removed.jsonl и независимой сверкой
инвентарей. Эта запись не объявляет18 SDK полностью очищенными.

## Восстановление и ограничения

Для каждого SDK сохраняются exact HEAD, stash listing, backup index и список
удалённых файлов с Git blob/SHA256/identity. В индексе только эти пути помечаются
`skip-worktree`, поэтому очистка кэша не создаёт массовое staged deletion.
Чтобы вернуть старый Reports materialization, сначала проверить записанный
HEAD, затем снять skip-worktree для NUL-delimited списка удалённых путей и
восстановить те же пути через `git restore --source=<recorded HEAD> --worktree`.
Для длинных списков использовать `--pathspec-from-file`/`--pathspec-file-nul`.
Не подменять целиком текущий индекс старым backup, если позже появились
собственные изменения. Git objects этих старых HEAD сохраняются; их удаление
или GC с потерей последней копии первичных данных этой операцией не разрешены.

Новая SDK355/Pulse165/Rdkde уже доставлена в отдельный
`source-native-archive-move-normal-a1`; resources Bin8cb также доставлены
отдельно. Normal Release/LLM Off/18-case декларация для Elder хранится в
корневом commit `12743f3ded0cedab43dd63d6e3e4614d2eb2c994` по пути
`Docs/StructTrain/TimeLearner/ValidationPlans/ElderNativeArchiveMove18-20261110`.
Это тот же source slice, но другой build profile относительно M40 ASan;
побитовая эквивалентность двух сборок не заявляется. Новая сборка Elder до
завершения очистки, освобождения lease и capacity preflight не запускается.
