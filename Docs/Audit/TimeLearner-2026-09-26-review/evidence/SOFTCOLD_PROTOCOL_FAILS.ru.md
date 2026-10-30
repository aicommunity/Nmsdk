# SoftCold протокольные / gate FAIL

Дата: 2026-10-09. Срез full49 Rs/Rm · W3 off: **0 PASS / 49 FAIL**.

Инвариант: **не** ослаблять LandscapeOk / Acc / fires / SoftCold Need→0.

На текущем срезе почти все FAIL — `train_incomplete` (`Need=1`); gate/fires часто вторичны. Разбор корзин: [`SOFTCOLD_CONVERGENCE_AUDIT.ru.md`](SOFTCOLD_CONVERGENCE_AUDIT.ru.md), [`FAIL_TAXONOMY_FULL49_NOTE.md`](FAIL_TAXONOMY_FULL49_NOTE.md), [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md).

| Метка | Смысл на срезе |
|-------|----------------|
| train_incomplete | Cold не дошёл до Need=0 |
| cpp_training_failure_1 | TipR@Rmax, W3 off |
| tipr_class=other | TipR не canon/flat после бюджета |
| gate_fail | Часто вместе с Need=1 — не ослаблять |

SoftColdOff / GoldTest / MatrixClone — отдельные протоколы; их PASS ≠ SoftCold.
