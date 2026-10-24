# Campaign status — latest

**Активный план:** [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../plans/PLAN_2026-10-25_dendrite_limits.md) (+ §H)  
**Ветка:** `plan/2026-10-25-dendrite-limits`  
**Обновлено:** 2026-10-24T15:10Z

Метрика: `sep_margin` + детекция цели; Done_exact / Done_BE раздельно. Data cleanup — у Тима; **offload не трогаем**.

---

## BLOCK offload (эскалация Тиму)

`/media/user/Data` free ~11% (&lt;15%). Не rsync. Активные Console не kill.

---

## Очередь

| Блок | Статус | Note |
| --- | --- | --- |
| §0 F1–F5 | **done** | pushed |
| §H dual-host / disk / registry | **done** | Data BLOCK |
| W0 SoftCold br25_nextseg ×3 (.11) | **running** | Test-phase на 2 reps; 3-й в очереди launcher |
| W0 SoftCold ctrl (.17) | **running** | Train `-t 320` |
| W0 R0 replay (.17) | **starting** | HIST nextseg IsNeedToTrain=0; не ждёт SoftCold |
| C1 Console dose (.17) | **starting** | LIMIT=8 (12−2 free−1 SoftCold); raw only; interpret after W0 ctrl PASS |
| genasym (.11) | **running** | не стопать |
| C1 interpret / W1 | **pending** | после W0 PASS |

---

## Диск / ядра

| Host | cores | consoles≈ | spare target | home Avail |
| --- | ---: | ---: | --- | --- |
| Elder-1 | 8 | ~5 | keep ≥2 | ~186G |
| M40 | 12 | 1 SoftCold + R0/C1 queue ≤8 | keep ≥2 | ~138G; Data BLOCK |
