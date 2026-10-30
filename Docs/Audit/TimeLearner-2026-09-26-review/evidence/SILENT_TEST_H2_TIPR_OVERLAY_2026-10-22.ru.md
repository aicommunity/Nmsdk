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
| `LD_LIBRARY_PATH` | `/home/user/tl-agent/lib` → **glog 0.4.0** (pin; см. [`DEBT_17_GLOG_ABI_FIX_2026-10-22.ru.md`](DEBT_17_GLOG_ABI_FIX_2026-10-22.ru.md)) |
| Gate | `phase9_preinh_bc_gate.py --skip-tipr-mid --diagnostic-threshold <thr> --span-ms 50` |
| `candidate_mid` | `0.0024126668029073456` (из G1 Test `posttune_complete.flag`) |

| RUN_ID | Роль |
|--------|------|
| `H2.TipROverlay-17-20261022T090300Z` | первая серия: **rc=127** (`libglog.so.0` not found без `env.sh`) |
| `H2.TipROverlay-17-20261022T090800Z` | повтор с `env.sh` + glog **0.6**: все 6 вариантов **`fires=null`**, diagnostic **`rc=-6`** (`EmitToGlog` smash) |
| **`H2.TipROverlay-17-20261022T125500Z`** | **retry after glog 0.4 pin** — все 6 клеток с валидными `fires` (ниже) |

Корень артефактов retry: `/media/user/Data/TLAgent-20261020/runs/H2.TipROverlay-17-20261022T125500Z/` (`h2_tipr_overlay_summary.json`, `*.result.json`, `*.gate.out`).

---

## Матрица TipR × порог (T090800Z — abort, для истории)

| TipR overlay | Порог | Факт |
|--------------|-------|------|
| все 6 клеток | thr=1 / candidate_mid | **не измерено** — `fires=null`, `rc=-6` |

---

## Retry after glog pin (`T125500Z`)

После pin Elder-matched **glog 0.4** в `~/tl-agent/lib/` (DEBT-17) та же матрица на том же frozen W01 и Console `4a0658f3…` дала валидные байты `fires`. Stack smash **не** воспроизводился. После CSV Console по-прежнему получает SIGTERM (`gate_rc=-15` в хвосте phase9) — известный TRACE hang; метрики `fires`/`acc` из CSV валидны (`gate_rc=0` в result.json).

| TipR overlay | Порог | Ожидание H2 | **Факт (measured)** |
|--------------|-------|-------------|---------------------|
| **baseline_flat** `86M×4` | thr=1 | silent `00000000` (G1) | **`00000000`**, Acc 7/8, mode=silent |
| **baseline_flat** `86M×4` | candidate_mid | `01000101` (offline W01) | **`01000101`**, Acc 4/8, mode=miss_target |
| **midband_20m** `20M×3+86M` | thr=1 | fires≠0 при H2 | **`00000000`**, Acc 7/8, silent |
| **midband_20m** `20M×3+86M` | candidate_mid | сравнить с baseline | **`01000101`**, Acc 4/8 (как baseline) |
| **keep_snap_2p88m** `~2.88M×3+86M` | thr=1 | KeepDone-геометрия чинит thr=1 | **`00000000`**, Acc 7/8, silent |
| **keep_snap_2p88m** | candidate_mid | сравнить с baseline | **`01000101`**, Acc 4/8 (как baseline) |

Во всех шести клетках `target_hit=0`. TipR overlay **не** меняет байт fires относительно baseline на том же L W01: thr=1 остаётся silent, `candidate_mid` даёт тот же partial pattern `01000101`.

---

## Вердикт H2

**H2 ослаблена / не подтверждена на оси TipR overlay (frozen W01).** Гипотеза «midband / keep-snapshot vs CanonRmin flatten восстанавливает fires на thr=1» **не выполняется** на Classic×N0 Span50 AsymRm gen при фиксированном L из G1: все три TipR-профиля при thr=1 дают `fires=00000000`, а при `candidate_mid` — идентичный `01000101`. Это согласуется с offline W13/W33 ([`SILENT_TEST_W13_W33_MID_2026-10-22.ru.md`](SILENT_TEST_W13_W33_MID_2026-10-22.ru.md)): midband TipR **20M×3+86M** не снимает silent при thr=1.

Инфраструктурный блокер **DEBT-17-console-glog** закрыт pin’ом glog 0.4 ([`DEBT_17_GLOG_ABI_FIX_2026-10-22.ru.md`](DEBT_17_GLOG_ABI_FIX_2026-10-22.ru.md)). **DEBT-D2-silent-test** остаётся **partial** (silent thr=1 + H3 mid-policy); KeepDone cold W33 по-прежнему не измерен после pin (отдельный шаг).

---

## Next

1. KeepDone cold W33 на `.17` с glog 0.4 (если нужен полный TipR-mode путь) — без G1 RERUN.
2. DEBT-D2: опираться на H3 (`candidate_mid` / flag) и H1-weak; не ждать TipR overlay thr=1 fires на flat L W01.
3. SPEC/Controller: не фиксировать KeepDone как «чинит silent thr=1» без новых измерений.

---

*Docs 2026-10-22; ветка `timelearner_fix2`; G1 RERUN не запускался.*
