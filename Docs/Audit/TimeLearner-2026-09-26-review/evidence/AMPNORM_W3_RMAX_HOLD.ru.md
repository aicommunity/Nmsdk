# W3 — RmaxDwell escape only when dt≥0

Дата: 2026-10-05. PulseLib `b32d715`. Console SHA16 `8589daff…`.

## Проблема

RmaxDwell escape всегда делал `R *= (1−step)` даже при `amp_dt < 0` (overshoot @ Rmax) → осцилляция `1e11 ↔ 0.85·Rmax`.

## Фикс

`NNeuronTimeLearner.cpp` / `NNeuronTimeLearnerBranch.cpp`:
- `dt >= 0` → down-step (undershoot);
- `dt < 0` → **hold** (не понижать R; dwell остаётся armed).

## Smoke / rematrix

- Keep PASS: `asym50`, `ltz50_gen`, `br50_gen`, `fs25_gen`.
- D-кейсы (`pa00`, `phase6_*`): TipR остаётся на ceiling без длительного 1e11↔8.5e10 step-down при `amp_dt<0`.
- Полная матрица: 13 PASS / 36 FAIL; корзина D=20 (ceiling hold, Need=1).
