# §5 flat TipR — asym25 / nextseg

Дата: 2026-10-05. SoftCold W4 provenance + case table.

## asym25

| поле | значение |
|------|----------|
| tipr_class | `flat` |
| expect_tipr | `flat` (CASES) |
| train | `done_flag_flush_gate_FAIL` |
| gate_rc | 1 |
| failure_class | `gate_fail` |
| TipR live | `8.6e7×4` |

**Вердикт:** flat TipR — **ожидаемый** режим кейса (`expect_tipr=flat`), не баг AmpNorm freeze. SoftCold FAIL = gate/селективность. C++ cold TipR start **не** править. LandscapeOk не ослаблять (§4).

## nextseg (`br50_nextseg`, `br100_nextseg`)

Корзина A в аудите (протокол сегментации; R-tune может не стартовать). Проверка в полной parallel-матрице; при L=`1 1 1 1` + flat — только документ, не маскировать Need.

## C++

Не вносился (diag ≠ freeze-при-ready с неверным expect).
