# Classic/Branch InhGrid SoftCold — RESULTS (2026-10-24)

Постановка кампании: три механизма торможения (PSI/preinh, NextSeg \(d=+1\), SegEI \(d=8,\alpha=1\), SymInh) на неизменном Classic fan-out и на Branch one-dendrite; cold SoftCold PostTune ON. Evidence-план: [`CLASSIC_BRANCH_INH_PLAN_2026-10-23.ru.md`](CLASSIC_BRANCH_INH_PLAN_2026-10-23.ru.md). Launch TSV: [`INH_GRID_COLD_LAUNCH.tsv`](INH_GRID_COLD_LAUNCH.tsv).

**Host/SHA:** Classic = Elder-1 (локально); Branch = M40/`10.245.1.17`. Nmsdk `ac5a091d1`, PulseLib `40f09a2`, Bin `01baf8d4`. NeuronModel во всех строках: `NSPNeuronGenSymInhC1e9` (не AsymRm/FastSpan).

**Счётчик Done:** Classic 48/48, Branch 24/24. Это закрытие очереди cold, **не** эквивалент Acc PASS.

**Вывод по качеству (после Diag 2026-10-24):** disk_stop-хвост закрыт re-run; научный разбор Acc/Need/mid — [`INH_GRID_SOFTCOLD_DIAG_2026-10-24.ru.md`](INH_GRID_SOFTCOLD_DIAG_2026-10-24.ru.md), harvest [`INH_GRID_DIAG_HARVEST_2026-10-24.tsv`](INH_GRID_DIAG_HARVEST_2026-10-24.tsv). **SoftCold PASS = 0/72:** у всех `converged_posttune_finalized` fires=`00000000`, Acc≈7/8, mid=`cpp_nonseparable`, Цель=нет; 34 кейса — `not_converged_at_stop` (Test не считался). Done≠Acc PASS.

---

## Classic × Mode → Span → Mod (PostTune ON)

### Classic × N0

#### Span 25 мс

| Mod | NeuronModel | TSV | Log reason | RUN_ID | Train | Test |
| --- | --- | --- | --- | --- | --- | --- |
| `gen` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `verify_done` | `INH.inh_c25_gen_n0_pton-Elder-1_-20261023T2136Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_gen_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_gen_InhGrid_N0/Test) |
| `preinh` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `verify_done` | `INH.inh_c25_preinh_n0_pton-Elder-1_-20261023T2140Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_InhGrid_N0/Test) |
| `nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `verify_done` | `INH.inh_c25_nextseg_n0_pton-Elder-1_-20261023T2138Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_nextseg_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_nextseg_InhGrid_N0/Test) |
| `segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c25_segei_n0_pton-Elder-1_-20261023T2219Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_segei_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_segei_InhGrid_N0/Test) |
| `preinh_nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c25_preinh_nextseg_n0_pton-Elder-1_-20261023T2217Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_nextseg_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_nextseg_InhGrid_N0/Test) |
| `preinh_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c25_preinh_segei_n0_pton-Elder-1_-20261023T2218Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_segei_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_segei_InhGrid_N0/Test) |
| `nextseg_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `verify_done` | `INH.inh_c25_nextseg_segei_n0_pton-Elder-1_-20261023T2139Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_nextseg_segei_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_nextseg_segei_InhGrid_N0/Test) |
| `all` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c25_all_n0_pton-Elder-1_-20261023T2135Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_all_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_all_InhGrid_N0/Test) |

#### Span 50 мс

| Mod | NeuronModel | TSV | Log reason | RUN_ID | Train | Test |
| --- | --- | --- | --- | --- | --- | --- |
| `gen` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_gen_n0_pton-Elder-1_-20261023T2222Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_gen_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_gen_InhGrid_N0/Test) |
| `preinh` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_preinh_n0_pton-Elder-1_-20261023T2227Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_InhGrid_N0/Test) |
| `nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_nextseg_n0_pton-Elder-1_-20261023T2224Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_nextseg_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_nextseg_InhGrid_N0/Test) |
| `segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_segei_n0_pton-Elder-1_-20261023T2231Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_segei_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_segei_InhGrid_N0/Test) |
| `preinh_nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_preinh_nextseg_n0_pton-Elder-1_-20261023T2228Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_nextseg_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_nextseg_InhGrid_N0/Test) |
| `preinh_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_preinh_segei_n0_pton-Elder-1_-20261023T2229Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_segei_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_segei_InhGrid_N0/Test) |
| `nextseg_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_nextseg_segei_n0_pton-Elder-1_-20261023T2225Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_nextseg_segei_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_nextseg_segei_InhGrid_N0/Test) |
| `all` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_all_n0_pton-Elder-1_-20261023T2220Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_all_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_all_InhGrid_N0/Test) |

#### Span 100 мс

| Mod | NeuronModel | TSV | Log reason | RUN_ID | Train | Test |
| --- | --- | --- | --- | --- | --- | --- |
| `gen` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_gen_n0_pton-Elder-1_-20261023T1443Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_gen_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_gen_InhGrid_N0/Test) |
| `preinh` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_preinh_n0_pton-Elder-1_-20261023T1809Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_InhGrid_N0/Test) |
| `nextseg` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_nextseg_n0_pton-Elder-1_-20261023T1445Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_nextseg_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_nextseg_InhGrid_N0/Test) |
| `segei` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_segei_n0_pton-Elder-1_-20261023T1814Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_segei_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_segei_InhGrid_N0/Test) |
| `preinh_nextseg` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_preinh_nextseg_n0_pton-Elder-1_-20261023T1811Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_nextseg_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_nextseg_InhGrid_N0/Test) |
| `preinh_segei` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_preinh_segei_n0_pton-Elder-1_-20261023T1812Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_segei_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_segei_InhGrid_N0/Test) |
| `nextseg_segei` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_nextseg_segei_n0_pton-Elder-1_-20261023T1448Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_nextseg_segei_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_nextseg_segei_InhGrid_N0/Test) |
| `all` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_all_n0_pton-Elder-1_-20261023T1442Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_all_InhGrid_N0/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_all_InhGrid_N0/Test) |

### Classic × N1

#### Span 25 мс

| Mod | NeuronModel | TSV | Log reason | RUN_ID | Train | Test |
| --- | --- | --- | --- | --- | --- | --- |
| `gen` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `verify_done` | `INH.inh_c25_gen_n1_pton-Elder-1_-20261023T2137Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_gen_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_gen_InhGrid_N1/Test) |
| `preinh` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `verify_done` | `INH.inh_c25_preinh_n1_pton-Elder-1_-20261023T2152Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_InhGrid_N1/Test) |
| `nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `verify_done` | `INH.inh_c25_nextseg_n1_pton-Elder-1_-20261023T2138Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_nextseg_InhGrid_N1/Test) |
| `segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c25_segei_n1_pton-Elder-1_-20261023T2220Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_segei_InhGrid_N1/Test) |
| `preinh_nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c25_preinh_nextseg_n1_pton-Elder-1_-20261023T2217Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_nextseg_InhGrid_N1/Test) |
| `preinh_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c25_preinh_segei_n1_pton-Elder-1_-20261023T2218Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_preinh_segei_InhGrid_N1/Test) |
| `nextseg_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `verify_done` | `INH.inh_c25_nextseg_segei_n1_pton-Elder-1_-20261023T2139Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_nextseg_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_nextseg_segei_InhGrid_N1/Test) |
| `all` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c25_all_n1_pton-Elder-1_-20261023T2136Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_all_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S25_all_InhGrid_N1/Test) |

#### Span 50 мс

| Mod | NeuronModel | TSV | Log reason | RUN_ID | Train | Test |
| --- | --- | --- | --- | --- | --- | --- |
| `gen` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_gen_n1_pton-Elder-1_-20261023T2223Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_gen_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_gen_InhGrid_N1/Test) |
| `preinh` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_preinh_n1_pton-Elder-1_-20261023T2228Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_InhGrid_N1/Test) |
| `nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_nextseg_n1_pton-Elder-1_-20261023T2224Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_nextseg_InhGrid_N1/Test) |
| `segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_segei_n1_pton-Elder-1_-20261023T2231Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_segei_InhGrid_N1/Test) |
| `preinh_nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_preinh_nextseg_n1_pton-Elder-1_-20261023T2229Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_nextseg_InhGrid_N1/Test) |
| `preinh_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_preinh_segei_n1_pton-Elder-1_-20261023T2230Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_preinh_segei_InhGrid_N1/Test) |
| `nextseg_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_nextseg_segei_n1_pton-Elder-1_-20261023T2226Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_nextseg_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_nextseg_segei_InhGrid_N1/Test) |
| `all` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `disk_stop_<80G` | `INH.inh_c50_all_n1_pton-Elder-1_-20261023T2221Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_all_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S50_all_InhGrid_N1/Test) |

#### Span 100 мс

| Mod | NeuronModel | TSV | Log reason | RUN_ID | Train | Test |
| --- | --- | --- | --- | --- | --- | --- |
| `gen` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_gen_n1_pton-Elder-1_-20261023T1444Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_gen_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_gen_InhGrid_N1/Test) |
| `preinh` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_preinh_n1_pton-Elder-1_-20261023T1810Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_InhGrid_N1/Test) |
| `nextseg` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_nextseg_n1_pton-Elder-1_-20261023T1446Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_nextseg_InhGrid_N1/Test) |
| `segei` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_segei_n1_pton-Elder-1_-20261023T1829Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_segei_InhGrid_N1/Test) |
| `preinh_nextseg` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_preinh_nextseg_n1_pton-Elder-1_-20261023T1812Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_nextseg_InhGrid_N1/Test) |
| `preinh_segei` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_preinh_segei_n1_pton-Elder-1_-20261023T1813Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_preinh_segei_InhGrid_N1/Test) |
| `nextseg_segei` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_nextseg_segei_n1_pton-Elder-1_-20261023T1503Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_nextseg_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_nextseg_segei_InhGrid_N1/Test) |
| `all` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `not_converged` | `INH.inh_c100_all_n1_pton-Elder-1_-20261023T1442Z-3267637` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_all_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S100_all_InhGrid_N1/Test) |

## Branch × N1 → Span → Mod (PostTune ON)

Branch×N0 в этой волне не входил в Done-сетку.

### Branch × N1 · Span 25 мс

| Mod | NeuronModel | TSV note | RUN_ID | Train | Test |
| --- | --- | --- | --- | --- | --- |
| `gen` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b25_gen_n1_pton-M40_-20261023T1733Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_gen_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_gen_InhGrid_N1/Test) |
| `preinh` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b25_preinh_n1_pton-M40_-20261023T1758Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_preinh_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_preinh_InhGrid_N1/Test) |
| `nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b25_nextseg_n1_pton-M40_-20261023T1733Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_nextseg_InhGrid_N1/Test) |
| `segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b25_segei_n1_pton-M40_-20261023T1800Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_segei_InhGrid_N1/Test) |
| `preinh_nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b25_preinh_nextseg_n1_pton-M40_-20261023T1759Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_preinh_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_preinh_nextseg_InhGrid_N1/Test) |
| `preinh_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b25_preinh_segei_n1_pton-M40_-20261023T1800Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_preinh_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_preinh_segei_InhGrid_N1/Test) |
| `nextseg_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b25_nextseg_segei_n1_pton-M40_-20261023T1734Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_nextseg_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_nextseg_segei_InhGrid_N1/Test) |
| `all` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b25_all_n1_pton-M40_-20261023T1732Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_all_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S25_all_InhGrid_N1/Test) |

### Branch × N1 · Span 50 мс

| Mod | NeuronModel | TSV note | RUN_ID | Train | Test |
| --- | --- | --- | --- | --- | --- |
| `gen` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b50_gen_n1_pton-M40_-20261023T1802Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_gen_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_gen_InhGrid_N1/Test) |
| `preinh` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b50_preinh_n1_pton-M40_-20261023T1805Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_preinh_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_preinh_InhGrid_N1/Test) |
| `nextseg` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `INH.inh_b50_nextseg_n1_pton-M40_-20261023T1802Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_nextseg_InhGrid_N1/Test) |
| `segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b50_segei_n1_pton-M40_-20261023T1811Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_segei_InhGrid_N1/Test) |
| `preinh_nextseg` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `INH.inh_b50_preinh_nextseg_n1_pton-M40_-20261023T1806Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_preinh_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_preinh_nextseg_InhGrid_N1/Test) |
| `preinh_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b50_preinh_segei_n1_pton-M40_-20261023T1809Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_preinh_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_preinh_segei_InhGrid_N1/Test) |
| `nextseg_segei` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `INH.inh_b50_nextseg_segei_n1_pton-M40_-20261023T1803Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_nextseg_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_nextseg_segei_InhGrid_N1/Test) |
| `all` | `NSPNeuronGenSymInhC1e9` | `not_converged` | `INH.inh_b50_all_n1_pton-M40_-20261023T1801Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_all_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S50_all_InhGrid_N1/Test) |

### Branch × N1 · Span 100 мс

| Mod | NeuronModel | TSV note | RUN_ID | Train | Test |
| --- | --- | --- | --- | --- | --- |
| `gen` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b100_gen_n1_pton-M40_-20261023T1728Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_gen_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_gen_InhGrid_N1/Test) |
| `preinh` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b100_preinh_n1_pton-M40_-20261023T1730Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_preinh_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_preinh_InhGrid_N1/Test) |
| `nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b100_nextseg_n1_pton-M40_-20261023T1728Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_nextseg_InhGrid_N1/Test) |
| `segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b100_segei_n1_pton-M40_-20261023T1731Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_segei_InhGrid_N1/Test) |
| `preinh_nextseg` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b100_preinh_nextseg_n1_pton-M40_-20261023T1730Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_preinh_nextseg_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_preinh_nextseg_InhGrid_N1/Test) |
| `preinh_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b100_preinh_segei_n1_pton-M40_-20261023T1731Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_preinh_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_preinh_segei_InhGrid_N1/Test) |
| `nextseg_segei` | `NSPNeuronGenSymInhC1e9` | `exit_1` | `INH.inh_b100_nextseg_segei_n1_pton-M40_-20261023T1729Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_nextseg_segei_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_nextseg_segei_InhGrid_N1/Test) |
| `all` | `NSPNeuronGenSymInhC1e9` | `exit_1_tsv_fix` | `INH.inh_b100_all_n1_pton-M40_-20261023T1727Z-3207187` | [`Train`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_all_InhGrid_N1/Train) | [`Test`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_branch_S100_all_InhGrid_N1/Test) |

## Classic disk_stop хвост — закрыт re-run

Исходные 24 кейса с `disk_stop_<80G` переиграны (см. addendum ниже).

---

## Addendum: disk_stop re-run (2026-10-24)

Постановка: 24 Classic-кейса, ранее оборванные `STOP Avail<80G`, переиграны dual-host после offload (Elder-1 S25×8 LIMIT≤8, M40/`.17` S50×16 LIMIT≤12). SoftCold PostTune ON; NeuronModel `NSPNeuronGenSymInhC1e9`.

### Итог очереди re-run

| Host | Span | Done | Notes |
| --- | --- | --- | --- |
| Elder-1 | Classic S25 ×8 | **8/8** | все `exit_1` (полный verify; не disk_stop) |
| M40 | Classic S50 ×16 | **16/16** | 14×`not_converged`, 2×`exit_1` (`preinh_segei_n0`, `segei_n0`) |

**Вывод:** infra-хвост disk_stop закрыт. Acc PASS на этих Span не получен: S25 завершил verify с `exit_1`, S50 почти весь `not_converged` (в духе Classic S100 первой волны).

Конфиги: `Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S{25,50}_*_InhGrid_N{0,1}/{Train,Test}`.

---

## Addendum: Diag Acc/Need/mid (2026-10-24)

Постановка Diag — план §4. Ниже сжатая матрица по provenance (не TSV exit-кодам). Полный разбор и root-cause not_converged — в DIAG.

### Classic (PostTune ON) — Acc / Need / mid

| Mode | Span | Mod (все 8, если не указано) | Conv | Need | fires | Acc | mid | Train/Test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N0+N1 | 25 | все | finalized | 0 | `00000000` | 7/8 | `cpp_nonseparable` | [`SelectivityInhGrid/EXP_classic_S25_*`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/) |
| N0 | 50 | `segei`, `preinh_segei` | finalized | 0 | `00000000` | 7/8 | `cpp_nonseparable` | `EXP_classic_S50_{segei,preinh_segei}_InhGrid_N0` |
| N0+N1 | 50 | остальные 14 | not_converged | 1 | — | — | missing | `EXP_classic_S50_*` |
| N0+N1 | 100 | все | not_converged | 1 | — | — | missing | `EXP_classic_S100_*` |

### Branch × N1 (PostTune ON)

| Span | Conv OK Mods | not_conv Mods | fires@conv | Acc | mid |
| --- | --- | --- | --- | --- | --- |
| 25 | все 8 | — | `00000000` | 7/8 | `cpp_nonseparable` |
| 50 | `gen`,`preinh`,`segei`,`preinh_segei` | `nextseg`,`preinh_nextseg`,`nextseg_segei`,`all` | `00000000` | 7/8 | `cpp_nonseparable` / missing |
| 100 | все 8 | — | `00000000` | 7/8 | `cpp_nonseparable` |

Train/Test: [`EXP_branch_S{25,50,100}_*_InhGrid_N1`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/).

**Итог addendum:** ни Classic, ни Branch не дали Цель=да; Branch сходится на S100, Classic — нет; единственный «плюс» SegEI на Classic — чаще дойти до finalize на S50 N0, без улучшения fires.

