# SILENT_TEST variant A — offline mid sweep (2026-10-22)

**Постановка.** На замороженном attempt rep3 **`G1.S1.W01-11-20261021T113257Z-15892`** (Trainer×Mode **Classic×N0**, Span **50**, Mod **AsymRm→gen**, PostTune **OFF**, case `W01_CL50_N0_PSIoff`) сравнили Test-gate при финальном C++ пути **thr=1** (`test_cpp_mid`, `--force-test-cpp-mid`) и при **`--diagnostic-threshold`** = `candidate_mid` из `posttune_complete.flag` (`train_candidate`). Полный retrain и G1 RERUN **не** запускались; Console прогон только Test-gate на копии workdir после Train.

**Train / Test (канон):** [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Train), [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test).

**Bundle:** `/home/user/TLAgent-20261020/runs/G1.S1.W01-11-20261021T113257Z-15892/W01/W01_CL50_N0_PSIoff/attempt-0001/` (partial extract); frozen Train/Test state для gate — `/home/user/TLAgent-20261020/runs/W01_CL50_N0_PSIoff_20261021T113258Z_3673774_4a914156_work/` (тот же rep3). Gate: [`phase9_preinh_bc_gate.py`](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityAsymRm/scripts/phase9_preinh_bc_gate.py), метрики — [`selectivity_metrics.py`](../../../../Bin/Configs/SpikeSamples/StructTrain/scripts/selectivity_metrics.py). Console: `/home/user/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole`.

---

## 1. `posttune_complete.flag` и TipR

| Фаза | Файл | Содержимое |
|------|------|------------|
| Train | `Train/posttune_complete.flag` | **отсутствует** (`EnablePostTrainTuning=0` по волне; PostTune probes на Train не финализировали flag) |
| Test | `Test/posttune_complete.flag` | `mid=1`, `result=2` (NonSeparable), `inference=1`, `FixedLTZ=1`, **`candidate_mid=0.0024126668029073456`**, `gap≈−8.36e−4`, `landscape_ok=0` |
| Test | `tipr` | `86000000×4` (flat Rmin, согласуется с partial G1) |

`candidate_mid` на этом кейсе взят из **Test inference mid** (не из Train probe flag). Probe metrics (8 значений из flag): max foil peak **≈0.00335**, target trial в зафиксированном CSV G1 **`ltz_potential_max≈0.00223`** — **ниже** `candidate_mid`, поэтому soma-fire на target при diagnostic thr ожидаемо **нет**.

---

## 2. Парный Test-gate (offline)

| Вариант | Порог | fires | Acc | Цель (`target_hit`) | mode | child/gate |
|---------|-------|-------|-----|---------------------|------|------------|
| **train_candidate** | `0.0024126668029073456` | `01000101` | **4/8** | **нет** | miss_target | gate_rc **−15** (grace, CSV полный) |
| **test_cpp_mid** | **1.0** (C++ NonSeparable → silent) | `00000000` | **7/8** | **нет** | silent | gate_rc **−15**; flag совпадает с G1 partial |

Baseline G1 partial (тот же bundle): Acc **7/8**, Цель **нет**, `fires=00000000` — совпадает с **test_cpp_mid**.

При **train_candidate** часть foils даёт soma-fire (3 FA), target (trial 0) по-прежнему **0**; при **thr=1** все `neuron_fired=0`, foils классифицируются как «не fire» → Acc 7/8 без цели.

---

## 3. Вердикт по гипотезам (H1, H3)

**H1 (silent mid LTZ≈1 подавляет target ниже порога).** В **сильной** формулировке из [`SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md`](SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md) (**target_hit=1** или **fires[0]=1** при `candidate_mid`, при silent cpp) — **не подтверждена**: при diagnostic thr target **не** fire, peak target **ниже** `candidate_mid`. В **слабой** формулировке (thr=1 **маскирует** любую soma-активность, видимую при более низком finite thr) — **подтверждена**: `01000101` vs `00000000`, Acc 4/8 vs 7/8.

**H3 (Train/Test probes vs применённый thr=1 на Test).** **Подтверждена**: на том же замороженном L/TipR/Test EXP **`train_threshold_test`** даёт **fires≠all-zero**, тогда как production **`test_cpp_mid`** оставляет **thr=1** и silent phenotyp — finite `candidate_mid` из flag **не** переносится на классификатор Test в штатном пути.

**H4 (flat TipR N0).** Остаётся запасной осью: даже при `candidate_mid` target peak не пересекает порог; cold variant B не требовался (offline дал различимые пороги).

---

## 4. Артеfacts (локально)

- Sweep workdir: `/tmp/silent_test_w01_15892/{train_candidate,cpp_test}/`
- Логи gate: `…/train_candidate_gate.out`, `…/cpp_test_gate.out`

---

*Выполнено 2026-10-22 на ветке `timelearner_fix2`; matrix RERUN не запускался.*
