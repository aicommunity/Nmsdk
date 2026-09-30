# План: почему не завершилась amp-нормализация (после всех прогонов)

Статус: **отложено до `DONE_TAILS`** очереди S3.c/d.  
Порядок после очереди: **(0) git commit checkpoint** → (1) проверка полноты хвостов → (2) этот план amp-norm.

Связано: [SOFTCOLD_PLAN_RESULT.md](SOFTCOLD_PLAN_RESULT.md), `EndOfLearning` / `AllSynapsesNormalized` в `NNeuronTimeLearner.cpp`.

## 0. Checkpoint commit (перед проверкой полноты)

После `DONE_TAILS`, **до** сверки манифеста/C1+C2:

1. Зафиксировать Docs/audit, Bin scripts (`repro_cold_lib`, `posttune_verify` overrides, smoke), `_repro/*manifest*`, `SOFTCOLD_DEFER_rcs_after_softcold_fix.txt`, taxonomy.
2. **Не** коммитить `*_work/`, StatisticLog, огромные archives (скилл `nmsdk-gitlinks`).
3. Только после успешного commit — проверка полноты хвостов и при необходимости AMPNORM.
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

1. Собрать все extended + B_partial bundles: provenance, tipr_live, mid_dbg, Need/TipR/L final.
2. Классифицировать: (a) TipR not-at-Rmin, (b) TipR@Rmin but Need=1, (c) PostTune stuck.
3. Точечный re-run **одного** кейса (`fs25_gen` или `asym50`) с:
   - отключённым prune **или** периодическим SNAP ResistanceStatus / AmpDt / NoImprove / DendLastAbsDt / TrainingPhase;
   - EnableDebug AmpDtAudit если доступен в логе.
4. Сопоставить с условиями `AllSynapsesNormalized` (ветки amp_ok / at_r_min / dead_tip / no_improve).
5. Документ: `evidence/AMPNORM_EOL_STUCK.ru.md` + при необходимости правка harness (не ослаблять LandscapeOk).

## Не смешивать

- NonSeparable mid (A) — после Need=0.
- Phase6 EstDelay runaway — отдельная ось.
- SoftCold SBM/tip-1 — уже снят как причина «не старта».
