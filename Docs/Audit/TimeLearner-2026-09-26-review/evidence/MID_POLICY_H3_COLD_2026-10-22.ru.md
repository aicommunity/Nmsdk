# MID_POLICY H3 — cold verify `UseCandidateMidOnNonSeparableTest=1` (2026-10-22)

**Постановка.** После патча PulseLib (`ApplyCandidateMidOnNonSeparableTest` в `FinalizePostTuneMid`, default-off) нужен один **Test-only** cold на замороженном W01 rep3 с **`UseCandidateMidOnNonSeparableTest=1`** и тем же C++ путём, что offline **`test_cpp_mid`** (`phase9_preinh_bc_gate.py --skip-tipr-mid --force-test-cpp-mid`). Offline baseline зафиксирован в [`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md): при **thr=1** (flag=0) — `fires=00000000`, Acc 7/8; при diagnostic **`candidate_mid≈0.0024126668029073456`** — `fires=01000101`, Acc 4/8, Цель нет. Ожидание cold с **flag=1**: C++ inference по-прежнему **NonSeparable** (`result=2`), но **`FixedLTZ`/`mid` ≈ `candidate_mid`**, phenotyp gate как у **`train_candidate`**, в `posttune_complete.flag` — **`test_mid_policy=candidate`**.

**Иерархия:** Trainer×Mode **Classic×N0** → Span **50** → NeuronModel **TimeLearner (Classic)** → Mod **AsymRm→gen**; PostTune **OFF** на Train волне; case **`W01_CL50_N0_PSIoff`**, attempt **`G1.S1.W01-11-20261021T113257Z-15892`**.

**Конфиги (канон matrix):** [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Train), [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test). Прогон — копия frozen workdir с патчем только параметра H3 (без retrain).

**Provenance.** Nmsdk **`e44c8f20aaf9793717600fbc23fe4c3649617d09`**, PulseLib **`5e5a59dfbae08987d0b9ad9e304b43c033c89bb7`**, Console **`/home/user/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole`** (SHA-256 prefix **`4a0658f3`**). Workdir copy: `/tmp/h3_mid_flag1_w01/` ← `/home/user/TLAgent-20261020/runs/W01_CL50_N0_PSIoff_20261021T113258Z_3673774_4a914156_work/`.

**Harness.** [`phase9_preinh_bc_gate.py`](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityAsymRm/scripts/phase9_preinh_bc_gate.py) `--skip-tipr-mid --force-test-cpp-mid --span-ms 50 --test-t 40`; метрики — [`selectivity_metrics.py`](../../../../Bin/Configs/SpikeSamples/StructTrain/scripts/selectivity_metrics.py). Лог: `/tmp/h3_mid_flag1_w01/phase9_run.log`.

---

## Результат cold (flag=1)

| Поле | Offline `train_candidate` | Offline `test_cpp_mid` (flag=0) | **Cold flag=1 + C++ Test mid** |
|------|-------------------------|----------------------------------|--------------------------------|
| Порог / `FixedLTZ` | `0.0024126668029073456` | `1.0` | **`0.0024126668029073456`** |
| `fires` | `01000101` | `00000000` | **`01000101`** |
| Acc | 4/8 | 7/8 | **4/8** |
| Цель (`target_hit`) | нет | нет | **нет** |
| `result` (flag) | — | `2` | **`2`** |
| `test_mid_policy` | — | — | **`candidate`** |
| gate `child_rc` | −15 | −15 | **−15** (CSV полный, grace) |

`Test/posttune_complete.flag` (cold): `mid=0.0024126668029073456`, `candidate_mid=0.0024126668029073456`, `FixedLTZ=0.0024126668029073456`, `landscape_ok=0`, `inference=1`, `result=2`, **`test_mid_policy=candidate`**.

---

## Вердикт

**PASS** относительно offline-ожидания для оси **H3 (harness + C++ policy):** при **`UseCandidateMidOnNonSeparableTest=1`** штатный Test inference больше **не** оставляет silent **`FixedLTZ=1`** при finite `candidate_mid`; gate phenotyp **бит-в-бит** совпадает с offline **`train_candidate`**, при этом **`PostTuneResult=NonSeparable`** сохранён (`result=2`, quality_fail по цели — ожидаемо).

**Не закрыто этим прогоном:** регрессия **flag=0** (default) — по политике H3 cold не обязательна; полный **`DEBT-D2-silent-test`** (G1 silent Acc 7/8 при default, W13/W33, Controller contract) остаётся отдельной работой. **H1** (target hit при finite mid) по-прежнему **нет** (peak target &lt; `candidate_mid`).

См. также [`MID_POLICY_H3_2026-10-22.ru.md`](MID_POLICY_H3_2026-10-22.ru.md).
