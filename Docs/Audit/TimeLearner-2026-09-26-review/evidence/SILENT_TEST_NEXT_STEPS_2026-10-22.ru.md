# DEBT-D2-silent-test — следующие шаги (2026-10-22)

**Контекст:** G1 S1 RERUN закрыт; exit-clean остаются **3/13** волн (**W01**, **W13**, **W33**). На всех девяти строках partial extract Train сходится (`converged_need0` или `converged_posttune_finalized`), Test в режиме **silent** даёт **Acc=7/8**, **Цель=нет**, `fires=00000000`, `detection_quality=target_not_detected`. Paired **F5** (γ=0 vs γ=1) на `W01_CL50_N1_PSIoff` **не** меняет исход ([`F5_GAMMA_PAIRED_2026-10-22.ru.md`](F5_GAMMA_PAIRED_2026-10-22.ru.md)). E2 R8: silent **EQUIVALENT** на S0/S1/S2 — ось **detection/mid**, не инфраструктура B1/E0 ([`E2_R8_SYNTHESIS_2026-10-21.ru.md`](E2_R8_SYNTHESIS_2026-10-21.ru.md)).

**SHA кампании (G1/F5):** Console `745d6061…`, PulseLib `6d746ac`. Новую matrix-кампанию **не** планируем; один точечный cold на `.11` — только если offline-диагностика не даст различимых порогов (см. § минимальный эксперiment).

---

## Фенотип по Trainer×Mode (exit-clean G1)

### Classic×N0 → Span 50 → AsymRm → gen

| PostTune | Case | Train conv. | L | TipR (rep3) | FixedLTZ (extract) | Test |
|--------|------|-------------|---|-------------|------------------|------|
| **OFF** | `W01_CL50_N0_PSIoff` | `converged_need0` | 27 22 15 1 | 86M×4 (CanonRmin flat) | **1.0** | silent 7/8 |
| **ON** | `W33_CL50_N0_PSIoff_POST` | `converged_posttune_finalized` | 27 22 15 1 | 20M×3 + 86M | **1.0** | silent 7/8 |

Train/Test: [`TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/{Train,Test}`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Train), [`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test); W33 — [`…/W33_CL50_N0_PSIoff_POST/{Train,Test}`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W33/inputs/W33_CL50_N0_PSIoff_POST/Train).

**Наблюдение:** PostTune ON/OFF **не** разводит исход на Span 50 N0 — оба silent при разной TipR-геометрии (flat Rmin vs midband+tip1).

### Classic×N1 → Span 50 → AsymRm → gen

| PostTune (волна) | Case | Train conv. | L | TipR (rep3) | Test |
|------------------|------|-------------|---|-------------|------|
| OFF* | `W13_HIST_ltz50_gen` | `converged_posttune_finalized` | 25 22 15 1 | 20M×3 + 86M | silent 7/8 |

Train/Test: [`TimeLearnerMatrix/W13/inputs/W13_HIST_ltz50_gen/{Train,Test}`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W13/inputs/W13_HIST_ltz50_gen/Train).

\*Колонка «PostTune OFF» — дизайн волны G1; метка `converged_posttune_finalized` и TipR после PostTune указывают, что **Train по факту прошёл PostTune** (HIST-кейс LTZ). Это не противоречит silent Test, но смешивает оси «vol OFF» и «C++ PostTune phase».

### F5 paired (тот же span, N1, не G1 exit-clean axis)

**Classic×N1 → 50 → AsymRm → gen**, PostTune OFF, `W01_CL50_N1_PSIoff`: Need=0, L=`25 22 15 1`, TipR 2.88M×3 + 86M, `test_mid_gap≈−0.00389`, silent, `child_rc=-15` ([`F5_GAMMA_PAIRED_2026-10-22.ru.md`](F5_GAMMA_PAIRED_2026-10-22.ru.md)). γ=0 ≡ γ=1.

### Конtrast (не silent, та же ось mid)

Branch×N1 `br25_gen` при **PostTune OFF** давал `fires=10110000`, detected ([`POSTTUNE_FIX_COLD_SUMMARY_2026-10-19.ru.md`](POSTTUNE_FIX_COLD_SUMMARY_2026-10-19.ru.md), [`M1_BOUNDARY_MAP_2026-10-17.ru.md`](M1_BOUNDARY_MAP_2026-10-17.ru.md) A2.1). Classic W01/W13 на текущем SHA **не** воспроизводят этот partial-fire режим — отдельная гипотеза «Classic canon TipR + LTZ=1».

**C2:** для W01/W13/W33 oracle `sep_marginal_m_oracle≤0`, feasible=True ([`G1_vs_C2_2026-10-21.tsv`](G1_vs_C2_2026-10-21.tsv)) — Console `Need=0` **не** означает PASS verify; marginal oracle согласуется с silent Acc 7/8 (нет FP, нет target hit).

---

## Общий механизм (код + gate)

1. **Train:** `EndOfLearning` → при `EnablePostTrainTuning=1` — `EnterPostTunePhase` → probes `BuildRecognitionProbePatterns` → `FinalizePostTuneMid` ([`NNeuronTimeLearner.cpp`](../../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.cpp) ~L4694–5251, [`NNeuronPostTrainTune.cpp`](../../../../Libraries/Nmsdk-PulseLib/Core/NNeuronPostTrainTune.cpp)). При `!LandscapeOk` или `gap<1e-4` → `mid = PostTrainSilentThreshold` (**1.0**), `PostTuneResult=NonSeparable` ([`POSTTUNE_ALGORITHM_AUDIT_2026-10-19.ru.md`](POSTTUNE_ALGORITHM_AUDIT_2026-10-19.ru.md)).
2. **Train без PostTune:** `CalibrateFixedLTZThresholdFromTraining` (~L880) из `LastSyncedMinLTZ`/`MaxLTZ`; при degenerate min/max — skip, порог может остаться не калиброванным.
3. **Test:** `MaybeStartInferenceMidProbes` (~L5421) — только если `EnablePostTrainTuning && EnablePostTrainMidThreshold && FixedLTZ≥0.9`; повторный mid на **MatrixData** Test. При `inference mid still silent` + `test_mid_quality=nonseparable` gate трактует как quality, не crash ([`posttune_verify.py`](../../../../Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py) ~L1861–1890).
4. **Отчёт G1:** `FixedLTZThreshold=1` и `mode=silent` в partial TSV — **финальное** состояние перед/после Test; `metrics_raw`: `target_hit=0 fire_all=0 matches=01111111` ([`G1_S1_PARTIAL_METRICS_2026-10-22.tsv`](G1_S1_PARTIAL_METRICS_2026-10-22.tsv)) — классификатор не видит soma-fire на target при thr≈1.
5. **`child_rc=-15`:** grace gate при nonseparable inference mid (F5/G1), связан с [`DEBT-TRACE-NOCSV`](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md) при зависании TRACE, но на exit-clean G1 Acc/Цель **уже** извлечены (`launch.exit=0`).

---

## Гипотезы (ранжирование)

| Ранг | Гипотеза | Почему правдоподобно | Что опровергнет |
|------|----------|----------------------|-----------------|
| **H1** | **Финальный LTZ≈1.0 (silent mid)** подавляет target peak ниже порога; foils тоже не fire → Acc 7/8 без цели | Единый `FixedLTZ=1` на W01/W13/W33; политика NonSeparable → silent ([`POSTTUNE_ALGORITHM_AUDIT_2026-10-19.ru.md`](POSTTUNE_ALGORITHM_AUDIT_2026-10-19.ru.md)); A2.4 thr=1 = тот же путь | Offline sweep: при `candidate_mid` из flag (≈0.1 на D3 gen) target fire на Test **без** retrain |
| **H2** | **PostTune CanonRmin flatten** (default `kPostTipCanonRmin`) уничтожает midband, landscape на probes NonSeparable | W33/W13 TipR 20M×3+86M vs W01 86M×4; M1 D3: flatten + cpp thr=1; A2.1 OFF на **Branch** gen восстанавливает partial fires | Classic W01 cold: `PostTrainTipResistanceMode=KeepDone` или явный `EnablePostTrainTuning=0` + midband TipR → fires≠00000000 |
| **H3** | **Train probes ≠ Test Matrix** → Train NonSeparable не implies Test, но C++ всё равно ставит thr=1 и **не** применяет best-effort/candidate на Test | Аудит §«Честность mid»; inference mid тоже nonseparable на G1/F5 | `train_threshold_test` (posttune_verify) fires≠all-zero при thr=candidate_mid на **замороженном** G1 bundle |
| **H4** | **Classic N0 @50: все TipR→Rmin (86M×4)** — soma response слишком flat для Pack A target при любом mid &lt; 1 | G1 W01 L=27 22 15 1, flat TipR; F4/F6 N1 с midband TipR **тоже** silent — ослабляет как *единственную* причину, но N0 — крайний случай | TipR midband-only overlay (без PostTune) на W01_N0 меняет LTZ landscape / fires |

**H4 update 2026-10-22:** сильная формулировка **ослаблена** offline+E1.1b ([`SILENT_TEST_H4_MARGIN_2026-10-22.ru.md`](SILENT_TEST_H4_MARGIN_2026-10-22.ru.md)): при `candidate_mid` foils уже fire; target LTZ≈0.00223 &lt; mid≈0.00241; γ(L)≈const ⇒ равномерный TipR scale сохраняет gap&lt;0. TipR overlay cold **deferred** (D1); следующий cold — H2 KeepDone.
| **H5** | **Marginal separability (C2 oracle)** — физически мало gap; `Need=0` = controller Done, не verify PASS | `m_oracle≤0`, sep_marginal в G1 vs C2 | C2 offline margin &gt; 0 при тех же L/TipR — маловероятно без смены state |
| **H6** | **γ / F4 / F6 / E2 wiring** | **Отвергнуты** на W01: E2 EQUIVALENT; F5 paired идентичен; F4/F6 не меняют silent ([`F4_F6_FLOOR_COLD_2026-10-20.ru.md`](F4_F6_FLOOR_COLD_2026-10-20.ru.md)) | — |
| **H7** | **TRACE hang (−15)** как первичная причина silent | На G1 exit-clean метрики есть; −15 сосуществует с `quality_fail` | Только если без CSV Acc был бы «—» |

**Приоритет для кода:** H1+H2+H3 → патч-точки `FinalizePostTuneMid` (Classic+Branch), `ApplyPostTrainTipMode`, политика best-effort / KeepDone ([`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md) §Verify vs Test).

---

## Минимальный эксперiment (один offline **или** один cold)

### Вариант A — **offline (предпочтительно, без Console train)**

**Цель:** отделить «thr=1 обязателен» от «при finite candidate_mid target виден на Test».

**Вход:** attempt bundle rep3 **`G1.S1.W01-11-20261021T113257Z-15892`** (Classic×N0, case `W01_CL50_N0_PSIoff`) — каталоги Train/Test после Train, файлы `posttune_complete.flag`, `posttune_mid_dbg.txt`, `SelectivityLog/results.csv` если есть.

**Действия:**

1. Прочитать `posttune_complete.flag`: `candidate_mid`, `metrics`, `result`, `tipr` vs `tipr_snapshot`.
2. На **замороженном** Test EXP (Train XML уже с финальными L/TipR) запустить только Test-gate через [`posttune_verify.py`](../../../../Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py) / `phase9_preinh_bc_gate.py` с `--diagnostic-threshold <candidate_mid>` (вариант `train_candidate`, см. ~L1835–1838) **без** `--force-test-cpp-mid`.
3. Сравнить с default cpp path (`test_cpp_mid`) и с thr=1.

**Критерии:**

- Если **train_candidate** даёт `target_hit=1` или fires[0]=1, а cpp thr=1 — silent → **H1/H3 подтверждены**, фикс в политике mid (best-effort / не маскировать Test thr=1).
- Если оба silent → смотреть soma peaks (A3 trace / `tl_probe_kernels analyze` на том же L/TipR) — **H4**.

**Train/Test cites:** W01 как выше.

### Вариант B — **один cold Console (только если A inconclusive и `.11` ≤8 Console)**

**Парный не нужен** — один diagnostic run:

- **Case:** `W01_CL50_N0_PSIoff` (якорь exit-clean, PostTune OFF по волне).
- **Overlay:** `--train-param EnablePostTrainTuning=0` **и** `--train-param AutoCalibrateFixedLTZThreshold=1` (явно), плюс `--train-param PostTrainTipResistanceMode=<KeepDone>` *или* отключение Canon flatten — **только одна** ось на run (не смешивать с γ/F5).
- **Снять:** `posttune_complete.flag`, inference `posttune_mid_dbg.txt`, полный gate log, `FixedLTZ` до Test.

**Ожидание при H2:** частичные fires как A2.1 Branch gen (не обязательно 8/8).

---

## Что **не** делать следующим

- Повтор F5 / γ на том же `W01_CL50_N1_PSIoff` ([`F5_GAMMA_PAIRED_2026-10-22.ru.md`](F5_GAMMA_PAIRED_2026-10-22.ru.md) §3).
- Новая G1/matrix RERUN на том же SHA ([`G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md`](G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md)).
- Списывать silent на DEBT-G1-exit-gate (harness **done** 2026-10-22).

---

## Связанные артеfacts

| Документ | Роль |
|----------|------|
| [`G1_S1_PARTIAL_METRICS_2026-10-22.ru.md`](G1_S1_PARTIAL_METRICS_2026-10-22.ru.md) | Канон exit-clean метрик |
| [`F5_GAMMA_PAIRED_2026-10-22.ru.md`](F5_GAMMA_PAIRED_2026-10-22.ru.md) | γ control |
| [`E2_R8_SYNTHESIS_2026-10-21.ru.md`](E2_R8_SYNTHESIS_2026-10-21.ru.md) | Не DIFFERENT по wiring |
| [`POSTTUNE_ALGORITHM_AUDIT_2026-10-19.ru.md`](POSTTUNE_ALGORITHM_AUDIT_2026-10-19.ru.md) | NonSeparable → thr=1 |
| [`M1_BOUNDARY_MAP_2026-10-17.ru.md`](M1_BOUNDARY_MAP_2026-10-17.ru.md) | train_candidate vs cpp_test |
| [`TECH_DEBT_TIMELEARNER_2026-10-20.ru.md`](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md) | DEBT-D2 registry |

---

*Docs-only расследование AGENT_PLAN 2026-10-22; cold не запускался.*
