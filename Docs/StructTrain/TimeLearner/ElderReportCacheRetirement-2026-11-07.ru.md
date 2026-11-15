# Освобождение повторно развёрнутых Reports на Elder

При проверке места свободный объём на Elder оказался меньше0.8GB. В рамках
разрешённой пользователем очистки подтверждённых дублей убраны **только рабочие
копии tracked Reports** двух неиспользуемых worktrees:

| Worktree под `/home/user/timelearner-refactor` | Сохранённый HEAD | Файлы | Payload bytes |
|---|---|---:|---:|
| `source-boundary-audit-a1` | `c174c98b237cd241fbae1d46850d7cbdc0d0c100` | 52298 | 391706565 |
| `source-owner-audit-a1` | `664ced2346171cd6b50f3f79af217dde83dde86f` | 52967 | 395857398 |

Удаление Git objects, refs, исходников, runtime либо уникальных результатов
не выполнялось. Применён per-worktree sparse checkout `/*`, `!/Reports/`;
HEAD и полный `git status` сохранились. Это освобождение повторной
материализации, не удаление данных из Git и не новая очистка истории.

До изменения проверены все105265 файлов: содержимое совпадает с index blob,
а каждый из26779 уникальных blob payloads отдельно прочитан из **уже локальной**
общей Git-базы и проверен по SHA1/SHA256/размеру. Это не предположение, что
недостающий объект потом удастся скачать. Git-база и worktree HEADs оставлены
на Elder; сетевой fetch для этой проверки не требовался.

Проверены отсутствие held leases и активных model/build/worker процессов.
Защищённые системные login helpers `sd-pam`, `ssh-agent`, `sshd` проверены
отдельно по kernel process name. Первые два preflight остановились на запрете
чтения их `/proc/exe` до любых изменений; producers и объяснение сохранены.

После удаления materializations свободное место выросло примерно на1.03GiB.
Terminal snapshot до упаковки receipt:734134272→1835991040 bytes; упаковка,
инвентарный JSON и Git-публикация занимают дополнительное место. Это не
гарантия достаточности диска для всей следующей build/experiment matrix.

Git evidence: `3089407e7ff43c3a31333a256252e40c456ea058`, раздел
`Reports/StructTrain/TimeLearner/s02-elder-tracked-report-cache-cleanup-a3`.
В архиве7 members, включая полный inventory;4461772 compressed bytes,
SHA256 `c4d56e9010a0d8a0501e4ca678b9fc3b1a0328e52d7729dc5bd382e9d0026752`.
Архив, все member hashes и105265 inventory records повторно сверены локально.

Для повторного анализа извлекайте нужные файлы из сохранённого HEAD через
Git в отдельный data cache. Для полного восстановления прежней materialization
можно вернуть сохранённые sparse patterns из receipt; для этих двух worktrees
исходно sparse checkout не был включён. Общую Git-базу
`/home/user/timelearner-refactor/source/.git` и указанные HEADs не удалять как
«лишний кэш»: именно их payloads были проверены как путь восстановления.
