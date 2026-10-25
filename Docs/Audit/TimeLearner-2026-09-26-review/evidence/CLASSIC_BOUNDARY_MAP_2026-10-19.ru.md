# Classic Boundary Map (Trainer=Classic, без Branch)

Дата: 2026-10-19.  
**Trainer:** `Classic` = `NNeuronTimeLearner` (не `NNeuronTimeLearnerBranch`).  
**Track:** `CL`.  
Не смешивать строки этой карты с Branch PASS×3 / M1_BOUNDARY_MAP.  
Канон группировки: [RESULT_GROUPING_HIERARCHY.ru.md](RESULT_GROUPING_HIERARCHY.ru.md).

Маркировка: см. [POST_P0_SYNTHESIS…](../POST_P0_SYNTHESIS_AND_NEXT_CYCLE_2026-10-19.ru.md) §0.

---

## 0. Сводка по иерархии Trainer×Mode → Span → NeuronModel

### Trainer=Classic · Mode=N0 · NeuronModel=baseline W01

| Span | Mod | Cold N+1 / HIST | Ярлык |
|---|---|---|---|
| 25 мс | PSIoff | Need=1 incomplete (`tl-cl-n1-w01-…`) | `CL-stall-short` |
| 50 мс | PSIoff | Need=0 fires=`00000000` NonSeparable | `CL-Need0-silent` |
| 50 мс Step=86 МОм | PSIoff | Need=1 (HIST) | `CL-incomplete-step86` |

### Trainer=Classic · Mode=N1 · NeuronModel=baseline W01

| Span | Mod | Итог | Ярлык |
|---|---|---|---|
| short N1 | — | broken path; вне мини-набора N+1 | `CL-N1-stall` |

NeuronModel AsymRm / FastSpan Classic — отдельные семьи в матрице; в N+1 cold не входили.

---

## 1. Исторический срез (до цикла N+1)

| Case (логическое) | Span / Mode | Исторический итог | Ярлык |
|---|---|---|---|
| W01 Classic 50 мс N0 Step≈1 ГОм | CL50 / N0 | Need=0 (часто BE @N=128); Test NonSeparable / target silent; Acc≈7/8 FP=0 | `CL-Need0-silent` |
| W01 Classic 50 мс N0 + step-down fix | CL50 / N0 | Need=0 после N=99→98; Test NonSeparable | `CL-Need0-silent` |
| W01 Classic 50 мс N0 Step=86 МОм | CL50 / N0 | Need=1, Test не запускался | `CL-incomplete-step86` |
| W01 Classic 25 мс N0 | CL25 / N0 | amp/sync stall в коротком бюджете | `CL-stall-short` |
| W01 Classic N1 | N1 | peak/TipR blow-up, нет роста N — **broken path** | `CL-N1-stall` |

Ссылки: [STATUS…](../STATUS.ru.md) (блок Classic W01), [W01_DIAGNOSIS…](metrics/W01_DIAGNOSIS_20261011.md), diagnostics `w01_classic_structural_2026-10-16`.

---

## 2. Мини-набор цикла N+1 (план cold)

Хост: `.17`, лимит ≤12 Console (вместе с BR-M1 A).  
`RUNS_ROOT`: `…/TimeLearnerMatrixRuns/n1-classic-w01/`  
`run_id` префикс: `tl-cl-*`.

| # | Case | Цель | В скоупе |
|---|---|---|---|
| CL1 | W01 Classic **50 мс / N0** | Повтор Need=0 + классификация качества на SHA `20c3e22` | да |
| CL2 | W01 Classic **25 мс / N0** | Stall vs Need=0 на текущем коде | да |
| CL3 | W01 Classic **50 мс / N0 Step=86 МОм** | Need=1 vs прогресс | опционально (слоты) |
| — | Classic **N1** | — | **нет** (отдельный diagnostic позже) |

Результаты cold — только сюда и в блок Classic STATUS; **не** в Branch PASS-таблицы.

---

## 3. Результаты cold N+1

`RUN_ID=tl-cl-n1-w01-20261019-10-04` · PL `20c3e22` · Host `.17`

| Run ID | Case | Host | Need | convergence | quality / fires | Ярлык | Notes |
|---|---|---|---|---|---|---|---|
| `tl-cl-n1-w01-…10-04` | `W01_CL25_N0_PSIoff` | `.17` | 1 | `not_converged_at_stop` | Test не оценён | `CL-stall-short` | L=`[14,12,1,1]` TipR flat 86 МОм |
| `tl-cl-n1-w01-…10-04` | `W01_CL50_N0_PSIoff` | `.17` | 0 | `converged_need0` | fires=`00000000` quality_fail | `CL-Need0-silent` | L=`[27,22,15,1]` TipR flat 86 МОм; `mid_source=cpp_nonseparable` |

Повторяет исторический паттерн: @50 мс структура сходится, Test silent/NonSeparable; @25 мс — incomplete.

---

## 4. Отличие от Branch

| | Classic (`CL`) | Branch (`BR-M*`) |
|---|---|---|
| Класс | `NNeuronTimeLearner` | `NNeuronTimeLearnerBranch` |
| Пульсы / NextSeg / PreInh | нет Branch-протоколов | nextseg / preinh / gen |
| Seg-order BE (BR-D7) | не применим без доказательства | Mode=0 early BE ∧ seg_ok |
| PASS-остров Post-P0 | нет (пока) | nextseg@25 + preinh@50/100 |

Ярлыки Classic (`CL-*`) **не** переименовывать в `D3`/`D7` без одинакового корневого механизма.
