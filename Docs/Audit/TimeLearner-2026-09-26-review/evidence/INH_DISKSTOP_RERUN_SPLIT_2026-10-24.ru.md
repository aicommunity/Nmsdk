> Исторический отчёт. Launchers/monitors удалены из текущего дерева; точные commit/blob и восстановление описаны в [реестре миграции](../../../StructTrain/TimeLearner/ScriptMigration.ru.md). Новую серию эти команды не возобновляют. Прежние измерения и критерии ниже сохранены.

# InhGrid Classic disk_stop re-run — dual-host split (2026-10-24)

Постановка: после SoftCold InhGrid 24 Classic-кейса оборвались гейтом `STOP Avail<80G`. Известное исправление — offload idle lanes/артефактов с Elder-1 на Data `.17`, затем повтор cold без ожидания оператора. Работу делим между хостами, чтобы не держать всю очередь на одном диске.

## Распределение

| Host | Cases | LIMIT | Список |
| --- | --- | --- | --- |
| Elder-1 (локально) | Classic Span25 disk_stop ×8 | ≤8 | `all`, `preinh_nextseg`, `preinh_segei`, `segei` × N0/N1 |
| M40 / `10.245.1.17` | Classic Span50 disk_stop ×16 | ≤12 | все 8 Mod × N0/N1 |

Лаунчер: [`INH_GRID_LAUNCH_CASES.sh` (исторический Git source)](https://github.com/aicommunity/Nmsdk/blob/b62127538694a3442771598420fd78fa7e405c8b/Docs/Audit/TimeLearner-2026-09-26-review/evidence/INH_GRID_LAUNCH_CASES.sh) (ожидание Avail≥85 G перед стартом кейса; `cpu_gate` с timeout 90 s). Offload lanes → `/media/user/Data/TLAgent-offload/elder1-lanes-20261024/`.

## Статус (финал)

- Elder-1: Classic S25×8 **ALL_DONE** (8×`exit_1`).
- M40/`.17`: Classic S50×16 **ALL_DONE** (14×`not_converged`, 2×`exit_1`).
- 5‑мин монитор остановлен после закрытия очереди.
