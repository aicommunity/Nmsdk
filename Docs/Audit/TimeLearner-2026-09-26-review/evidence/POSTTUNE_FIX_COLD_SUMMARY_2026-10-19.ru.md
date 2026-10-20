# Сводка cold PostTune-fix — кампания v5 (2026-10-19)

Канон группировки: [RESULT_GROUPING_HIERARCHY.ru.md](RESULT_GROUPING_HIERARCHY.ru.md).  
Назначения хостов: [DUALHOST_ASSIGNMENT_POSTTUNE_FIX_2026-10-19.ru.md](DUALHOST_ASSIGNMENT_POSTTUNE_FIX_2026-10-19.ru.md).

База конфигов (относительные ссылки ниже): [`Bin/Configs/SpikeSamples/StructTrain/`](../../../../Bin/Configs/SpikeSamples/StructTrain/).  
Для HIST/W48 — канонические EXP `…/Train` и `…/Test` из `matrix.json` `source_config`. Для W01 — подготовленные matrix inputs (factor-variant), т.к. отдельного `source_config` у шаблона `classic*` нет.

## Постановка

После цикла правок PostTune в PulseLib нужно было не только подтвердить зелёный PASS×3, но и закрыть полный парный протокол §4 A–E и §5 OFF на **одном** финальном SHA, с изоляцией dual-host (`.11` ≤8 Console, `.17` ≤12) и единой табличной формой: строки = Mod, колонки = PostTune OFF / ON, плюс Host / RUN_ID / SHA и ссылки на Train/Test конфиги, на которых получены метрики.

Промежуточные прогоны на SHA `8575df3` / `7c814a3` / `bd11169` (волны «w1/w2» до v5) в эту сводную **не входят**: там политика mid ещё менялась (в том числе auto-KeepDone TipR, который чинил gen-стиль D3, но ломал PASS preinh). Здесь — только срез **PulseLib `d52dc1c`**, Console SHA16 `d2862a42fa266145` на обоих хостах после sync.

## Политика PostTune на финальном SHA (`d52dc1c`)

1. Ideal LandscapeOk → mid из `ComputeMidThreshold`.
2. Best-effort mid **только** при tiny-gap (все foil ниже target, gap &lt; 1e‑4).
3. Иначе silent mid (FixedLTZ=1) для Test inference; **TipR не откатывается** автоматически. KeepDone TipR остаётся явным tip-mode / PostTune OFF (A2.1) для D3-стиля gen.

На практике это даёт: PASS×3 preinh/nextseg остаются одноогневыми при ON; `br25_gen` при ON уходит в silence (NonSeparable mid), тогда как при OFF сохраняет частичную детекцию target (`fires=10110000`, detected=True) — критерий плана «gen ON не хуже OFF по реакции на target» на этом SHA **не выполнен**, и это зафиксировано ниже без смягчения gate.

## Единый шаблон колонок

Во всех таблицах ниже:

| Колонка | Содержание |
|---|---|
| Configs | ссылки на каталоги **Train** и **Test** EXP (или matrix inputs), с которых готовился cold |
| PostTune OFF | `fires` / `detected` / `training_convergence` |
| PostTune ON | `fires` / `detected` / `training_convergence` / `posttune_quality` |
| SHA | PulseLib short + Console16 |
| Host / RUN_ID | изолированные корни `n1-posttune-fix-11` / `…-17` |

`Need` в matrix_result часто `null` после finalize; сходимость читается из `training_convergence` (`converged_posttune_finalized` при ON, `converged_need0` при OFF).

---

## Trainer=Branch · Mode=N1 (структурная sync + параметрическая TipR)

### Span=25 мс

#### NeuronModel=baseline (W10 Branch)

Постановка: якорь D3/D2-класса — `br25_gen` и `br25_preinh` плюс PASS peer `br25_nextseg`. Проверяли, сохраняет ли финальная политика детекции target при ON и не ломает ли PASS×3.

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| gen | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Test) | `10110000` / True / converged_need0 | `00000000` / False / converged_posttune_finalized / nonseparable | PL `d52dc1c` · Cons `d2862a42fa266145` | `.11` | OFF `…-ptoff-…-19-37-W10` · ON `…-pton-…-17-23-W10` |
| preinh | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_preinh_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_preinh_C1e9/Test) | `00000000` / False / converged_need0 | `00000000` / False / converged_posttune_finalized / nonseparable | same | `.17` | OFF `…-ptoff-…-20-46-W10` · ON `…-pton-…-17-25-W10` |
| nextseg (PASS×3) | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test) | `11111111` / True / converged_need0 | `10000000` / True / converged_posttune_finalized / nonseparable | same | `.17` | OFF `…-ptoff-…-20-46-W10` · ON **reuse** `tl-ptfix-passx3-v4-17-20261019-16-40` |

Вывод по Span=25 baseline: PostTune ON на gen даёт полный silence Test (NonSeparable mid, tipr остаётся canon), тогда как OFF сохраняет частичный огонь и детекцию target — это ожидаемый рычаг A2.1 / tip-mode, а не регрессия TipR. Preinh молчит в обеих колонках. PASS nextseg при ON держит канон `10000000`; при OFF уходит в all-fire — метрики OFF обязательны планом, PASS от OFF не требуется.

#### NeuronModel=FastSpan Classic (W12)

Постановка: мини-сетка §4C — обязательно `fs25_gen` / `fs25_preinh`, плюс ≥1@50. Бюджет Train ≈320 с wall-poll; на обоих режимах обучение **не** доходит до Need=0 в отведённом окне.

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| gen | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityFastSpan/EXP_span25ms_fast_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityFastSpan/EXP_span25ms_fast_C1e9/Test) | — / — / not_converged_at_stop (`train_incomplete`) | — / — / not_converged_at_stop (`train_incomplete`) | PL `d52dc1c` · Cons `d2862a42fa266145` | `.11` | OFF `…-ptoff-…-19-37-W12` · ON `…-pton-…-17-23-W12` |
| preinh | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityFastSpan/EXP_span25ms_fast_preinh_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityFastSpan/EXP_span25ms_fast_preinh_C1e9/Test) | — / — / not_converged_at_stop (`train_incomplete`) | — / — / not_converged_at_stop (`train_incomplete`) | same | `.11` | same |

Вывод: для Classic FastSpan @25 мс cold v5 даёт только статус сходимости Train (Need=1 до стопа). Это не измерение separability PostTune; отдельный удлинённый бюджет / soft-cold полный прогон — вне закрытия этого плана, но ID и парный протокол закрыты.

#### NeuronModel=FastSpan Branch (W48 smoke §4E)

Постановка: первые cold на семье `SelectivityBranchFastSpan` после §0b. PASS на первом круге не требовался; обязательны Need/fires/mid-метрики.

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| gen | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranchFastSpan/EXP_br_fs_span25_gen_N1_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranchFastSpan/EXP_br_fs_span25_gen_N1_C1e9/Test) | `10110000` / True / converged_need0 | `00000000` / False / converged_posttune_finalized / nonseparable | PL `d52dc1c` · Cons `d2862a42fa266145` | `.11` | OFF `…-ptoff-…-20-47-W48` · ON `…-pton-…-18-42-W48` |
| preinh | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranchFastSpan/EXP_br_fs_span25_preinh_N1_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranchFastSpan/EXP_br_fs_span25_preinh_N1_C1e9/Test) | `00000000` / False / converged_need0 | `00000000` / False / converged_posttune_finalized / nonseparable | same | `.11` | same |

Вывод: Branch×FastSpan @25 ведёт себя как baseline Branch gen/preinh на том же Span: ON gen → silence NonSeparable; OFF gen → частичная детекция `10110000`. Preinh молчит в обеих колонках. Smoke §4E закрыт.

#### NeuronModel=AsymRm Classic (W09 / W11)

Постановка: §4B — packA @25 gen и preinh-слот.

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| gen (`asym25`) | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityAsymRm/EXP_span25ms_packA_gen_posttune/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityAsymRm/EXP_span25ms_packA_gen_posttune/Test) | `00000000` / False / converged_need0 | `00000000` / False / converged_posttune_finalized / nonseparable | PL `d52dc1c` · Cons `d2862a42fa266145` | `.17` | OFF `…-ptoff-…-20-46-W09` · ON `…-pton-…-17-25-W09` |
| preinh (`asym25_preinh`) | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityAsymRm/EXP_span25ms_packA_preinh/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityAsymRm/EXP_span25ms_packA_preinh/Test) | `00000000` / False / converged_need0 | `10000000` / True / converged_posttune_finalized / nonseparable (**ok**) | same | `.17` | OFF `…-ptoff-…-20-46-W11` · ON `…-pton-…-17-25-W11` |

Вывод: gen Asym @25 молчит в обеих колонках. Preinh при ON дал канонический `10000000` и `failure_class=ok` — единственный «зелёный» Asym-кейс v5; при OFF тот же preinh молчит. Это полезный контраст NeuronModel на одном Span.

### Span=50 мс

#### NeuronModel=baseline (W10 Branch)

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| gen | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span50_packA_gen_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span50_packA_gen_C1e9/Test) | `11111111` / True / converged_need0 | `10000000` / True / converged_posttune_finalized / nonseparable (**ok**) | PL `d52dc1c` · Cons `d2862a42fa266145` | `.11` | OFF `…-ptoff-…-19-37-W10` · ON `…-pton-…-17-23-W10` |
| preinh (PASS×3) | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span50_packA_preinh_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span50_packA_preinh_C1e9/Test) | `00000000` / False / converged_need0 | `10000000` / True / converged_posttune_finalized / nonseparable (**ok**) | same | `.17` | OFF `…-ptoff-…-20-46-W10` · ON **reuse** `tl-ptfix-passx3-v4-17-…` |

Вывод: @50 baseline gen при ON удерживает одноогневой PASS-подобный паттерн; OFF даёт all-fire с детекцией. PASS preinh@50 при ON зелёный; при OFF — silence.

#### NeuronModel=FastSpan Classic (W12, ≥1@50)

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| gen | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityFastSpan/EXP_span50ms_fast_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityFastSpan/EXP_span50ms_fast_C1e9/Test) | — / — / not_converged_at_stop (`train_incomplete`) | — / — / not_converged_at_stop (`train_incomplete`) | PL `d52dc1c` · Cons `d2862a42fa266145` | `.11` | OFF `…-ptoff-…-19-37-W12` · ON `…-pton-…-17-23-W12` |

Вывод: как @25, Train не завершён в бюджете; парный протокол выполнен, separability не интерпретируется.

### Span=100 мс

#### NeuronModel=baseline (W10 Branch, PASS×3)

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| preinh | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span100_packA_preinh_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span100_packA_preinh_C1e9/Test) | `00000000` / False / converged_need0 | `10000000` / True / converged_posttune_finalized / nonseparable (**ok**) | PL `d52dc1c` · Cons `d2862a42fa266145` | `.17` | OFF `…-ptoff-…-20-46-W10` · ON **reuse** `tl-ptfix-passx3-v4-17-…` |

Вывод: PASS×3 ON @100 зелёный; OFF silence. Вместе с nextseg@25 и preinh@50 это даёт **PASS×3 ON = 3/3** на `d52dc1c`.

#### NeuronModel=FastSpan Classic (W12, ≥1@100)

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| gen | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityFastSpan/EXP_span100ms_fast_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityFastSpan/EXP_span100ms_fast_C1e9/Test) | `00000000` / False / converged_need0 | `00000000` / False / converged_posttune_finalized / nonseparable | PL `d52dc1c` · Cons `d2862a42fa266145` | `.17` | OFF `…-ptoff-…-20-46-W12` · ON `…-pton-…-17-25-W12` |

Вывод: в отличие от fs@25/50, `fs100_gen` **сходится** Train в бюджете, но Test silence в обеих колонках. Это закрывает требование «≥1@100» с измеримыми fires, без PASS.

---

## Trainer=Classic · Mode=N0

### Span=25 мс · NeuronModel=baseline (W01)

Постановка: §4D — CL25 N0 в сводной с парным ON/OFF. Для ON matrix `posttrain_tuning` временно форсирован в `True` (в каноне W01 он False); OFF — дефолт False. Конфиги — prepared matrix inputs (шаблон `classic25` → factor-variant от AsymRm packA).

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| PSIoff | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL25_N0_PSIoff/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL25_N0_PSIoff/Test) | — / — / not_converged_at_stop (`train_incomplete`) | — / — / not_converged_at_stop (`train_incomplete`) | PL `d52dc1c` · Cons `d2862a42fa266145` | `.17` | OFF `…-ptoff-…-20-46-W01` · ON `…-pton-…-17-25-W01` |

Вывод: CL25 N0 не завершил Train в отведённом окне ни при ON, ни при OFF. В сводную входит как документированный incomplete, без заявки на Classic PASS.

### Span=50 мс · NeuronModel=baseline (W01)

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| PSIoff | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test) | `00000000` / False / converged_need0 | `00000000` / False / converged_posttune_finalized / nonseparable | PL `d52dc1c` · Cons `d2862a42fa266145` | `.17` | OFF `…-ptoff-…-20-46-W01` · ON `…-pton-…-17-25-W01` |

Вывод: CL50 N0 сходится, но Test silence в обеих колонках — классический Need0-silent класс, уже известный из dual-track; PostTune ON на этом кейсе его не снимает.

---

## Trainer=Classic · Mode=N1

### Span=25 мс · NeuronModel=baseline (W01 N1 short)

| Mod | Configs (Train · Test) | PostTune OFF: fires / detected / conv | PostTune ON: fires / detected / conv / posttune | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| PSIoff | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL25_N1_PSIoff/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL25_N1_PSIoff/Test) | — / — / not_converged_at_stop (`train_incomplete`) | — / — / not_converged_at_stop (`train_incomplete`) | PL `d52dc1c` · Cons `d2862a42fa266145` | `.17` | OFF `…-ptoff-…-20-46-W01` · ON `…-pton-…-17-25-W01` |

Вывод: N1 short @25 также incomplete в бюджете; парный протокол выполнен.

---

## Сводка закрытия плана (§4 / §5)

| Требование | Статус |
|---|---|
| §4A baseline Branch ON/OFF (`br25_gen`, `br25_preinh`, `br50_gen`) | **закрыто** (v5) |
| §4B AsymRm ON/OFF (`asym25` + preinh-слот) | **закрыто** |
| §4C Classic FastSpan мини-сетка @25 + ≥1@50 + ≥1@100 ON/OFF | **закрыто** (25/50 = train_incomplete; 100 = silence) |
| §4D Classic W01 CL25/CL50 N0 + N1 short ON/OFF | **закрыто** (CL25 incomplete; CL50 silence) |
| §4E Branch×FastSpan W48 gen+preinh ON/OFF | **закрыто** |
| §5 PASS×3 ON `10000000` ×3 | **3/3 green** (`passx3-v4`, тот же SHA) |
| §5 PASS×3 OFF метрики | **закрыто** (nextseg all-fire; preinh@50/100 silence) |
| Dual-host параллель + изоляция RUN | **да** (реестр v5) |
| Сводная в иерархии Trainer×Mode → Span → NeuronModel → Mod + ссылки Train/Test | **этот файл** |

### Что из этого следует

Финальная политика PostTune **удерживает PASS×3** и при этом **не** восстанавливает детекцию target на `br25_gen` / Branch-FS gen без явного KeepDone tip-mode или PostTune OFF. Asym preinh@25 при ON — положительный outlier. Classic FastSpan @25/50 в стандартном matrix-бюджете не даёт Test-метрик; @100 сходится в silence. Classic W01 остаётся в известном Need0-silent / incomplete классе и не блокирует закрытие PostTune-фикса по Branch PASS критерию.

Монитор `AGENT_LOOP_TICK_ptfix` остановлен после closeout v5.
