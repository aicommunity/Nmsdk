# F4 / F6-floor cold W01 Classic×N1 (Console `8dac9680…`)

Постановка: после сборки PulseLib `agent/tl-audit-f2-f3`@`696f6d7` + Bin whitelist/`774704fc` проверить cold converge `UseRelativeAmpEps=1` (F4) и `PreferConfiguredResistanceMinFloor=1` (F6-floor) на том же кейсе, что F2/F6mid — `W01_CL50_N1_PSIoff`, PostTune OFF, Host `.11`.

Trainer×Mode: Classic×N1. Span 50 мс. NeuronModel AsymRm.  
Train/Test: `TimeLearnerMatrix/W01/inputs/W01_CL50_N1_PSIoff/{Train,Test}` + attempt overlays.

| ID | flags | RUN_ID | training_convergence | L | TipSynapseResistance | Test/gate |
|---|---|---|---|---|---|---|
| F6.mid (prev) | DisableMidbandWalk | F6.mid-11-…9113 | converged_need0 | 25 22 15 1 | @Rmin (86 М×4) | silent/hang −15 |
| **F4.rel** | UseRelativeAmpEps=1 | F4.rel-11-…4599 | **converged_need0** | **25 22 15 1** | **2.88 М×3 + 86 М** (`tipr_class=other`) | gate_rc=1, child_rc=−15 |
| **F6.floor** | PreferConfiguredResistanceMinFloor=1 | F6.floor-11-…8682 | **converged_need0** | **25 22 15 1** | **та же** 2.88 М×3 + 86 М | gate_rc=1, child_rc=−15 |

Overlays подтверждены в `runtime_input_overrides.json` (`train_params` + XML sha change). Console sha256 `8dac9680becd543a…`.

## Выводы

Оба флага **не ломают** Need=0 на той же L-геометрии, что E1/F2/F6mid. В отличие от F6.mid (TipR все @Rmin), F4 и F6-floor оставили три tip-синапса около **2.88 МОм** и один на 86 МОм — `tipr_class=other` vs expect=canon; это отличие TipR-оси, не отказ train. Gate/Test hang (−15) — прежний DEBT silent-Test, не регрессия F4/F6. Следующий шаг: F5 gamma; silent-Test; E2 R8 до SERIES_DONE.
