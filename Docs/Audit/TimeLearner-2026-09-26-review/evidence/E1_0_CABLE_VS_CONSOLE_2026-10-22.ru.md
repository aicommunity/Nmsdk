# E1.0 — модель кабеля vs Console (одиночный EPSP)

Постановка: сверить офлайн-модель `plans/AGENT_PLAN_2026-10-20/tools/cable_model` с NeuroModelerConsole по одиночному импульсу на соме для длин дендрита **L ∈ {1, 4, 10, 25, 50}** и моделей **NSPNeuronGen** (τ = 10 мс, D = 5 мс, f = 2000 Гц) и **NSPNeuronGenAsymRmD001C1e9** (τ = 10 мс, D = 1 мс, f = 20000 Гц). Критерий этапа 1 плана: относительная ошибка **амplitude, t_peak и FWHM ≤ 5%** — тогда модель может заменить большую часть сетки E1.1. Trainer×Mode для этой проверки не применим (чистая физика кабеля); конфиги Train/Test — probe-only (`IsNeedToTrain=0`), TipR = 8.6e7, ISI = 2 с.

**Хост:** `.11` (2026-10-22). **Runtime Console:** `tl-agent/Nmsdk` (сборка A0). **Git (docs):** ветка `timelearner_fix2`, без изменений PulseLib/Bin относительно H3 mid-policy (`a780654ee` cold PASS, HEAD docs `f6e829967`).

**Связь с C2:** офлайн-сверка span×(τ,D) уже закрыта как **C2_MATCH** ([`C2_SWEEP_2026-10-20.ru.md`](C2_SWEEP_2026-10-20.ru.md), [`C2_compare_2026-10-20.txt`](C2_compare_2026-10-20.txt)) — это запас синхронизации по паттернам, **не** soma peak/latency/FWHM одиночного EPSP; E1.0 дополняет C2, не дублирует его.

## Прогоны Console (минимальные)

| NeuronModel | Probe | Шаблон Test | lengths | RUN / отчёт |
|---|---|---|---|---|
| NSPNeuronGen | `scratch/E1_0/gen_grid` | W02 `W02_CL480_N1_PSIoff/Test` | 50,4,25,1 | `agent-reports/E1_0_20261022/kernel_gen_grid.json` |
| NSPNeuronGen | C1 p2 (reuse) | тот же | 30,20,**10**,**1** | `C1_20261020_11/kernel_2.json` |
| NSPNeuronGenAsymRmD001C1e9 | C1 p4 (reuse) | W01 `W01_CL50_N0_PSIoff/Test` | 25,10,4,1 | `C1_20261020_11/kernel_4.json` |
| NSPNeuronGenAsymRmD001C1e9 | `scratch/E1_0/asym_L50_w11` | W11 `W11_HIST_asym100_gen/Test` | **50**,25,10,1 | `E1_0_20261022/kernel_asym_L50_w11.json` |

Шаблон W01 ограничивает L ≤ 25 на дендрит; для **L = 50** AsymRm использован W11 (тот же `NeuronClassName`, сегменты до 52). Попытка W02_CL100 для L = 50 дала ошибку Console «no positive NPulseChannel membrane resistance» — не включена в вердикт.

Офлайн-якорь README: L = 1, Gen → pred peak **0.015628** (совпадает с W04 `InitialSomaPotential` ≈ 0.015781 в пределах ~1%).

## Таблица ошибок (Console vs cable_model, критерий E1.0 = 5%)

| NeuronModel | L | peak err | t_peak err | FWHM err | E1.0 row |
|---|---:|---:|---:|---:|---|
| NSPNeuronGen | 1 | −6.55% | +3.45% | 0% | FAIL (peak) |
| NSPNeuronGen | 4 | −6.36% | 0% | 0% | FAIL (peak) |
| NSPNeuronGen | 10 | −6.31% | 0% | −0.68% | FAIL (peak) |
| NSPNeuronGen | 25 | −6.29% | 0% | 0% | FAIL (peak) |
| NSPNeuronGen | 50 | silent (meas=0) | — | — | **INVALID** |
| NSPNeuronGenAsymRmD001C1e9 | 1 | +38.07% | −12.66% | −5.94% | FAIL |
| NSPNeuronGenAsymRmD001C1e9 | 4 | +47.00% | −3.16% | −0.21% | FAIL (peak) |
| NSPNeuronGenAsymRmD001C1e9 | 10 | +46.93% | −1.29% | −0.07% | FAIL (peak) |
| NSPNeuronGenAsymRmD001C1e9 | 25 | +46.90% | −0.52% | 0% | FAIL (peak) |
| NSPNeuronGenAsymRmD001C1e9 | 50 | +46.89% | −0.25% | 0% | FAIL (peak) |

Повторяемость: [`evidence/tools/e1_0_summarize.py`](tools/e1_0_summarize.py) (`--reports ~/TLAgent-20261020/agent-reports`).

## Выводы

**NSPNeuronGen — PARTIAL.** На измеримых L ∈ {1, 4, 10, 25} задержка и FWHM совпадают с моделью в пределах 5% (t_peak ≈ 0%, FWHM ≤ 0.7%). Амплитуда систематически **ниже** предсказания на **6.3–6.6%** (чуть хуже порога E1.0, но в допуске C1 10%). **L = 50:** soma канала дендрита 1 тождественно 0 при корректной проводке — тот же класс DEBT, что **DEBT-C1-silent-soma** (см. [`C1_SET1_PARTIAL_2026-10-20.ru.md`](C1_SET1_PARTIAL_2026-10-20.ru.md) для L = 51). Для сетки E1.1 модель **может заменить прогон по t_peak/FWHM и δ(L)**; по амплитуде нужен фиксированный коэффициент ≈ **1.067** или расширение oracle; **L = 50** на Console требует отдельного разбора silent-soma, не блокирует L ≤ 25.

**NSPNeuronGenAsymRmD001C1e9 — PARTIAL (amp), FAIL (строгий E1.0).** Для L ∈ {4, 10, 25, 50} **t_peak и FWHM** в пределах 5% (на L = 50: −0.25% / 0%). **Peak** стабильно **+39…+47%** vs пассивный cable (как в C1 set4: тормозной Rm = 1e8 не моделируется). L = 1: t_peak −12.7%, FWHM −5.9% — короткий дендрит на f = 20 kГц. Полная замена E1.1 по **амplitude** без калибровки **не** обоснована; по **задержке/ширине** — да.

| Verdict (E1.0) | NSPNeuronGen | NSPNeuronGenAsymRmD001C1e9 |
|---|---|---|
| **Итог** | **PARTIAL** | **PARTIAL** (timing OK на L≥4; amp FAIL) |
| Замена E1.1 grid | частично (timing + L≤25; amp bias; L50 Console invalid) | timing/FWHM; amp — после oracle AsymRm |

**Общий вердикт этапа E1.0: PARTIAL** — строгий MATCH (5% по трём метрикам на всех L) **не** достигнут; C2_MATCH подтверждает только ортогональный offline sweep синхронизации.
