# Elder: освобождение места без удаления данных экспериментов

Удалены две неиспользуемые отдельные code-cache копии под
`/home/user/timelearner-refactor`:

- `source-single-maximum-console-root-a1`, commit038a6641;
- `source-single-impulse-maximum-a2-root-delivery`, commit62997ad1.

Это частные shallow Git delivery clones, не рабочие linked worktrees. Перед
удалением проверены clean tracked/untracked status, отсутствие stash/alternates,
собственная .git и безопасные абсолютные границы. Все927+924 видимых файлов
сопоставлены с Git blob/mode; каждый blob и оба commits доступны в retained
`source-integrated-acceptance-normal-a1`. Cleanup не зависит от удаления
исторических результатов. Модели, primary, logs и пять runtime не удалялись;
125 runtime file bindings побайтово совпали до/после. Source keeper HEAD038
не изменён этой операцией. Позднейшая размерная сборка обновляет его отдельно.

Доступное место по statvfs:3192844288 →3255242752 bytes, прирост62398464 bytes
(около59.5MiB, filesystem blocks). Это адресная очистка двух кэшей, не решение
общего дефицита диска Elder. Порог следующей проверки не снижался:3GiB disk,
8GiB available memory,6GiB group cap и2GiB disk demand сохранены.

## Две неудачные подготовки не скрыты

Первая размерная попытка `s07-maximum-dimensions-elder-normal-a1` завершилась
на preflight до reserve/source update/build/native. В producer числа были
записаны после assertion и поэтому в первичной неудаче отсутствуют. Последующий
readback дал3193073664 free disk bytes при требовании3221225472; memory была
достаточна. Новая попытка сохраняет actual availability перед проверкой.

Первая cleanup a1 остановилась без удаления: для заведомо pre-reserve failed
dependency по ошибке потребовалась существующая lease. Corrected a2 явно
использует production reservation_optional=True только для этого завершённого
pre-reserve predecessor, проверяет not_created и build_passed=false.
Scope не расширен до произвольных отсутствующих reservations.

Evidence `ad2cc6f7798ae3ef5189a210e211d11741fee853`:
13 main archive members/73220 compressed bytes; оба исходных failed archives
сохраняются отдельно вместе с fresh bound closure/not_created readbacks.
[Независимая Git/archive/hash сверка](ObsoleteSourceCacheCleanupVerification-20261107.json).
Lease очистки освобождена после whole-cgroup closure. Научных расчётов и
scientific verdict в этом maintenance gate нет.
