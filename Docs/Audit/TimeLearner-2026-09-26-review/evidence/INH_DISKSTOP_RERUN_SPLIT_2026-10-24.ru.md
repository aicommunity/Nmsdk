# InhGrid Classic disk_stop re-run — dual-host split (2026-10-24)

Постановка: после SoftCold InhGrid 24 Classic-кейса оборвались гейтом `STOP Avail<80G`. Известное исправление — offload idle lanes/артефактов с Elder-1 на Data `.17`, затем повтор cold без ожидания оператора. Работу делим между хостами, чтобы не держать всю очередь на одном диске.

## Распределение

| Host | Cases | LIMIT | Список |
| --- | --- | --- | --- |
| Elder-1 (локально) | Classic Span25 disk_stop ×8 | ≤8 | `all`, `preinh_nextseg`, `preinh_segei`, `segei` × N0/N1 |
| M40 / `10.245.1.17` | Classic Span50 disk_stop ×16 | ≤12 | все 8 Mod × N0/N1 |

Лаунчер: [`INH_GRID_LAUNCH_CASES.sh`](INH_GRID_LAUNCH_CASES.sh) (ожидание Avail≥85 G перед стартом кейса; `cpu_gate` с timeout 90 s). Offload lanes → `/media/user/Data/TLAgent-offload/elder1-lanes-20261024/`.

## Статус (обновление mid-run)

- Elder-1: Classic S25×8 **ALL_DONE** (лаунчер закрыт; notes в основном `exit_1` после полного verify — не disk_stop).
- `.17`: Classic S50×16 — **12/16 done** (`not_converged`), хвост 4 running: `segei`/`preinh_segei` ×N0/N1. EventsLog периодически trim’ится при Avail&lt;105 G.
- Offload Elder-1 lanes/TLAgent → Data выполнен; Avail Elder-1 ≫80 G.
