# A3 — runtime wiring (2026-10-20)

Постановка: выяснить, использует ли Console проводку XML как есть (A3.1 corrupt vs repaired) и пересвязывает ли C++ отводы при смене `DendriteLength` без правки `<Links>` (A3.2).

## A3.1

| variant | wiring check | Console | Model SHA change | peaks target=1 soma_0..3 |
|---|---|---|---|---|
| corrupt W09_HIST_asym25/Test | FAIL fanout | killed after TRACE stall | — | см. peaks_corrupt.txt |
| repaired (64 renamed) | OK | killed after TRACE stall; peaks recovered | **no** (same SHA) | 0.00549 0.00608 0.00727 0.01340 |

Console с `TraceLogEnabled` стабильно зависает после заполнения `test_trace.csv` (DEBT-A3-trace-hang). Пики снимались watchdog-ом с уже записанного CSV.

Вердикт A3.1: **A15_ACTIVE_AT_RUNTIME** (ratios target=1 ≈ 8.88 / 8.01 / 6.55 / 1.00).

## A3.2 keep-links L=30,20,10,1 vs template taps 51/43/25/1

| L req | best_matching_tap | template tap | интерпретация |
|---|---|---|---|
| 30 | 30 | 51 | совпал с DendriteLength |
| 20 | null (soma silent) | 43 | канал нем (как C1) |
| 10 | 10 | 25 | совпал с DendriteLength |
| 1 | 1 | 1 | совпал |

`relink_verdict=MIXED_OR_UNCLEAR` из‑за silent L=20; по трём живым каналам задержки совпадают с **запрошенной** длиной, не с XML-отводами → рабочая гипотеза **CPP_RELINKS_TO_DENDRITELENGTH** (с оговоркой silent-каналов).

Train/Test шаблоны: `TimeLearnerMatrix/W09/inputs/W09_HIST_asym25/{Train,Test}` и `W02/inputs/W02_CL480_N1_PSIoff/Test`.

## A3.1 final
A15_ACTIVE_AT_RUNTIME
ratios=[8.878955873484921, 8.014782328323639, 6.552459904966033, 1.0]
