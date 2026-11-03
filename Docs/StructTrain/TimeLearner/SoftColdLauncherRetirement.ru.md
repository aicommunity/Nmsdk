# Удаление исторических SoftCold/OpenGaps/T2/T4 launchers

Подэтап9/12 удаляет11 shell entrypoints из текущего Bin без wrappers и копий.
Конфиги, сохранённые модели, первичные измерения и исходные критерии результатов
не меняются. Историческая серия D и прежние очереди не возобновляются.

Retrieval snapshot Bin `39d811e5e0798eecf124f32356c9fc6edbe4538a`.
[Машинный реестр](script_migration.json) содержит105 записей:103 retired и2 moved,
включая полные archive/last-change SHA, blob SHA1, SHA256, size, source URL и git show.
Снимок определяет содержимое инструмента, а не комбинацию кода старого прогона.

| Файл | Причина удаления |
|---|---|
| `Configs/SpikeSamples/StructTrain/scripts/open_gaps_remain6_waiter.sh` | Historical OpenGaps six-case waiter; pattern-based process intervention and fixed old RCS/queue paths. |
| `Configs/SpikeSamples/StructTrain/scripts/open_gaps_w0_diag.sh` | Historical OpenGaps W0 subset; old posttune_verify, shared logs, RCS and case manifest. |
| `Configs/SpikeSamples/StructTrain/scripts/run_canon_soft.sh` | Historical Branch/FastSpan two-repeat cold harness and implicit old registry commits. |
| `Configs/SpikeSamples/StructTrain/scripts/run_invest_ab.sh` | Historical fixed A1/A2/B1/B2 investigation harness and shared status files/commits. |
| `Configs/SpikeSamples/StructTrain/scripts/softcold_c_batch.sh` | Historical C1/C2 fixed case list using old posttune_verify and shared runtime. |
| `Configs/SpikeSamples/StructTrain/scripts/softcold_full49_status_snapshot.sh` | Historical full49 status from old RCS/log/process names; rc0 is not modern scientific PASS. |
| `Configs/SpikeSamples/StructTrain/scripts/softcold_full_matrix.sh` | Historical serial full49 queue and legacy registry updates; shared workspace/runtime. |
| `Configs/SpikeSamples/StructTrain/scripts/softcold_full_matrix_parallel.sh` | Historical full49 xargs queue/shared RCS; labels rc0 as PASS, not a training certificate. |
| `Configs/SpikeSamples/StructTrain/scripts/softcold_w4_status_snapshot.sh` | Historical W4 full49 status tied to old logs/RCS and process names. |
| `Configs/SpikeSamples/StructTrain/_repro/runs/T2_control_batch.sh` | Historical T2 three-case Branch/Asym control batch; old shared Console and posttune harness. |
| `Configs/SpikeSamples/StructTrain/_repro/runs/T4_cold_matrix.sh` | Historical September D4/T4 fixed six-case matrix; old shared runtime and historical audit outputs. |

Все11 исходников прочитаны. Буквальный tracked scan accepted root49946c54,
Bin39d811e5 и Pulse027070e8 обнаружил executable callers только внутри удаляемой
цепочки. Root consumers включали две копии текущих skill/reference инструкций;
они согласованы с root production CLI, status axes, native lifecycle, Git-only
синхронизацией и compact report policy. Семантика прежних registry сохранена
как историческая. Девять root audit документов и два Bin отчёта получают
историческую оговорку; Markdown links к удалённым launchers ведут в immutable Git.
Inventory JSON и старые evidence snapshots не переписываются.

Такой source scan не исключает произвольно вычисляемые имена во внешнем коде.
Оставшиеся generic legacy runners/analyzers и полная migration ещё требуют review.
Современный pipeline не объявляется эквивалентом старых mutable shell waves.

## Приёмка

До merge необходим production `history verify-migration` на обоих workers с
точным root SHA и явными repository handles. Положительный gate проверяет все105
records и отсутствие старых путей. Отрицательный Git-tree fixture восстанавливает
один из11 удалённых launcher blobs и должен быть отклонён без исполнения script.
Численные прогоны для этих удалений не нужны; активные experiments не изменяются.
Проверка сохранности Git payload допускает только11 удалений,2 оговорки отчётов
и новый retirement note в Bin. Runtime/native acceptance не следует из history gate.


## Проверено на обоих workers,03.11

Проверенный root `a197dd87c999679ef80973f71af3de8576102be0`, Bin feature
`66eca4f17bdcf02896513e6e863224ca160a949c`:

| Worker | Evidence commit | Archive members / compressed bytes |
|---|---|---|
| Elder | `7661cb40c5af6ce07554d756d0e7a52b2ba9e624` |10 /39710|
| M40 | `39bf8189e3add38d6dce964fcde265d430319d65` |10 /39715|

Все105 records прошли production CLI. На каждом worker восстановленный launcher
в дочернем Git tree отклонён с migration_old_path_still_present/exit2; положительный
receipt для него не создан. Ни один исторический script не исполнялся и не
восстанавливался в filesystem. Outer/member checksums и380 source hashes каждого
пакета независимо сверены;105 source records отдельно сопоставлены с Git blobs.
Root17/child14 changed paths проверены, прочие tree blobs сохранены.

Bin принят merge commit `4af17aa240a7da0e30655a62c07cc4832e7253b9`, remote develop
проверен; его tree `effdda23838749bd2bad1e077b4bdf32e6be4f78` равен tested feature.
Корень фиксирует точный merge gitlink. Это завершённый адресный пакет миграции;
полные этапы9/12, перенос остальных analyzers и production queue остаются открытыми.
