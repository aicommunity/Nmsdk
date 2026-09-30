# План: почему не завершилась amp-нормализация (после всех прогонов)

Статус: **в работе** (после `DONE_TAILS` 2026-09-30T10:05:51Z).  
Порядок: **(0) git commit checkpoint ✓** → (1) проверка полноты хвостов ✓ → (2) этот план amp-norm.

Связано: [SOFTCOLD_PLAN_RESULT.md](SOFTCOLD_PLAN_RESULT.md), `EndOfLearning` / `AllSynapsesNormalized` в `NNeuronTimeLearner.cpp`.

## 0. Checkpoint commit (перед проверкой полноты) — DONE

После `DONE_TAILS`, **до** сверки манифеста/C1+C2:

1. ✓ Bin `0bb8125` (scripts/manifest/rcs) + root `c790edb` (Docs evidence + Bin gitlink).
2. ✓ Без `*_work/`, StatisticLog, archives (`nmsdk-gitlinks`).
3. ✓ Полнота: 4 extended + 24 C1+C2 в RC, `missing_count=0`, все `rc=1`.
## Наблюдение (уже)

| case | L | TipR live | Need | Интерпретация |
|------|---|-----------|------|----------------|
| fs25_gen_ext640 | gold `6 5 4 1` | dend2≈`3.4e7` (не Rmin) | 1 | length OK, **amp-norm не дожат** на dend2 |
| asym50 (ext, mid) | ≈`29 22 15 1` | canon `2e7×3` | 1 | TipR на полу; EOL всё равно не срабатывает → residual `|ampDt|`, sync, или иной gate |

`EndOfLearning` = `AllDendritesSynced() && AllSynapsesNormalized()`; при PostTune Need не сбрасывается сразу.

## Гипотезы

1. **H1 TipR floor + residual dt** — R на Rmin, но `|Initial−MaxAmp|>kAmpNormEps` и знак/условия `at_r_min&&dt_positive` не закрывают Done.
2. **H2 NoImprove застревание** — счётчик/oscillation band не достигает best-effort выхода.
3. **H3 length_settled ложный** — L≈gold, но `DendLastAbsDt` / BestEffort не в tol → `ready_for_r_tune=0` или sync gate.
4. **H4 prune/harness** — после `rmtree(StatisticLog)` трассы мертвы; диагностика слепа (не причина EOL, но мешает).
5. **H5 softcold tip-1 vs gold fat** — иная траектория ampDt после strip (сравнить с GoldTest / pre-fix strip).

## Метод после очереди

0. ✓ Checkpoint + полнота (см. §0).
1. ✓ Собрать extended bundles: см. [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md) — классы (a)/(b).
2. ✓ Классификация: fs25=(a) TipR not-at-Rmin; asym\*=(b) TipR@Rmin Need=1.
3. ✓ Diagnostic `fs25_gen --no-prune --snap-every 20`: Need=1, dend2 mid-band; NM exit по `-t`; slog wiped post-run.
4. Сопоставить с `AllSynapsesNormalized` / TipR-update (`dt>5` skip) — **next** (код + keep-slog).
5. ✓ Документ: [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md).

## Не смешивать

- NonSeparable mid (A) — после Need=0.
- Phase6 EstDelay runaway — отдельная ось.
- SoftCold SBM/tip-1 — уже снят как причина «не старта».
