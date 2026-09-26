# Phase 1 — TL-01 classic kAmpNormEps

**Status:** done 2026-09-26

## Change

[`NNeuronTimeLearner.h`](../../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h): `static constexpr int kAmpNormEps = 1e-5` → `double` + `static_assert` positive / `== 1e-5`.

Branch header unchanged (`double` already).

## Build

- Preset: `linux-gcc-debug-local`
- Console SHA-256: `ec86430e871e9314d61b948565581705bf72116516f32bb79c5091994c4a1a47`
- Unpatched baseline Console (P0): `4917a2bcbac318d160ca8b596452d3986ccc9978172d35a1b554d65b5a27c843`
- PulseLib HEAD at fix: (local dirty until commit)

## Tests

`python3 -m unittest tests.test_posttune_verify_unit` → 27 OK (includes `TestClassicAmpNormEpsHeader`, `TestFailureClass`).
