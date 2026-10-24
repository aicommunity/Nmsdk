# Campaign status — latest

**Активный план:** [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../plans/PLAN_2026-10-25_dendrite_limits.md) (+ §H)  
**Ветка:** 2026-10-24T21:45Z (00:45 MSK 25.10)
**Обновлено:** 2026-10-24T19:30Z (22:30 МСК)

Метрика: `sep_margin` + детекция цели; Done_exact / Done_BE раздельно.

---

## 2026-10-24T21:45Z (00:45 MSK 25.10): E05 series E0-E5 at dt = 0.5 ms launched (queue dispatchers on .11 and .17)

Plan: [`../plans/PLAN_2026-10-25_E05_series.md`](../plans/PLAN_2026-10-25_E05_series.md). DefaultTimeStep 2000 in Train/Test, verified in Project.ini and by `now=` increments of 5e-4 in TrainingDynamics.

**E0 (done).** Console vs segsim, one dendrite, subthreshold sig-ref probe: t_peak and FWHM equal segsim for C 7.5e-11/1e-10/2.5e-10 and L 50/200/400; delay/seg = tau - dt (0.25/0.5/2.0 ms). Amplitude Console/segsim 0.72-0.80 at L 50, 0.36-0.40 at L 200-400 (open item, TipR compensates). Delay parameters used as planned. Table: `E05/E0/E0_console_vs_segsim_dt2000.tsv`.

**Code.** PulseLib 29c7ead (class overrides + dynamics-log thinning), a327676 (Branch `InitEstDelayPerSeg`). Consoles `~/e05_bin/NeuroModelerConsole.e05` (first jobs) and `.e05b` (from 00:41 MSK .11; .17 after its build).

**Finding (Branch, tau 0.75 ms).** Branch EstDelayPerSeg is internal (init 0.005 s/seg, EMA). Smoke E2_b (old binary): L stuck at 1/1/9/1 for 300 iterations, d2 peak never valid, est stays 0.005 -> deadlock, not a capacity limit. E4_b_s0 (.17, old binary) ended Done_BE at L 18/17/11/1. Both are diagnostic only; Branch points rerun with InitEstDelayPerSeg = point EstDelayPerSeg.

**Readback OK** (smoke E2_c, E4_c, E5_c): NeuronClassOverrides in EventsLog (Capacity 7.5e-11 / 1e-10, InhRm 1e7, InhRsyn 8.6e7), MaxDL 450/250/500, EstDelayPerSeg 0.00025/0.0005, POST_RESET L 1 1 1 1, TipR 8.6e7 flat.

**Dispatchers** (`tools/e05_dispatch.sh`, own session, survive ssh): .11 `~/e05_runs/series` (8 slots, 6 reserved for REPASS_ITI6), .17 `$DATA/runs/E05_series` (12 slots, 10 reserved). REPASS_ITI6 not touched. Wall time: classic at L ~170 needs ~16 s per 1.5 s iteration -> up to ~4 h per point for train_t 1280 s.

**First results (00:45 MSK).** E1_c_s0 (S100, MaxDL 100): trainer refused after 797 s wall, L 49/47/29/1, d2 TipR saturated at 1e10 (res_no_improve 30), delay_residue 0.0025 -> E1 fails as predicted (amplitude limit), test not run. E4_b_s0 (old binary, diagnostic): Done_BE, L 18/17/11/1, m(S/4) -0.195, m(S/8) -0.527. .17 PulseLib a327676 + e05b built (sha af9f39d9), dispatcher restarted 00:45 MSK with e05b; E4_b_s0n queued first. Both hosts full: .11 6 REPASS + 2 E05, .17 REPASS batch + 2 E05 (reserve 10 until REPASS ends, ~1-1.5 h).


---

## 2026-10-24T20:30Z (23:30 MSK): long-ITI controls done -> no target selectivity in any variant; REPASS sweep launched

**ITI_ctrl (.11 + .17), Test-only, ITI 6 s (12 s for simk2), ref vs target@pos4/reversed:**
| job | sep | fired | note |
|---|---|---|---|
| simk2 d12 ref / tpos4 | -0.0004 / -0.0003 | all 8 | all = 0.0434, zero within-trial effect |
| ctrl_br25 d6 ref / tpos4 | -0.0002 / -0.0003 | target + samples1-3 | samples 4-7 at 0.098-0.0999 below thr; position-independent |
| W0 d6 reversed (.17) | -0.0003 | target + samples1-3 | same sample-dependent pattern |
| C1 w1.5 d6 ref / tpos4 | +0.0008 / -0.0068 | none | 0.040-0.042 |
| C1 w1.5 d6 nsoff | -0.0009 | all 8 | 0.0477: nextseg lowers all trials ~12%, uniformly |
| C1 w0.75 d6 | +0.0003 | all 8 | |
| psi2.5 d6 ref / tpos4 | +0.0111 / -0.0024 | none | target 0.0341@pos0 vs 0.0336@pos4: residual first-trial bias ~1.5% even at 6 s |
| combo psi2.5+nextseg d6 ref / tpos4 | +0.0112 / -0.0029 | none | |
| combo d6 nsoff | md5 == psi2.5 d6 ref (03efc964) | | nextseg adds NOTHING once trials do not overlap |

**Conclusions.** (1) With non-overlapping trials no tested structure (Branch nextseg S25, sim k1/k2, C1 nextseg dose, pre-inh psi, combo) separates the target from foils; all residual differences are sample-identity-driven (target ~= samples 1-3, samples 4-7 slightly lower) and <=2.5% of LTZ max. (2) Q1: nothing to transfer to S50/S100 - S25 success was ITI carry-over. (3) Q2: pre-inh acts within trial but by sample features, not by target; nextseg acts only across trials in combo. (4) Even ITI 6 s leaves a ~1.5% first-trial bias for psi2.5 -> keep permutation controls mandatory, not only long ITI.

**Launched:** REPASS_ITI6 sweep - every historical trained Test dir (latest per case) re-tested at ITI 6 s, ref + target@pos4: .11 `REPASS_ITI6_e11_20261024T2011Z` (53 cases/106 jobs, 6 parallel), .17 `REPASS_ITI6_e17_20261024T2012Z` (43 cases/86 jobs, 10 parallel). Large models (W01_CL50, CL480, BR480) run >13 min per batch. Tool: /tmp/repass_sweep.sh (copy to be committed after first full pass).

**Next (pending REPASS):** if no historical case shows position-independent target selectivity, the one-channel campaign result is negative for the current target/foil set; next step is the input-level analysis why target ~= samples 1-3 (requirements for the pattern / synthetic dataset design, to be approved by Tim before generation).

---

## 2026-10-24T19:25Z (22:25 MSK): order controls + long ITI -> nextseg "detection" is inter-trial carry-over

**W1 (Branch sim k2) jitter replicas:** simk2 j0/jp01/jm01 bit-identical (results md5 ab162e0a, Model f4b489c1ed57) -> post-reset TipR jitter is erased by training; NOT independent seeds. simk1 == ctrl_br25 (f82febbc, sep 0.0111).

**W1_order_ctrl_20261024T1910Z (.11, Test-only on trained structures):**
| job | sep | note |
|---|---|---|
| simk2_ref | +0.2389 | ltz decays with trial index 0.0434 -> 0.017 |
| simk2_tpos4 | -1.2725 (excl0 -0.7075) | foil at pos0 = 0.0434 fires, target@4 = 0.0191 |
| simk2_tlast | -1.2726 (excl0 -0.7430) | positional |
| simk2_nsoff / nsoff_tpos4 | -0.0002 / -0.0004 | all 8 = 0.0434, all fire |
| ctrlbr25_tpos4 / tlast | -0.0184 / -0.0199 (excl0 -0.0083) | none fire, ~0.096-0.100 |
Verdict: W1 has no real selectivity; effect is positional/cumulative.

**C2order_20261024T1857Z (.17), done:** preinh k0 all 0.0477 fire (sep -0.0009/tpos4 -0.0006); k3.0 ~0.0478 all fire (0.0003/-0.0019); k2.5 none fire, 0.031-0.034, sample-dependent, target 0.0341 ~ samples1-3 (sep 0.0111 / tpos4 -0.0024); combo psi2.5+nextseg ref sep 0.2293, tpos4 -0.2192 (excl0 -0.0084) -> artifact. Non-monotonic k2.5 vs k3.0 noted.

**Lazy-wiring hypothesis REFUTED:** nextseg inh synapse is wired in Test (wire_now true; trace of W0 ref vs nsoff differs inside trial 0 from 50 ms). It acts mainly after the peak, producing a long hyperpolarizing tail (-0.039 at 0.5 s, -0.003 at 1.5 s) that carries into the next trial at ITI 1.5 s (trial starts at -0.0027 -> peaks ~0.098). The "detection" = trial-0 advantage from carry-over.

**W0_longITI_20261024T1925Z (.17, Delay 1.5 -> 6.0 s, verified in model: trial1 starts 6.027 s, all trial starts 0.0000):**
| job | fired (by trial) | ltz |
|---|---|---|
| d6.0_ref | 11110000 | target 0.1003 = samples1-3 0.1003; samples4-7 0.0995/0.0999/0.0979/0.0988 |
| d6.0_tpos4 | 00001111 (samples 4-7 first) | position-independent: samples 4-7 suppressed, 0-3 fire |
| d6.0_nsoff | 11111111 | all 0.1003-0.1004 |
Verdict: without carry-over nextseg gives a small within-trial, sample-dependent (not target-specific) suppression (<=2.4%) of samples 4-7; target not separated from samples 1-3. Threshold margin ~0.0001 -> fragile.

**ITI_ctrl_e11_20261024T1922Z / ITI_ctrl_e17_20261024T1924Z (partial at 19:27Z):** simk2 Delay 12: all trials 0.0434 and fire (no within-trial effect at all). C1 nextseg w1.5 Delay 6: 0.0419/0.0415/0.0416, none fire. combo Delay 6: 0.0271/0.0267/0.0268; psi2.5 Delay 6: 0.0341/0.0336/0.0337 (same as at 1.5 s -> preinh effect is within-trial, sample-dependent, not target-selective).

Queued: ITI_ctrl2_e11_20261024T1930Z (ctrlbr25 d6 ref/tpos4, c1w15 d6 nsoff, c1w075 d6 ref), ITI_ctrl2_e17_20261024T1930Z (W0 d6 reversed order, psi2.5 d6 tpos4, combo d6 nsoff). Tool: tools/run_iti.py.

**Q1 implication:** S25 "success" of Branch nextseg is an ITI carry-over artifact; there is nothing to transfer to S50/S100 until a within-trial target-selective mechanism exists. **Q2:** pre-inh (k2.5) and post-seg (nextseg) inhibition both act, but are sample-dependent and not aligned with the target.

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

## 2026-10-24T22:10Z (01:10 MSK 25.10): hourly check, E05 series in progress

- E1_c_s0 (.11, S100 class TauH0, C 2.5e-10, MaxDL 100): ended with C++ training refusal (TimeLearnerTrainingAudit phase 4 reason 1) at L 49/47/29/1, d2 TipR saturated at 1e10, no_imp 30. No test metrics. Consistent with expected FAIL (delay budget does not fit S100 at tau 2 ms), but the FAIL is a training refusal, not a measured m(S/4).
- E1_b_s0 (old binary) stopped after 1.5 min without exit code; Branch points rerun as *_s0n with InitEstDelayPerSeg.
- E4_b_s0 (.17, old binary, diagnostic only): Done_BE at L 18/17/11/1, m(S/4) -0.195, m8_iti6 -0.527: no detection (est deadlock, see above).
- Utilisation fix: .11 dispatcher reserved 6 slots for REPASS_ITI6 while it ran only 2 Consoles (3 cores idle). Restarted with RESERVE_N=2: E3off_b_s0, E4off_c_s0, E4off_b_s0 started; .11 8/8 busy. .17 12/12 busy (10 REPASS + E4_c, E5_c).
- Disk: .11 / 69 % used; .17 / 46 %, /media/user/Data 89 % used (413 GB free, above the 5 % threshold).
