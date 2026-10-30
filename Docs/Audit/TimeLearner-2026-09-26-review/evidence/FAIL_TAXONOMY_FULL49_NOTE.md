# FAIL taxonomy full49 (Rs/Rm · W3 off)

Срез: Console `39edc03c82665dba` · PulseLib `b5229e4` · Bin `6a7ef63a` · **0 PASS / 49 FAIL**.  
Источник: [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md) · [`SOFTCOLD_CONVERGENCE_AUDIT.ru.md`](SOFTCOLD_CONVERGENCE_AUDIT.ru.md).

| Класс | n (прибл.) | Признак | Действие |
|-------|------------|---------|----------|
| `train_incomplete` / Need=1 | 49 (все) | Cold не закрыл `Need` до конца `-t` | Единственный SoftCold-контракт FAIL |
| stall mid TipR (`other`) | большинство B/D | TipR не canon/flat; L частично вырос; `failure_reason=0` | Исследовать trainer path при derived Rmin |
| `cpp_training_failure_1` | ~8–12 | TipR@derived Rmax → `failure_reason=1`, W3 off | Ожидаемо; не возвращать length-escape |
| tipr @Rmin floor | E/other | TipR≈`rmin=1e4` на части dend | Следствие derived нижней границы |
| gate/fires secondary | многие | `gate_rc≠0` / fires mismatch при Need=1 | Не ослаблять gate; чинить Train |

W3 length-escape / absolute `ResistanceMin=2e7` **не** на пути обучения.
