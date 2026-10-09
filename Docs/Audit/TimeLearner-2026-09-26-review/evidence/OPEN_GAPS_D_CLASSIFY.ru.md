# Open Gaps / D classify (после full49 Rs/Rm · W3 off)

Дата: 2026-10-09.  
`EnableRmaxLengthEscape=false`. D-корзина SNAP (**D=24**) — **не** W3 length-escape и не absolute Rmin ceiling-hold как путь обучения.

Актуальный срез: [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md) · [`STATUS.ru.md`](../STATUS.ru.md) · **0 PASS / 49 FAIL**.

## Что значит D сейчас

- TipR mid/`other` или @derived Rmax, `Need=1`, cold не сошёлся.
- Подмножество с `cpp_training_failure_1` (честный stop на Rmax).
- Старые метки `D_algo_open` / W3d–W3e **сняты** с живого аудита.

## Open research (не ослаблять gate)

1. Почему при derived `Rmin≈Rm/1000` TipR/L часто залипают mid при `failure_reason=0`.
2. Честный Rmax-fail path vs stall mid — раздельные гипотезы.
3. Gold/MatrixClone PASS остаются контролем весов; SoftCold Working на срезе отсутствует.

`D_algo_open` / AmpNorm W3-escape campaigns — не актуальны.
