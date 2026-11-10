# Освобождение tracked Reports caches старых SDK Elder

Операция A3 завершена:1258684 files,12043062096 logical bytes.
Свободное место2420293632→17256710144 bytes (около16.1GiB после операции),
self peak RSS195657728 bytes. Owner отсутствует, fresh snapshot не содержит
held leases. [Шесть точных metadata files](ValidationPlans/ElderReportCacheRetirement-20261110/terminal-readback.json)
сохранены lossless/base64 с SHA256; полные file inventories и index backups
пока остаются в серверном кэше и требуют отдельной compact capture/проверки.
Это завершение удаления проверенных копий, а не приёмка всего этапа2.

Выявлен недостаток этого разового producer: disk demand128MiB не учитывал
полный removed.jsonl и резервные индексы; фактический каталог аудита превысил
demand. Свободное место росло, но соблюдение output budget этим не доказано.
Исходные demands/журналы сохраняются без исправления задним числом. Перед
повторным применением подобного инструмента требуется потоковый сжатый log
и расчёт всех временных выходов. Source A3 по Git-ссылке является историческим,
не рекомендуемым активным launcher.

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

[Точный producer в Git history](https://github.com/aicommunity/Nmsdk/blob/bf5715d525321469f74719a9d38f755d5ab7ec8b/Docs/StructTrain/TimeLearner/ValidationPlans/ElderReportCacheRetirement-20261110/producer.py.txt)
зафиксирован до прохода и удалён из текущего Docs tree после завершения.
Запись добавлена в script_migration.json:357 current records против356 ранее
runtime-проверенных; новая полная production-проверка остаётся открытой.
Wrappers/копии запускателя не оставлены. Использован штатный `Reservations.open_existing`, write leases
на выбранные SDK/common Git dirs и отдельный output. Held lease не игнорируется
по истечении TTL. Старые SDK проверяются по cwd/exe/fd пользовательских
процессов; PAM/SSH/ssh-agent исключены явно и записываются как непроверенные
служебные helper paths, а не как доказательство полного proc audit.

## Попытки

- A1 остановлен на защищённом ssh-agent до первого удаления:0 files.
- A2 остановлен собственным SIGINT до первого удаления:0 files. Причина —
  перевод накопительного million-file inventory на поочерёдное хранение.
  Owner PID/start_ticks проверены; finally освободил lease.
- A3, producer commit `bf5715d525321469f74719a9d38f755d5ab7ec8b`, завершён
  в `readbacks/s02-elder-tracked-report-cache-retirement-a3`. Все18 inventories
  проверены перед первым unlink; каждый сохраняется отдельно в gzip.
  Память резервируется512MiB, self-HWM guard400MiB, не более100000 files на
  один SDK. Финальный self-HWM указан выше; ранние127MiB были промежуточным наблюдением.

Terminal и компактные metadata опубликованы; полный removed.jsonl и независимая
сверка инвентарей ещё не включены в Git-приёмку. Уникальные untracked reports
не удалялись, поэтому это не удаление всех Reports-каталогов.

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
побитовая эквивалентность двух сборок не заявляется. Первая preparation прошла,
но native preflight отклонил несовпадение SDK/helper до запуска компиляции.
Для A2 выбран runner1386206616d82952166ece926e814cd2c5aafbb9; worker побайтно
совпадает с SDK355. После fresh cleanup/capacity проверки и corrected canonical
PASS normal A2 реально запущен: supervisor1687/start388720843, main7419,
unit timelearner-f33b896c-71f9-47e1-b01d-24a0d9a9ff70.service. Новый build/runtime
изолирован от старых копий. Native18 и научный PASS ещё не получены.

[Полный отчёт запуска normal18 и точные A1/A2 observations](https://github.com/aicommunity/Nmsdk/blob/430072b1f02612d5e9fbcc8fd6c8f4d04a25e658/Docs/StructTrain/TimeLearner/ElderArchiveMove18Launch-20261110.ru.md).
