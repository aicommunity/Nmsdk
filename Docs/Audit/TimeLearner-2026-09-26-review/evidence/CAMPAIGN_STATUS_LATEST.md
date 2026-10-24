# Campaign status — latest

**Активный план:** [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../plans/PLAN_2026-10-25_dendrite_limits.md) (+ §H)  
**Ветка:** `plan/2026-10-25-dendrite-limits`  
**Обновлено:** 2026-10-24T17:15Z (проверка 20:05 МСК)

Метрика: `sep_margin` + детекция цели; Done_exact / Done_BE раздельно.

---

## Диск Data

`/media/user/Data` ≈ **87% used / 473 G free** — в норме (порог стопа archive &lt;5% free).

---

## W0 TipR-jitter — измерение было пустым (исправление)

Readback на `_work` после SoftCold (seed 1624/1625Z): Train/Test `TipR` = `20000000×3 86000000` = база HIST; стартовый post-reset tip (`83420000…87720000`) **стёрт обучением**. Все 5 `results.csv` md5=`f82febbc` (= baseline SoftCold). `W0_SEED_ROW` verdict/acc=None — sep_margin не считаем.

| Партия | Статус |
| --- | --- |
| `*-1621Z` | **failed_stale** — AttributeError dataclasses/importlib |
| `*-1622Z-rel` | **failed_stale** — нет процессов, логи на poll#2–3 |
| `*-1624/1625Z` post-reset SoftCold | **failed_noop** — TipR jitter erased; identical results |
| **Test-only TipR tip jitter** | **running** — `w0_br25_test_tipr_jitter.sh` на финальном SoftCold Test; sep только если md5≠baseline |

W0 baseline: детекция **PASS**, `sep_margin≈0.011` **FAIL** (порог 0.10) → **W0 PASS не объявляем**.

---

## C1 28/28 rc=0 — не дозовая кривая

| Серия | Факт | Вывод |
| --- | --- | --- |
| segei ×16 | md5=`c4165040` = psi_k0.0; Model d1≡d8 | `set_tag` no-op: тегов SegEI **нет** в gen XML → delta/alpha не записаны |
| nextseg w0…w4 | Model InhR разный (1e15…21.5e6), results md5=`a443fbfb` одинаковый | вес в XML есть, на ответ **не влияет** — механизм не доказан |

Фикс: `ensure_tag_after` для SegEI; readback gate; серия **`mech`** (nextseg w0 vs w4 + segei d1 vs d8) **до** dose. Dose-кривую не интерпретировать до `MECH_PASS`.

---

## Q1: почему C1 nextseg sep≈0.136, а W0 SoftCold ≈0.011

Один и тот же NeuronModel `NSPNeuronGenAsymRmD001C1e9`, TipR end-state `20M 20M 20M 86M`, NextSeg=1.

| | C1 nextseg w1 (inference-only) | W0 SoftCold |
| --- | --- | --- |
| Шаблон | `EXP_br_span25_packA_nextseginh_C1e9` | тот же EXP, cold train |
| L | **13 11 7 1** (HIST pack) | **7 6 4 1** (после SoftCold) |
| TipR | canon | canon (сходится сюда) |
| FixedLTZ (Test) | Model ≈0.0476 | ≈0.100 |
| sep_margin | **0.136** | **0.011** |

Главное отличие — **длина дендрита после SoftCold короче HIST**; плюс другой mid/LTZ. Не «другой нейрон».

Train/Test: [`…/nextseginh_C1e9/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train) · [`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test).

---

## R0

Старый FAIL: gold Train LTZ `0.0115` ≠ Test `0.0476` without overlay.  
Протокол: **FixedLTZ Train→Test** до Console (`r0_branch_nextseg_replay.sh`). Запуск на M40.

---

## genasym `inh_c25_genasym_n0_pton` exit_1 (16:31Z)

Train: лог `Resistance bounds could not be derived: no positive NPulseChannel membrane resistance`; Console **SIGTERM** от parent (~model time 210 s). Test gate: `skip-tipr-mid thr=1 (silent)` — C++ inference mid **не** записал `posttune_complete.flag`. Итог: `done_exit1` — train/gate fail, не PASS. (Журнал evidence заархивирован; workdir Train/Test на месте.)

---

## Очередь сейчас

| Блок | Host | Статус |
| --- | --- | --- |
| W0 Test-only TipR jitter ×5 | Elder | **launch** |
| C1 `--series mech` | M40 | **launch** (до dose) |
| R0 FixedLTZ overlay | M40 | **launch** |
| W1 | — | blocked до R0+W0 margin context + C1 mech |
