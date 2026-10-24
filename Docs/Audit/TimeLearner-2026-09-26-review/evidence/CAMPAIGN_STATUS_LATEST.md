# Campaign status — latest

**Активный план:** [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../plans/PLAN_2026-10-25_dendrite_limits.md) (+ §H)  
**Ветка:** `plan/2026-10-25-dendrite-limits`  
**Обновлено:** 2026-10-24T18:15Z

Метрика: `sep_margin` + детекция цели; Done_exact / Done_BE раздельно.

---

## Диск `/media/user/Data` (Tim 18:11)

- Порог free для archive/offload: **5%** (было 15%).
- Сейчас ~**11% free** → journal-archive **разблокирован**.
- Архивация **только** журналов NMSDK (`archive_nmsdk_journals.sh`); модели/csv/конфиги не трогаем.
- Если free упадёт **&lt;5%** — стоп + запись сюда. Полную зачистку Data по-прежнему эскалируем Тиму при необходимости.

---

## Очередь

| Блок | Статус | Note |
| --- | --- | --- |
| §0 / §H | **done** | threshold 5%; journal archiver |
| W0 SoftCold ×3 (.11) + ctrl (.17) | **running** | |
| W0 R0 replay (.17) | **running/done?** | HIST nextseg |
| C1 Console dose (.17) | **relaunch after Path JSON fix** | LIMIT≤7–8; interpret after W0 PASS |
| genasym (.11) | **running** | |
| Journal archive → Data | **running** | nice/ionice; skip active |

---

## Ядра

| Host | spare | note |
| --- | --- | --- |
| Elder-1 (8) | keep ≥2 | ~5 SoftCold/Test |
| M40 (12) | keep ≥2 | SoftCold ctrl + R0/C1 |
