# G1 S1 — PARTIAL извлечение метрик после RERUN (2026-10-22)

**Arm:** G1.S1. **Отбор:** 13 волн / 32 case — [`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv). **Кампания SHA (план):** Console `745d6061…`, PulseLib `6d746ac`; статус exit после RERUN — [`G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md`](G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md) (коммит плана `39289c503`). **Политика:** [`G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md`](G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md) — без `SYNTHESIS_FINAL` по полной матрице, без повторного cold RERUN на том же SHA.

**Машиночитаемый срез:** [`G1_S1_PARTIAL_METRICS_2026-10-22.tsv`](G1_S1_PARTIAL_METRICS_2026-10-22.tsv) — **38 строк** (9 exit-clean × rep1–3; 29 case-строк для волн с `launch.exit≠0` на последнем принятом rep3). Иерархия колонок и группировка — [`RESULT_GROUPING_HIERARCHY.ru.md`](RESULT_GROUPING_HIERARCHY.ru.md); полные Acc/Цель/Test — **только** где `failure_class` пуст и `launch_exit=0`.

## Постановка

После закрытия серии **`G1_S1_RERUN`** (2026-10-22T03:05Z) осталось **3/13** волн с **`launch.exit=0`** на последнем rep3 (W01, W13, W33 — first-pass на `.11`); **10/13** волн по-прежнему закрываются с кодами **1** или **2**, при этом drv исторически печатал `SERIES_DONE`/`EXIT=0` (DEBT-G1-exit-gate). Документ фиксирует **честный PARTIAL rollup**: метрики обучения и silent-Test inference для exit-clean подмножества плюс маркированные строки `failure_class=launch_exit_N` для остальных case без зачёта PASS×3 и без подстановки Acc/Цель там, где очередь не принята как exit-clean.

Источники read-only: [`G1_S1_GOOD_WAVES_EXTRACT_2026-10-21.tsv`](G1_S1_GOOD_WAVES_EXTRACT_2026-10-21.tsv) (W01/W13/W33, три rep), `summary.tsv` / `queue_exit.txt` под `$REPORTS/G1/{run_id}/` для RERUN rep3 где артефакты есть на Elder-1 (W02, W31); для `.17` RERUN rep3 локальных summary на `.11` нет — строки case-level с `—` в метриках Test и сохранёнными Train/Test путями matrix inputs.

## Сводка exit-clean (метрики допустимы для SYNTHESIS_PARTIAL)

На всех **девяти** строках exit-clean (три rep × три волны) картина **стабильна**: Train доходит до `converged_need0` (W01) или `converged_posttune_finalized` (W13, W33); Test в режиме **silent** даёт **Acc=7/8**, **Цель=нет**, `fires=00000000`, separation **fail** / detection **target_not_detected**. Это **не** PASS по контракту PostTrain verify (нет попадания в цель), но очередь **exit-clean**, поэтому цифры включаются в partial-синтез как факт Console на текущем SHA, а не как успех кампании.

| Wave | Trainer×Mode | Span | NeuronModel | Mod | PostTune | Case (rep3 run_id) | Acc | Цель | Train conv. |
|------|--------------|------|-------------|-----|----------|-------------------|-----|------|-------------|
| W01 | Classic×N0 | 50 | AsymRm | gen | OFF | W01_CL50_N0_PSIoff (`…113257Z-15892`) | 7/8 | нет | converged_need0 |
| W13 | Classic×N1 | 50 | AsymRm | gen | OFF | W13_HIST_ltz50_gen (`…073758Z-3533`) | 7/8 | нет | converged_posttune_finalized |
| W33 | Classic×N0 | 50 | AsymRm | gen | ON | W33_CL50_N0_PSIoff_POST (`…120726Z-15166`) | 7/8 | нет | converged_posttune_finalized |

Train/Test для каждой строки TSV: `TimeLearnerMatrix/{WAVE}/inputs/{CASE}/{Train,Test}` (см. колонки `train_config` / `test_config` в TSV).

## Группировка Trainer×Mode → Span (вся выбранная матрица)

### Classic×N0

**Span 50.** Exit-clean **W01** (AsymRm, PostTune OFF) и **W33** (тот же span, PostTune ON) — единственные case на оси с полными Test-метриками; оба дают silent 7/8 без цели. **W02** (Span **100** и **480**, baseline gen, OFF) после RERUN rep3 `…232414Z-32270` имеет **`launch_exit=1`**, `queue_exit=1`; partial-строки несут `failure_class=launch_exit_1`, Train остановился `not_converged_at_stop`, Test **не оценён** (`not_evaluated_training_incomplete`). **W31** (Span **480**, margin-current) — RERUN rep3 `…184544Z-29973`, тот же класс failure; одна case-строка с неполным Train-следом, Acc/Цель **—**. **W04** в Classic×N0 не входит (Branch).

### Classic×N1

**Span 50.** **W13** (HIST ltz50 gen) — exit-clean, метрики как в § exit-clean. **W09** на `.17` (5× HIST, spans 25–480) — последний RERUN rep3 `…200402Z-28218`, **`launch_exit=1`**; 5 case-строк `launch_exit_1`, Acc/Цель **—**. **W12** (Span **480**, phase6 ltzcal twin) — RERUN **`launch_exit=1`**, одна case-строка без локального summary.

### Branch×N0

**Span 480.** **W04** (gen, OFF) — RERUN rep3 **`launch_exit=2`** (`launch_exit_2`), единственная волна с кодом 2. **W08** (nextseg) — RERUN **`launch_exit=1`**. **W48** (FastSpan, 6× gen/nextseg, spans 25/50/100) — RERUN rep3 **`launch_exit=1`**, шесть case-строк без Acc/Цель.

**Span 100 / 50 / 25 (Branch×N0 и смешанные HIST).** **W10** (3 case), **W11** (в т.ч. br480 nextseg/tiprmin) — RERUN **`launch_exit=1`**, case-level маркировка без Test PASS.

### Branch×N1

**W09** / **W10** / **W11** содержат N1 case (`norm=1` в отборе): для них в TSV `mode=N1`; метрики Test не зачисляются из‑за `launch_exit_1` на волне. **W37** (Classic×N0/N1 packB/packC, spans 25/100) — RERUN rep3 `…174842Z-18318`, **`launch_exit=1`**, summary на Elder-1 **NO_RESULTS**; шесть case-строк только с failure_class и путями Train/Test.

## Выводы для плана

RERUN **не расширил** exit-clean подмножество beyond W01/W13/W33; partial extract подтверждает, что даже на «принятых» волнах Console стабильно даёт **7/8 без цели** в silent Test — согласуется с открытыми DEBT (silent-Test, CL-N1, F5 paired), а не с инфраструктурным one-shot glitch. **G1 vs C2** по всем 32 case остаётся **заблокирован** до смены SHA/алгоритма или нового отбора; допустим следующий шаг — заполнение [`SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md`](SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md) секцией **SYNTHESIS_PARTIAL** со ссылкой на этот TSV.

## Связанные артефакты

| Файл | Роль |
|------|------|
| [`G1_S1_PARTIAL_METRICS_2026-10-22.tsv`](G1_S1_PARTIAL_METRICS_2026-10-22.tsv) | Канон PARTIAL extract |
| [`G1_S1_GOOD_WAVES_EXTRACT_2026-10-21.tsv`](G1_S1_GOOD_WAVES_EXTRACT_2026-10-21.tsv) | Источник exit-clean rep1–3 |
| [`G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md`](G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md) | Черновик схемы колонок |

---
Зеркало (sync): `/home/user/TLAgent-20261020/agent-reports/G1/G1_S1_PARTIAL_METRICS_2026-10-22.{ru.md,tsv}`.
