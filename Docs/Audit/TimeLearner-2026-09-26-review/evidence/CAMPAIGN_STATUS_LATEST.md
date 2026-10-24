# Campaign status — latest

**Активный план:** [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../plans/PLAN_2026-10-25_dendrite_limits.md) (+ §H dual-host/disk/offload)  
**Ветка:** `plan/2026-10-25-dendrite-limits`  
**Обновлено:** 2026-10-24T18:05Z

Метрика: `sep_margin` + детекция цели; Done_exact / Done_BE раздельно. H0 TauH0 — вне приоритета.

---

## BLOCK: offload на `/media/user/Data`

На M40 `/media/user/Data` сейчас **~89% used / ~11% free** (&lt; порога **15% free** из плана §H3).

**Действие:** перенос в `/media/user/Data/TLAgent-offload/…` **не выполнять**, пока free% ≥ 15. Скрипт `evidence/tools/disk_watch_offload.sh` при `check`/`offload` вернёт `BLOCK_OFFLOAD`. Активные Console **не** убивать.

Нужна ручная очистка Data (или другой том) — затем снять блок в этом файле.

---

## Очередь

| Блок | Статус | Note |
| --- | --- | --- |
| §0 F1–F5 | **done** (pushed) | PulseLib `2e5308e`, Bin `b7706a07` |
| §H dual-host / disk / registry | **in progress** | plan §H; `RUN_REGISTRY/`; `disk_watch_offload.sh` |
| M40 sync + build + br25_nextseg ctrl | **in progress** | stash сохранён на .17; fetch ветки |
| W0 br25_nextseg ×3 (.11) | **running** | параллельно genasym |
| genasym SoftCold (.11) | **running** — не стопать | |
| C1 / W1–W2 | **pending** | после W0 PASS + M40 ctrl |

---

## Диск сейчас

| FS | Host | Avail / free% | Действие |
| --- | --- | --- | --- |
| `/home/user` | Elder-1 | ~186G (~41% free) | OK; warn&lt;80G → offload done (не kill) |
| `/` | M40 | ~138G | OK |
| `/media/user/Data` | M40 | ~407G / **~11% free** | **BLOCK offload** |
