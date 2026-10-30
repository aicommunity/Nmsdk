# E2 R8 A/B — синтез 2026-10-21

Постановка: после трёх повторов на каждом из четырёх кейсов R8 сравнить плечи S0 (Bin refresh без B1/E0, PulseLib `d52dc1c`), S1 (B1+E0, тот же PulseLib/Console) и S2 (E1 flags Console, defaults = no-op) и вынести вердикты EQUIVALENT / DIFFERENT для ворот D2b и G1.

Матрица сырых строк: [`E2_matrix_2026-10-21.tsv`](E2_matrix_2026-10-21.tsv). Host `.17`. Все 12 серий — `SERIES_DONE` / `EXIT=0`.

## Вердикты пар (по успешным результатам; rep3 W01 — infra `worker_exit=1` при Avail&lt;80 ГБ)

| Wave / case | Trainer×Mode | S0↔S1 | S1↔S2 | Ключевые поля (типичный успешный rep) |
|---|---|---|---|---|
| W01 `W01_CL50_N0_PSIoff` | Classic×N0 | **EQUIVALENT** | **EQUIVALENT** | converged_need0; L=`27 22 15 1`; TipR 86 М×4; fires silent |
| W02 `W02_CL480_N1_PSIoff` | Classic×N1 | **EQUIVALENT** | **EQUIVALENT** | not_converged_at_stop; L=`54 44 1 1`; TipR@Rmax на двух входах |
| W04 `W04_BR100_N1_PSIoff` | Branch×N1 | **EQUIVALENT** | **EQUIVALENT** | converged_need0; L=`24 19 11 1`; fires `11111111`; quality_fail |
| W10 br25_nextseg / br50_preinh / br100_preinh | Branch HIST | **EQUIVALENT** | **EQUIVALENT** | converged_posttune_finalized; fires `10000000`; fail=ok |
| W10 br25_gen / br25_preinh | Branch HIST | **EQUIVALENT** | **EQUIVALENT** | converged_posttune_finalized; fires silent; quality_fail |

Train/Test: `TimeLearnerMatrix/{W01,W02,W04,W10}/inputs/<case>/{Train,Test}`.

## Выводы

1. **S1↔S2 = EQUIVALENT** на всём R8: флаги E1 в defaults — no-op; D2b и G1 **не блокируются** различием Console E1.
2. **S0↔S1 = EQUIVALENT**: гипотеза H-A15b (SoftCold fan-out tip→сегменты ломает обучение) на R8 **не подтверждена** — патчи Bin B1+E0 не меняют категории train/fires/L.
3. Classic×N1 W02 stall — системный (все плечи), не артефакт аудитных флагов.
4. Silent / quality_fail на W01 и части W10 — прежний DEBT Test/detection, не DIFFERENT между плечами.
5. **G1 cold** по карточке — только после явного «да» человека; docs-ready: E2 зелёный по EQUIVALENT, диск `.17` после offload `_repro` снова ≈90 ГБ Avail.

## Следующий шаг

F5 (`CorrectAttenuationGammaForTipR`); silent-Test; при «да» — отбор G1 24–32 и серии.
