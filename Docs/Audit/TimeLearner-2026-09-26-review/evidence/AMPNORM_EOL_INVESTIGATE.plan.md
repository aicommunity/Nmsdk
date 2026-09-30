# План: почему не завершилась amp-нормализация (после всех прогонов)

Статус: **DONE** (расследование; PulseLib fix — отдельный план).  
Порядок: **(0) checkpoint ✓** → (1) полнота ✓ → (2) классификация ✓ → (3) diagnostic ✓ → (4) code-map ✓.

Связано: [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md), [SOFTCOLD_PLAN_RESULT.md](SOFTCOLD_PLAN_RESULT.md),
`AllSynapsesNormalized` / `ChangeSynapseResistanceStatus` в `NNeuronTimeLearner.cpp`.

## 0. Checkpoint commit — DONE

1. ✓ Bin SoftCold scripts/manifest + root Docs (`c790edb` / later AmpNorm bumps).
2. ✓ Без `*_work/`, archives.
3. ✓ Полнота: 4 extended + 24 C1+C2, `missing_count=0`, все `rc=1`.

## Наблюдение

| case | L | TipR live | Need | класс |
|------|---|-----------|------|-------|
| fs25 | ≈gold | dend2≈`3.4–3.5e7` | 1 | **(a)** not-at-Rmin |
| asym50/100 | growth | `2e7×3` Rmin | 1 | **(b)** @Rmin Need=1 |

## Гипотезы → итог

1. **H1** — ✓ (a) mid-band; код: skip `|dt|>5` / NoImprove без Done.
2. **H2** — возможен, traces не пойманы до wipe.
3. **H3** — главный кандидат для (b).
4. **H4** — ✓; mitigation `--keep-slog` (+ `--no-prune`/`--snap-every`).
5. **H5** — снят.

## Метод — DONE

0. ✓ Checkpoint + полнота.
1. ✓ Bundle classification → STUCK doc.
2. ✓ (a)/(b).
3. ✓ `fs25 --no-prune --snap-every 20`.
4. ✓ Code-map `AllSynapsesNormalized` / TipR branches + `--keep-slog`.
5. ✓ [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md).

## Не смешивать

- NonSeparable mid (A), phase6 EstDelay, SoftCold SBM — вне этого плана.
