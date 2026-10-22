# SILENT_TEST H2 — frozen TipR overlay W01 (2026-10-22)

**Постановка.** После H2 KeepDone cold на W33 ([`SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md`](SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md), SHA `655f7659e`) гипотеза **H2** осталась **inconclusive** из‑за Train abort (`EmitToGlog` / `rc=-6`). Следующий шаг без полного KeepDone retrain: на **замороженном** G1 W01 Test bundle наложить TipR midband / keep-snapshot (не CanonRmin flatten) и сравнить Test-only gate при **thr=1** и **`candidate_mid`** через `phase9_preinh_bc_gate.py --skip-tipr-mid --diagnostic-threshold`. Полный Train, G1 RERUN и повтор KeepDone cold на W33 **не** запускались.

**Иерархия:** Trainer×Mode **Classic×N0** → Span **50** → NeuronModel **AsymRm** → Mod **gen**; PostTune по волне **OFF**; ось эксперимента — только XML TipR + Test-gate.

**Конфиги Train / Test (канон matrix):** [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Train), [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test).

**Источник bundle:** `G1.S1.W01-11-20261021T113257Z-15892` / work `W01_CL50_N0_PSIoff_20261021T113258Z_3673774_4a914156_work` (rsync → `.17` как `H2.TipROverlay-W01-src`).

---

## Прогоны на `.17` (M40)

| Поле | Значение |
|------|----------|
| Host | `.17` (`10.245.1.17`) |
| Console | `/home/user/tl-agent/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole` |
| Console SHA-256 prefix | **`4a0658f3…`** |
| `LD_LIBRARY_PATH` (успешный старт `-h`) | `/home/user/tl-agent/lib` (`libglog.so.0`) |
| Gate | `phase9_preinh_bc_gate.py --skip-tipr-mid --diagnostic-threshold <thr> --span-ms 50` |
| `candidate_mid` | `0.0024126668029073456` (из G1 Test `posttune_complete.flag`) |

| RUN_ID | Роль |
|--------|------|
| `H2.TipROverlay-17-20261022T090300Z` | первая серия: **rc=127** (`libglog.so.0` not found без `env.sh`) |
| `H2.TipROverlay-17-20261022T090800Z` | повтор с `source tl-agent/env.sh`: все 6 вариантов **`gate_rc=1`**, diagnostic **`rc=-6`**, **`fires=null`**, нет `results.csv` |

Корень артефактов: `/media/user/Data/TLAgent-20261020/runs/H2.TipROverlay-17-20261022T090800Z/` (`h2_tipr_overlay_summary.json`, `*.result.json`, `*.gate.out`, копии EXP).

---

## Матрица TipR × порог (T090800Z)

| TipR overlay | Порог | Ожидание H2 | Факт |
|--------------|-------|-------------|------|
| **baseline_flat** `86M×4` | thr=1 | silent `00000000` (G1) | **не измерено** — `fires=null`, `rc=-6` |
| **baseline_flat** `86M×4` | candidate_mid | `01000101` (offline W01) | **не измерено** — `fires=null`, `rc=-6` |
| **midband_20m** `20M×3+86M` | thr=1 | fires≠0 при H2 | **не измерено** |
| **midband_20m** `20M×3+86M` | candidate_mid | сравнить с baseline | **не измерено** |
| **keep_snap_2p88m** `~2.88M×3+86M` (W13 `tipr_snapshot`) | thr=1 | KeepDone-геометрия | **не измерено** |
| **keep_snap_2p88m** | candidate_mid | сравнить с baseline | **не измерено** |

Во всех шести клетках `h2_tipr_overlay_summary.json`: `gate_rc=1`, `fires=null`, `acc=null`, хвост gate: `diagnostic threshold run produced no results.csv (rc=-6)`.

**Сигнатура abort (Test `run_train_candidate_gate.log`, baseline thr=1):** `*** stack smashing detected ***` → `SIGABRT` → `__stack_chk_fail` в **`RDK::Logging::detail::EmitToGlog()`** — тот же класс, что KeepDone cold W33 (`child_rc=-6`), а не вердикт TipR→landscape.

Ранний `T090300Z` дал ту же пустую метрику при **rc=127** (отсутствие glog в loader path); после фикса `LD_LIBRARY_PATH` физика TipR всё равно не была замерена из‑за smash.

---

## Вердикт H2

**Still inconclusive.** TipR overlay на frozen W01 **не** дал ни одного валидного байта `fires`; гипотеза «midband / keep-snapshot vs CanonRmin flatten восстанавливает fires на thr=1» **не подтверждена и не ослаблена** этим RUN. Долг относится к **инфре `.17` Console** (нестабильный phase9 diagnostic path: `EmitToGlog` / `rc=-6` на SHA `4a0658f3…` + `tl-agent/lib` glog), а не к физике TipR.

Ранее известные offline факты без изменения: W33/W13 уже несут TipR **20M×3+86M** и при thr=1 остаются silent ([`SILENT_TEST_W13_W33_MID_2026-10-22.ru.md`](SILENT_TEST_W13_W33_MID_2026-10-22.ru.md)) — это **не** замена измеренного overlay на том же L W01.

---

## Next (не `.17` abort)

1. **Не** повторять TipR overlay / KeepDone cold на `.17` с тем же Console+glog, пока не закрыт `EmitToGlog` smash.
2. После освобождения локальных слотов D1 (`3cefd64` W02) — retry overlay на **local HEAD Console** (системный glog; mid-sweep W01 уже работал) или на known-good bisect Console; без полного Train W33.
3. DEBT-D2-silent-test остаётся **partial**; H3/H4 статусы без изменения.

---

*Docs 2026-10-22; ветка `timelearner_fix2`; G1 RERUN не запускался.*
