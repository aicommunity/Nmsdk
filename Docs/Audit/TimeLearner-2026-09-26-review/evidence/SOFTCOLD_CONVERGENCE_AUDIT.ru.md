# SoftCold convergence audit (full49 Rs/Rm · W3 off)

Срез: Console `39edc03c82665dba` · PulseLib `b5229e4` · Bin `6a7ef63a` · PARALLEL=8 · **0 PASS / 49 FAIL**.

## Вердикт

Ни один SoftCold-49 case не довёл cold Train до `Need=0`. Все строки реестра: SoftCold=`FAIL`, `failure_class=train_incomplete`.

## Корзины (SNAP)

| bucket | n | смысл на этом срезе |
|--------|---|---------------------|
| D | 24 | TipR mid/`other`, Need=1; часть с TipR@Rmax |
| B | 19 | Branch/asym-like stall mid TipR |
| E | 2 | TipR у нижней границы (asym100/ltz100) |
| G | 2 | br100 keep/search аномалии (`br100_search` rc=137) |
| N | 1 | br25_on |
| other | 1 | asym100_gen |

## Механики FAIL

1. **train_incomplete / not_converged_at_stop** (большинство): бюджет `-t` исчерпан при `Need=1`, `failure_reason=0`, `w3_length_escape=0`. TipR не canon; L частично вырос; gate/fires вторично.
2. **cpp_training_failure_1** (pa*/phase6*/часть psi*): TipR@derived Rmax → `failure_reason=1` при W3 off (length-escape запрещён).

См. [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md), [`STATUS.ru.md`](../STATUS.ru.md).
