# Campaign status — latest

**Активный план:** [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../plans/PLAN_2026-10-25_dendrite_limits.md) (+ §H)  
**Ветка:** `plan/2026-10-25-dendrite-limits`  
**Обновлено:** 2026-10-24T15:20Z

Метрика: `sep_margin` + детекция цели; Done_exact / Done_BE раздельно.

---

## Диск `/media/user/Data` (Tim 18:11)

- Порог free для archive/offload: **5%** (было 15%).
- Сейчас ~**11% free** → journal-archive **идёт**.
- Архивация **только** журналов NMSDK (`archive_nmsdk_journals.sh`); модели/csv/конфиги не трогаем.
- Если free упадёт **&lt;5%** — стоп + запись сюда.
- Elder (.11): нет локального mount Data → `DATA_OFFLOAD_HOST=user@10.245.1.17` (rsync после verify).
- M40 (.17): локально; ~79 GiB журналов в `TLAgent-20261020/runs` (в т.ч. Dynamics multi-GB) — batch 314 dirs, largest-first, `nice`/`ionice`, skip active W0/R0.

**Логи батчей:** Elder `/tmp/jarch_elder_batch.log`; M40 `/tmp/jarch_m40_batch.log`.  
**Архивы:** `/media/user/Data/TLAgent-offload/journals/<host>/20261024/`.  
**Реестр:** `RUN_REGISTRY/runs.tsv` строки `jarch_*`.

---

## Очередь

| Блок | Статус | Note |
| --- | --- | --- |
| §0 / §H | **done** | threshold 5%; journal archiver |
| W0 SoftCold ×3 (.11) + ctrl (.17) | **running** | skip journals |
| W0 R0 replay (.17) | **running** | skip journals |
| C1 Console dose (.17) | **relaunched** | LIMIT=7; Path JSON fix |
| genasym (.11) | **running** | skip journals |
| Journal archive → Data | **running** | Elder ~70 dirs; M40 314 dirs |

---

## Ядра

| Host | spare | note |
| --- | --- | --- |
| Elder-1 (8) | keep ≥2 | ~3 SoftCold/Test + genasym |
| M40 (12) | keep ≥2 | SoftCold ctrl + R0 + C1≤7 |
