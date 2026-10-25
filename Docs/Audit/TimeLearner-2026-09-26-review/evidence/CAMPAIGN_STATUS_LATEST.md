# Campaign status — latest

**Активный план:** [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../plans/PLAN_2026-10-25_dendrite_limits.md) (+ §H)  
**Ветка:** plan/2026-10-25-dendrite-limits (Nmsdk, Bin, PulseLib)  
**Обновлено:** 2026-10-24T19:30Z (22:30 МСК)

## hourly 2026-10-25 13:05 MSK - A1_r2 досчитана: RminNoImproveMinProgress частично снимает ранний стоп Branch, выделения цели нет

- Нагрузка: .11 7 Console (NSR_E5_c_N1_f1, NSR_E2_c_N0_f1, NSR_E5_c_N0_f1, NSR_E1_c_N1_f1_frz, NSC_E2_c_N0_t1, NSC_E5_c_N0_t1, NSC_E5_c_N0_t0), в очереди 1 (NS_E4_c_N0). .17 3 Console (NSR_E1_b_N0_f0/f1 с 11:26, NSC_E1_b_N0_t0 с 11:34), очередь пуста. Диск: .11 / 103 ГБ свободно, /media/user/Data 390 ГБ (89%), чистка не нужна. Новых заданий не ставилось.
- A1_r2 (.11, e05_job 5c8f251, Console e05c). TRAIN_GATE ok, RminNoImproveMinProgress есть в Train XML, train_valid, Test обучен (test_L = final_L). m8 = (амплитуда цели - макс. foil) / амплитуда цели.
  - A1_E5_b_p05_r2 и A1_E5_b_p025_r2 (S50, теория 200 166 100 1): L 153 137 73 1 (r1 и раньше: 73 57 41 1). m(S/4) +0.075, m(S/8) -0.015, m8 gate05 = iti6 = itiS = gate05_t7 = -0.099; без торможения (off) -0.084.
  - A1_E2_b_p05_r2 и A1_E2_b_p025_r2 (S100, теория 400 334 200 1): L 273 249 137 1 (было 73 57 41 1). m(S/4) -0.048, m(S/8) -0.030, m8 -0.144 во всех контролях паузы; off -0.133.
  - A1_E2c10_b_p05_r2 (C 1e-10, раньше стоп 89 73 57 1): L 161 129 73 1. m(S/4) +0.104, m(S/8) -0.080, m8 -0.113; off -0.109.
  - p05 и p025 побитно совпадают (L, все амплитуды и метрики). Значит, при новом коде рост останавливает уже не порог RminNoImproveMinProgress, а другой критерий. Гипотеза, проверять после рефакторинга.
  - Критически: L выросла до ~0.75 (S50) и ~0.68 (S100) от теоретической, ранний стоп ERR-06 снят частично. Но цель не выделяется: на цели спайков нет ни в одном тесте, в iti6 срабатывает 1 foil, при паузе 6 с, в gate05 и itiS амплитуда цели ниже максимального foil. Положительный m(S/4) есть только в порядке q без паузы и в контролях порядка и паузы не воспроизводится, то есть это эффект порядка, а не выделение. Off-тесты (без торможения) дают ту же картину с меньшими амплитудами.
- Classic на .11 (5c8f251):
  - NS_E2_c_N0: not_converged_at_stop при train_t 1280 с (3.4 ч), final_L 417 337 217 1, Test = шаблон (52 48 27 1), метрик нет.
  - NSR_E2_c_N1_f1 (Resync=1): C++ отказ TimeLearnerTrainingAudit phase=4 reason=1, tip R в rmax 1e10 (rmax_stall=1), final_L 393 337 217 1, Test = шаблон, метрик нет. Перемер отказ Classic E2 не снимает.
  - NSR_E1_c_N1_f2 (Resync=2): тот же отказ phase=4 reason=1, final_L 49 47 29 1, как у f0/f1, метрик нет.
- .17 (WIP 552ce27): NSR_E5_b_N0_f0, NSR_E5_b_N0_f1 и NSC_E5_b_N0_t1 завершились rc=3 INVALID train_stalled: final_L 1 1 97 1 после 400 итераций аудита, то есть в режиме N0 у Branch S50 растёт один дендрит, а два других не начинают рост. Результат одинаков при Resync 0/1 и с подгонкой ёмкости и совпадает с NSC_E1_b_N0_t1 (1 1 11 1). Похоже на общую проблему N0 у Branch, а не на эффект флагов.
- Вывод на 13:05: A1_r2 закрыта. Новый критерий даёт заметно больший L, но выделения цели нет и при L ~0.7 от теоретической. Перемер и подгонка ёмкости пока ни в одном случае не дали выделения; Classic E2/E5 по-прежнему не доучивается (отказ C++ или not_converged), Test остаётся шаблоном. Досчитываются 7 + 1 заданий на .11 и 3 на .17.

## hourly 2026-10-25 12:05 MSK - новые итоги NSR/NSC/NS: выделения цели нет ни в одном случае

- Нагрузка: .11 7 Console (5 A1_r2 в доп. тестах xt, NS_E2_c_N0, NSR_E2_c_N1_f1), в очереди 9 (NSR_E5_c_N1_f1, NSR_E2_c_N0_f1, NSR_E5_c_N0_f1, NSR_E1_c_N1_f1_frz, NSR_E1_c_N1_f2, NSC_E2_c_N0_t1, NSC_E5_c_N0_t1, NSC_E5_c_N0_t0, NS_E4_c_N0). .17 6 Console (NSR_E1_b_N0_f0/f1, NSR_E5_b_N0_f0/f1, NSC_E5_b_N0_t1, NSC_E1_b_N0_t0), очередь .17 пуста с 11:34. Диск: .11 / 107 ГБ свободно, .17 / 97 ГБ, /media/user/Data 390 ГБ (89%), чистка не нужна. Новых заданий не ставилось.
- .17 (e05_job WIP 552ce27, train_gate и test_gate пройдены, Test обучен, кроме отмеченных):
  - NSR_E1_b_N1_f0 (ResyncAfterNormalization=0): L 28 21 14 1, m(S/4) -0.153, m8 gate05 = iti6 = -0.238, цель не выделена.
  - NSR_E1_b_N1_f1_r2 (Resync=1) побитно равен f0 (m8 -0.2377, L 28 21 14 1): перемер после нормализации на E1_b ничего не меняет.
  - NSR_E1_b_N1_f2 (Resync=2): L 23 20 13 1, m(S/4) -0.185, m8 -0.339, done_be 0, хуже f0.
  - NSR_E2_b_N1_f1 и NSR_E5_b_N1_f1: L 73 57 41 1 у обоих (ранний стоп Branch, ERR-06; для E5 ожидалось 200 166 100 1), m8 -0.3416 / -0.3413, совпадает с прежним E2_b gate05 -0.3416. Перемер не влияет, предел задаёт стоп роста.
  - NSC_E1_b_N0_t1 (SyncCapacitanceTrim=1 + Resync=1): Train не сошёлся к стопу (train_t 1280 с), final_L 1 1 11 1, то есть рост двух дендритов не начался; Test = шаблон (22 18 11 1, C 1e-9 против 2.5e-10 в Train), метрик нет. Подгонка ёмкости при N0 срывает рост, разбирать после рефакторинга.
  - NSR_E1_b_N1_f1_frz: INVALID, rc=3, флага FreezeTipResistanceAfterFirstSync нет в Train XML (консоль rs1 его не знает). Ошибка конфигурации задания, гейт сработал правильно.
- .11 (e05_job 5c8f251):
  - NS_E5_c_N1 (11:39): как и NS_E5_c_N0, not_converged_at_stop при train_t 640 с (около 2.5 ч), L 209 185 105 1 в обоих режимах, Test = шаблон, метрик нет. У N1 tip R двух дендритов упёрлись в rmax 1e10 (у N0 все 8.6e7). Сравнение N0/N1 для Classic E5 не состоялось.
- Вывод на 12:05: ни перемер (Resync 1/2), ни подгонка ёмкости не дали выделения цели. На Branch E2/E5 результат определяется ранним стопом роста (ERR-06), Classic E5 не доучивается за отведённое время. Ждём A1_r2 (снимает ли RminNoImproveMinProgress стоп) и NSR/NSC Classic на .11 (оценка до 15:00-16:00 MSK и позже).
## 11:22 MSK: D остановлена по решению Тима до рефакторинга

- Решение Тима 25.10 11:22 MSK: сетка торможения D (InhGrid S50/S100, 32 задания D_c50_*/D_c100_* в очередях E05 .11/.17) остановлена до большого рефакторинга. Не чинить и не перезапускать. Досчитываются только A1_*_r2 (Branch, RminNoImproveMinProgress) и NSR_*/NSC_* (normsync). Новых заданий не добавлялось.
- **D итог (32): завершено 15, прервано 13, снято из очереди 4.**
  - Завершены (rc=0): .17 12 (D_c100: gen_n1, preinh_n1, segei_n1, nextseg_n0/n1, preinh_nextseg_n0/n1, preinh_segei_n1, nextseg_segei_n1, all_n0, all_n1 (досчитался сам в 11:24); D_c50_gen_n1); .11 3 (D_c50: preinh_nextseg_n1, preinh_segei_n1, nextseg_segei_n1).
  - Прерваны 11:24-11:25 MSK (SIGTERM группе процессов задания; SIGKILL не понадобился): .11 5 (D_c50: all_n0, all_n1, nextseg_segei_n0, preinh_nextseg_n0, preinh_segei_n0); .17 8 (D_c100: gen_n0, preinh_n0, segei_n0, preinh_segei_n0, nextseg_segei_n0; D_c50: gen_n0, preinh_n0, preinh_n1). В диспетчере они отмечены rc=NA. Каталоги сохранены, в каждом файл STOPPED_BY_DECISION_2026-10-25. Результаты неполные, в сводках не использовать.
  - Сняты из очереди (.17): D_c50_nextseg_n0/n1, D_c50_segei_n0/n1. Строки в queue.tsv закомментированы префиксом `# STOPPED_BY_DECISION_2026-10-25`, бэкап queue.tsv.bak_decision_1122.
- Смоук-проверки прерванного разбора D (.17 runs/E05_smoke_flags, RT_segei_n1 / RT_nextseg_n1) закончились сами до остановки, дальше не ведутся.
- Незавершённая правка e05_job.py из разбора D (аудит-гейты Train/Test, синхронизация флагов learner в Test Model) закоммичена как WIP без проверки: 552ce27. На .17 рабочий файл изменён в 11:20 MSK, поэтому NSR/NSC на .17, стартовавшие после этого, идут уже с этими гейтами. На .11 задания идут на 5c8f251, рабочую копию .11 не обновляли, пока очередь не закончится.
- .11: NS_E2_c_N0 и NS_E5_c_N1 (normsync N0, не D) досчитываются. NS_E4_c_N0 не входит в список разрешённых заданий и снят с очереди как `# HOLD_BY_DECISION_2026-10-25`.
- **Досчитывается:** .11: A1_*_r2 x5 (старт 11:24-11:26), NS x2 (идут с 08:43/09:10), в очереди NSR x6 + NSC x3 (7 слотов). .17: NSR x8 + NSC x2 идут, в очереди NSC_E1_b_N0_t0 (11 слотов). Оценка: .17 до ~13:30-14:30 MSK (NSC_E1_b_N0_t1 идёт с 09:49), .11 до ~15:00-16:00 MSK (A1 r1 шли 32-38 мин, r2 может идти дольше; NS ~2.5 ч на задание; NSR/NSC на .11 начнутся только после освобождения слотов).
- Диспетчеры E05 (.11 pid 1696167, .17 pid 183987) работают дальше и берут только оставшиеся A1_r2/NSR/NSC.
- 11:34 MSK уточнение: NS_* на .11 входят в разрешённое сравнение по нормализации -> NS_E4_c_N0 возвращён в очередь .11 (HOLD снят, идёт на той же версии e05_job.py 5c8f251, что и остальные задания .11, pull на .11 не делался). NSR/NSC на .17, запущенные после 11:20 MSK, идут на непроверенной WIP-версии e05_job.py 552ce27 -> сравнивать .11 и .17 по NSR/NSC можно только с этой оговоркой.

## hourly 2026-10-25 11:05 MSK (08:05Z) - D grid 12/32 done, all negative, D methodology suspicious

- Load: .11 7 Console (dispatcher slots 7) / 8 cores, .17 11 / 12 cores (dispatcher slots 11), load avg 9.8 / 13.0. Disk: .11 / 108 GB free (76%), .17 / 101 GB free (54%), /media/user/Data 393 GB free (89%). No archiving needed.
- D done 12/32 (.17 9, .11 3). No target detection: m8_iti6 all <= 0 (c100: gen -0.106, preinh -0.054, preinh_segei -0.058, segei -1.57, nextseg n0/n1 -0.575 and preinh_nextseg n0/n1 -0.568 both be_transfer_rejected_structure; c50: gen_n1 -1.29, preinh_nextseg_n1 / preinh_segei_n1 -0.0078, nextseg_segei_n1 -0.0067). Only m_S4 +0.0075 for c50 preinh_* at short ITI, gone at ITI 6 s.
- Red flags (old errors): (1) c50 Classic final_L = test_L = 25 22 14 1 = initial template L: Train did not grow the dendrites at all although train_valid true. (2) c50 preinh_nextseg_n1 and preinh_segei_n1 bit-identical; nextseg_segei_n1 inh-on m8_iti6 == m8_gate05_off (-0.00668) -> nextseg/segei flags have no effect. (3) readback_test: Parameters.EnableNextSegmentInhibition/EnableSegExcInh set, but Model.* = None and Parameters.UsePresyn_n1 = 0 vs Model 140/196 -> Test model may not carry the inhibition flags. (4) c100 n0 == n1 bit-identical for nextseg and preinh_nextseg -> N0/N1 mode may not reach the model. D results are NOT a valid negative on inhibition until (1)-(4) are checked. Registry rows for D still 'queued' - to be updated by the A/D/E worker.
- Remaining D jobs keep running (cores busy); no new jobs queued by this check.

## normsync 2026-10-25 09:40 MSK (06:40Z) - e05_job console fix + TRAIN_GATE, A1 invalid -> rerun

- Bug: e05_job.py set NMSDK_CONSOLE from spec console AFTER importing repro_cold_lib (NM resolved at import) -> every Train ran on the dispatcher console (e05b); spec console reached only the extra tests. Invalid: A1 x5 (RminNoImproveMinProgress absent from Train XML) and NSR smoke x3. Fixed in 5c8f25124 (console set before import) + TRAIN_GATE after Train: Train console == spec console and spec lset keys present in Train XML, else job_valid=false, INVALID file, tests skipped, rc=3. Running jobs unaffected.
- Requeued: smoke NSR_E1_c_N1_f1_r2/f0_r2 + NSC_E1_c_N1_t1 (.11), NSR_E1_b_N1_f1_r2 + NSC_E1_b_N0_t1 (.17) ahead of pending D; then A1_*_r2 x5 on .11 (e05c, off tests via class), NSR/NSC comparison (.11 9, .17 11).
- D grid: all 32 Classic, no lset; e05c differs from e05b only by the Branch-only RminNoImproveMinProgress (default 0) -> no special console needed, left as is.
- Details: NORMALIZATION_SYNC_2026-10-25.md section 7.3-7.4.

## A/D/E 2026-10-25 08:55 MSK (05:55Z) - plan PLAN_2026-10-25_A_D_E.md

- E DONE: phase8_tiprmin_gate.py time step from config (default 2000, Bin 78bcb00f); verified = gate05 (-0.3416). Affected (0.05 ms, diagnostic): m8_phase8_gate E2_b_s2_itiS/itiS2 +0.0004, E4_b_s2_r -0.1510, E5_b_s2_r -0.0324, plus phase8 gate ROW fires and inference-mid threshold. m_S4, m8_gate05, m8_iti6, m8_itiS unaffected.
- A: cause = TipR at Rmin -> NoImproveCount++ on every length apply, limit 2 -> best-effort at L 73/57/41 although |dt| still falling. Flag RminNoImproveMinProgress (PulseLib 02cc0c7, default 0 = old). A1 x5 running on .11 since 08:37 (console e05c).
- D: inhibition XML patches are dead (BuildStructure rebuilds neuron from NeuronClassName); old InhGrid configs were SymInhC1e9 for all mods -> PSI never active. Fixed via NeuronClassName (e05_job e706927c4), check on/off -0.3416 vs -0.2748. 32 jobs: .17 24 (16 c100 + 8 c50, from 08:48), .11 8 c50 (queued). train_t 2x, be_transfer 1.

## E05 hourly 2026-10-25 06:10 MSK (03:10Z) - E05 series closed, REPASS_ITI6 .11 final

- E5off_c_s0_r BE3 (Classic S50 tau 0.75 ms, NO inhibition; train_valid true, be_check L/C/tips true): m_S4 -0.468, m_S8 0.0, m8_iti6 -0.653, m8_gate05 -0.653 - bit-equal to E5_c (with inhibition). Inhibition has no effect in Classic at S50 as well (pair now complete: E4_c==E4off_c, E5_c==E5off_c). Finished 05:11 MSK.
- REPASS_ITI6_e11 ALL_DONE 05:28 MSK (run_iti.py, ITI 6 s, ref + target pos4). Valid outcome: 13 cases with results.csv (S25 family br25*, inh_c25*), all sep < 0 in both orders (max -0.0002, min -0.0134); inh_c25_genasym_n0 timed out (rc 124, both orders). 32 cases (all inh_c50_* and inh_c100_*, 64 runs) gave NO_RESULTS: Console ran ~5 min but wrote no SelectivityLog/results.csv; their source *_work/Test dirs have no posttune_complete.flag (only posttune_mid_dbg.txt), i.e. the 23.10 inhibition-grid trainings for S50/S100 never produced a completed trained Test. These are VOID, not negative - no conclusion about S50/S100 inhibition from REPASS. Only order/ITI-invariant positive in all REPASS (both hosts) remains W08 / br480_tiprmin (see W08ctrl, m +0.018..0.020, lost with nextseg OFF).
- Series E0-E5 fully executed; queues empty. .17 idle since 05:11, .11 idle since 05:28 MSK. No new series launched (needs Tim): Branch stop criterion (L 73/57/41 vs 400/334/200), Classic rmax refusal / amplitude attenuation on long dendrites, real replicate variability, retraining of S50/S100 inhibition grid if still wanted.
- Disk 06:08 MSK: .11 / 118 GB free (74% used); .17 / 115 GB free (47%); /media/user/Data 404 GB free (89% used, above 5% threshold). No archiving needed.

---

## E05 hourly 2026-10-25 05:05 MSK (02:05Z) - .17 idle gap, E5off_c control, REPASS e11 near end

- .17 was idle 04:26-05:02 MSK (E05 queue exhausted, all E0-E5 points done, no new series without Tim). Queued E5off_c_s0_r BE3q/BE3i6/BE3g5 = Classic S50 tau 0.75 ms WITHOUT inhibition (completes the E5 inhibition on/off pair for Classic; E5_c_s1_r skipped: seed replicate is bit-identical). Started 05:02.
- Finished since 04:05: E5off_c_s0_r and E5_c_s1_r Classic trains (final L 209 185 105 1, no metrics: refused, tests only via BE3); x11 BE3i6/BE3g5 for E1/E2/E3off/E4off and E3weak/E4/E5 BE3* on .17 - all negative, consistent with the 04:05 entry (m8_iti6 = m8_gate05: E1 -0.144, E2/E3off/E3weak -0.508/-0.509, E4/E4off -0.151, E5 -0.653).
- Branch summary unchanged: only E4(off)_b m_S4 +0.072 and E5off_b m_S4 +0.036 are positive at short ITI; at ITI 6 s E4_b -0.103, E5off_b +0.036 (fired none, margin 3.6% of target response, no spike detection) -> no target detection.
- REPASS_ITI6 .11: 73/74 dirs done, last batch jobs_013 (inh_c50 gen/nextseg, 6 Console) running; analyzed cases: 0 order-invariant positive.
- Disk 05:00 MSK: .11 / 126 GB free (72% used); .17 / 115 GB free; /media/user/Data 404 GB free (89% used, >5% threshold). No archiving needed.
- Load: .11 6 Console / 8 cores (REPASS), .17 2-3 Console / 12 cores (only remaining approved control).

---

## E05 hourly 2026-10-25 04:05 MSK (01:05Z) - BE3 re-tests of refused Classic structures

**BE3 (best-effort transfer v3, verified: be_check L/C/tips all true, analyzer rows present).** Classic Train structures tested at dt 0.5 ms, target not first (q = S/4,S/8; i6 = ITI 6 s; g5 = gate05):
- E1_c (S100, tau 2 ms, refused): L 49 47 29 1; m_S4 -0.048, m_S8 -0.009, m8_iti6 -0.144, m8_gate05 -0.144. FAIL as predicted.
- E2_c (tau 0.75 ms, Rm_inh 1e7, refused): L 393 337 217 1 (predicted 400 334 200); m_S4 -0.265, m_S8 0.000.
- E3off_c / E3weak_c (no/weak inhibition, refused): L 393 345 217 1; m_S4 -0.267, m8_gate05 -0.508.
- E4_c == E4off_c (C 1e-10, refused): L 201 177 105 1 (predicted 200 168 101); m_S4 -0.207, m_S8 -0.219, m8_iti6 -0.151, m8_gate05 -0.151. Inhibition on/off bit-equal in metrics.
- E5_c (S50, tau 0.75 ms; train_valid TRUE): L 209 185 105 1; m_S4 -0.468, m8_iti6 -0.653, m8_gate05 -0.653. FAIL as predicted (boundary control).

**Interpretation.** (1) Classic structural learning reaches the theoretically expected L (delay-sync residue within tol) for E2 and E4, so dendrite length / MaxDendriteLength is NOT the limit at dt 0.5 ms. What fails is selectivity: every trained structure responds more to samples than to the target (m < 0). Hypothesis to verify: E0 Console/segsim amplitude ratio 0.36-0.40 at L 200-400 means long dendrites attenuate the signal much more than in segsim; tip R compensates up to rmax 1e10 -> C++ refusal, and the summed peak at the soma loses the coincidence advantage of the target. (2) Inhibition (pre/post, nextseg) has no measurable effect in either trainer at these settings (E4_c == E4off_c; E4_b == E4off_b; E3off_b == E3weak_b). Consistent with REPASS_ITI6.

**REPASS_ITI6 .11:** 46/74 cases done, max sep -0.0004 (no case > 0); batch jobs_009 running (6 Console). .17 REPASS done earlier (see 02:20 entry).

**Series E0-E5 status:** all planned points executed; queues empty on both hosts (.11 busy with REPASS, .17 finishing last Classic trains E5off_c_s0_r, E5_c_s1_r and x11 BE3g5). No new series launched: further points (Branch stop criterion, real replicate variability, Classic rmax / attenuation) need Tim's decision. Next-plan draft: open questions listed in the 00:45Z audit section.

**Disk 04:00 MSK:** .11 / 134 GB free (70%); .17 / 115 GB free (47%); /media/user/Data 402 GB free (89% used, threshold 5% not reached).

---

## E05 series audit 2026-10-25 03:45 MSK (00:45Z) - problems A-D

**A. Seed replicates identical.** No seed exists: e05_job `jitter` multiplies only the LAST tip (TipSynapseResistance[-1], L=1 dendrite); C++ SoftCold reset canonicalises it to TipResistanceCanonLast=86000000 (audit `reset_complete tip_r=[...,86000000]`), Console is deterministic. Bit-identical pairs: E2_b s0n/s1/s2, E1_b s1/s2, E3off_b s0/s1, E4off_b s0/s1, E3weak_b s0_r/s1_r, E4_b s0n_r/s1_r, E5_b s0_r/s1_r; Classic E1_c s0/s1/s2, E3off_c, E4off_c, E4_c same final L. Fix: jitter flagged `jitter_effective=false`, comma parse fixed; s1/s2 replicates dropped/killed. Real variability needs Tim's choice (pattern jitter / excitatory tips / init L).
**B. Classic: no metrics.** Genuine C++ refusal `cpp_training_failure_1` (tip R at rmax 1e10 on 1-2 dendrites, e.g. E4off_c tips `1e10 1e10 3.15e7 8.6e7`, E2_c `4.4e7 1e10 6.2e8`) although delay sync reached (residue 3.5 ms < tol 4.17 ms). posttune -> SKIP_GATE -> Test stays the template (L 52 48 27 1, Capacity 1e-9, NPMembraneBio, UsePresynapticInhibition 0). Old e05_job tested this template. Fix: `train_valid`, `test_is_trained`, `metrics_basis`; tests skipped on template. Best-effort transfer (`be_transfer`, Neuron-block overlay) builds a Test but analyzer writes 0 rows -> default OFF, UNVERIFIED.
**C. Branch: L stops early, no detection.** Overrides reach Train and Test (readback + full Test=Train neuron: Capacity, Preinh2_5 classes, InhSyn R). Branch stops at L 73 57 41 1 (S100 & S50, C 7.5e-11) / 89 73 57 1 (C 1e-10) via its per-dendrite sync criterion, far below L_expect (400 334 200 1 / 200 168 101 1). Inhibition has NO effect on Branch results (E4_b == E4off_b, E3off_b == E3weak_b bit-identical). Note: L_expect key is never applied (code reads L_init) and is irrelevant after SoftCold (L -> 1 1 1 1). Needs Tim decision (C++ Branch trainer criterion).
**D. gate05 vs gate.** gate05 verified at dt 0.5 ms (xt/gate05/Test/Project.ini Default/Global 2000; new key `gate05_dt_ok`). Old `gate_GlobalTimeStep`=20000 read the phase8 Test (dt 0.05 ms) - renamed `phase8_gate_GlobalTimeStep`, `m8_gate` -> `m8_phase8_gate` (diagnostic). m8_gate05 == m8_iti6 in Branch is expected (responses order/ITI-independent at these settings).

**Valid results (Branch, dt 0.5 ms, target not first):** none detects the target. E4(off)_b m_S4 +0.072, m_S8 +0.029, m8_iti6 -0.103; E5off_b m_S4 +0.036 (= m8_iti6), E2_b m_S4 0.0 / m8_iti6 -0.342; E1_b m_S4 -0.153; E5_b -0.129; E3off/E3weak_b -5e-5. Neuron silent in tests (Branch Test FixedLTZThreshold 1).

**Queue actions:** killed (provable duplicates) .11: E2_c_s2, E3off_c_s2, E4off_c_s2; .17: E3weak_c_s1_r, E3weak_c_s2_r, E4_c_s2_r, E5_c_s2_r, E5off_c_s1_r, E3weak_b_s2_r. Dropped from queue: .11 E4off_b_s2, E1_b_s0r; .17 E5off_c_s2_r, E5off_b_s2_r. Own BE/BE2 re-test jobs killed and disabled (0 rows). Kept: Classic representatives E3weak_c_s0_r, E5off_c_s0_r, E5_c_s1_r (.17), REPASS_ITI6 (.11). Every kill logged in dispatch.log (AGENT_KILL).
**Open for Tim:** Branch trainer stop criterion; how replicates should vary; Classic rmax refusal (raise rmax / accept refused structure / proper transfer); phase8 dt 0.05 ms gate (unchanged, pending).

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

## 2026-10-24T23:20Z (02:20 MSK 25.10): hourly check, E05 + REPASS_ITI6

**Incidents (fixed this hour)**
- .17 E05 dispatcher (pid 56417, started 00:45 MSK) had no NMSDK_ROOT -> JOB=/home/user/Nmsdk/... missing -> 22 queued jobs ended rc=2 in ~20 s each (01:14-01:22 MSK); .17 ran only REPASS + E5_c_s0, idle 01:48-02:14 MSK after REPASS finished. Fix: dispatcher restarted 02:14 MSK (pid 113632, NMSDK_ROOT=~/tl-agent/Nmsdk, console e05b, DATA_DIR set, no reserve); the 22 labels requeued as `<label>_r` (E5/E3weak/E5off s0 first, then s1, s2).
- dt rule violation found: phase8_tiprmin_gate.py forces Test `GlobalTimeStep 20000` (dt 0.05 ms) for the posttune gate test, while Train and the e05 XT tests run at 2000 (now step 5e-4). => `m8_gate`, gate ROW fires/detection and the C++ inference-mid threshold of every E05 job are at dt 0.05 ms and are NOT valid results (diagnostic only); XT `neuron_fired` flags use that threshold too. m(S/4), m(S/8), m8_iti6 (relative ltz at dt 0.5 ms) stay valid. Fix in e05_job.py (this commit): readback of GlobalTimeStep, new `gate05` test (original samples, target at position 4, Delay 1.5 s, dt 0.5 ms) -> `m8_gate05`, plus `gate_GlobalTimeStep` in result.json. phase8 itself not changed (Bin, needs decision).

**E05 results since 01:10 MSK** (m = (tgt - max foil)/tgt, ltz at dt 0.5 ms)
| job | host | outcome | final L | m(S/4) | m(S/8) | m8_iti6 |
| --- | --- | --- | --- | --- | --- | --- |
| E3off_c_s0 | .11 | C++ refusal (TipR cap 1e10) | 393 345 217 1 | - | - | - |
| E4off_c_s0 | .11 | C++ refusal (TipR d1,d2 1e10) | 201 177 105 1 | - | - | - |
| E4_c_s0 | .17 | C++ refusal | 201 177 105 1 | - | - | - |
| E5_c_s0 (old bin) | .17 | not_converged_at_stop, TipR d1,d2 1e10, Test model stale (L 25 23 15) | 209 185 105 1 | - | - | - |
| E1_c_s1 | .11 | C++ refusal (= s0) | 49 47 29 1 | - | - | - |
| E2_b_s0n | .11 | Done_BE early | 73 57 41 1 | 0.000 | -0.053 | -0.342 |
| E3off_b_s0 | .11 | Done_BE; training identical to E2_b_s0n (same L, TipR, audit ROW) | 73 57 41 1 | -0.00005 (flat 0.0764) | - | - |
| E4off_b_s0 | .11 | Done_BE early | 89 73 57 1 | +0.072 | +0.029 | -0.103 |
| E1_b_s1 | .11 | Done_BE | 28 21 14 1 | -0.153 | +0.045 | -0.238 |

- Classic: grows to the design length (E3off ~400, E4/E4off ~200, E5 ~200) but tip resistances of d1/d2 hit the 1e10 cap -> refusal/no convergence. Consistent with E0 (Console amplitude after 200-400 segments ~0.36-0.40 of the tip input): attenuation, not delay, is the binding limit.
- Branch: stops by Done_BE at 73/57/41 (E2/E3off) or 89/73/57 (E4off), far below design (400/334/200, 200/168/101); no detection in any test; E2 prediction (m ~0.11 Branch) not met; off controls are FAIL as expected but indistinguishable from "on".
- Inhibition overrides reach Train/Test XML (readback) but do not change Branch training at all (E2_b_s0n == E3off_b_s0 bit-identical training) -> "identical repeat" class: inhibition is inactive during Branch growth at these params.

**REPASS_ITI6 e17: finished 01:48 MSK** (43 cases, 41 with results, 2 NO_RESULTS). Order-invariant positive (ref and tpos4 both m>0, target fired, no foil fired): only BR480 Branch structures:
W08_BR480_N0_PSIoff_NEXT, br480_nextseg, h0_b480_nextseg_n0_pton all give identical ltz (tgt 0.0365 / max foil 0.0358, m +0.019) -> one deterministic structure, not 3 replicas; br480_tiprmin (L 85 46 25 1) m +0.017 (0.0517/0.0508). All S25/S50/S100 cases: m <= 0 in at least one order (br25sim_k4 +0.164 ref / -0.211 tpos4, h0_b100_preinh_n0 +0.027/-0.121, br100_preinh, br50_preinh, br50_gen, h2_keepdone_w33/W01_CL50: order artifacts). Tests at dt 0.5 ms (Test ini 2000).
**REPASS_ITI6 e11**: 23/53 cases done (16 inh_c100_* NO_RESULTS, the rest m <= 0); still running (batch 008 of 017, 2 Consoles).

**Launched**
- .17 W08ctrl_e17_20261024T2313Z (Test-only, run_iti.py): W08 tlast d6, tpos2 d12, tpos4 d6 nextseg OFF, tpos4 d1.5; br480_tiprmin tlast d6, tpos2 d12, tpos4 d1.5.
- .17 E05 requeue (22 jobs), .11 queue continues (E2_c_s2 ... E1_b_s0r).
- Load: .11 8/8 slots (7 Consoles + job between Consoles); .17 12/12 (7 W08ctrl + 5 E05 at 02:16 MSK).
- Disk: .11 / 69 %; .17 / 46 %, /media/user/Data 89 % (409 GB free) -> no cleanup.

**W08ctrl first results (02:25 MSK, dt 0.5 ms; d12 runs partial 5/8 trials)**
| test | W08 (BR480 nextseg) tgt / max foil / m / fired | br480_tiprmin tgt / max foil / m / fired |
| --- | --- | --- |
| target last, ITI 6 s | 0.03654 / 0.03582 / +0.0196 / 00000001 | 0.05174 / 0.05082 / +0.0177 / 00000001 |
| target pos 2, ITI 12 s (5/8) | +0.0196 / 00100 | +0.0177 / 00100 |
| target pos 4, ITI 1.5 s | +0.0196 / 00001000 | +0.0177 / 00001000 |
| target pos 4, ITI 6 s, nextseg OFF | 0.03720 / 0.03846 / **-0.034 / 11111111** | n/a |
=> BR480 Branch nextseg selectivity is order- and ITI-invariant (1.5-12 s) and requires nextseg inhibition (OFF -> all samples fire, target not max). Margin only ~2 % of target ltz. Not reproduced at S25/S50/S100.
