# Campaign status — latest

**Активный план:** [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../plans/PLAN_2026-10-25_dendrite_limits.md) (+ §H)  
**Ветка:** `plan/2026-10-25-dendrite-limits`  
**Обновлено:** 2026-10-24T19:00Z (22:00 МСК)

Метрика: `sep_margin` + детекция цели; Done_exact / Done_BE раздельно.

---

## 2026-10-24 ~22:00 МСК (19:00Z) — главное: артефакт первого предъявления

**Порядковый контроль (C1b на .11, W0 на .17) показал: «детекция» цели в Branch nextseg S25 — артефакт порядка теста.** Цель всегда стоит первой (trial 0). Торможение nextseg на trial 0 не действует (ltz как без торможения), с trial 1 подавляет все образцы одинаково, без учёта класса. Перенос цели на позицию 4 или 7 → цель не срабатывает, срабатывает ложный образец на позиции 0.

| Прогон | порядок | цель сраб. | ложн. сраб. | sep |
| --- | --- | --- | --- | --- |
| C1 nextseg w1.0 | цель 0 | да | 0/7 | 0.154 |
| C1 nextseg w1.0 | цель 4 / 7 | нет | 1/7 (поз. 0) | −0.198 / −0.198 |
| C1 w0.75 / 1.25 / 1.5 | цель 0 | да / да / нет | 7 / 0 / 0 | 0.001 / 0.401 / 0.626 (артефакт) |
| C1 load-only R=1e15 | цель 0 | да | 7/7 | −0.0002 (нагрузка кабеля без эффекта) |
| C1 segei d1 a1 | цель 4 | нет | 1/7 (поз. 0) | — (все после 0 → 0) |
| W0 (seed4 j+0.01) ref | цель 0 | да | 0/7 | 0.0115 |
| W0 tpos4 / tlast | цель 4 / 7 | нет | 1/7 (поз. 0) | −0.018 / −0.020 |
| W0 nextseg off | цель 0 | да | 7/7 | −0.0005 (все 0.1003–0.1004) |

Без торможения обученные структуры C1 и W0 дают **одинаковый** отклик на все 8 образцов → селективности структуры нет; вся «разделимость» — межпредъявленческий перенос состояния торможения. Гипотеза кода (не проверена): синапс nextseg подключается лениво (`RelinkNextSegInhToDataset(..., wire_now)`) в ходе первого предъявления.

**Q1sim (Test-only, .17, `Q1sim_20261024T1831Z`)**: Sim1 = бит-в-бит C1 (md5 172c65a7) ✓. gen k2/k4: все 8 = 0.0476. ns w1: k2 sep 0.307, k4 0.164 (foils падают по trial — накопление торможения при длинных TC и нескалированном периоде 1.5 с), naive k2 0.208/naive k4 цель не срабатывает. Всё на порядке «цель первая» → sep артефактный.

**Запущено:** W1 (.11) `W1_sim_k2_20261024T1830Z` 6 обучений (sim k2 ×3, naive br50, ctrl br25, sim k1); W2 (.17) `W2_sim_k4_20261024T1831Z` 4 обучения (sim k4 ×3, naive br100); C2 (.17) `C2order_20261024T1857Z` 8 Test-only (preinh 0/2.5/3.0 ± tpos4, combo preinh2.5+nextseg ± tpos4). Внимание: post-reset jitter TipR, по данным W0, стирается обучением → реплики jp01/jm01 вероятно идентичны j0 (проверка детерминизма, не независимые сиды).

**Следствие для плана:** критерий детекции/sep_margin обязан проверяться с перестановкой порядка (цель не на позиции 0) или с прогревочным предъявлением. Все прежние PASS/«успехи» с целью на trial 0 требуют перепроверки.

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
