# A — NonSeparable mid (asym25 / br25)

Дата: 2026-10-01.  
Класс: **A_nonseparable_mid** ([SOFTCOLD_PLAN_RESULT.md](SOFTCOLD_PLAN_RESULT.md), [RETEST_EXTENDED_TIME.plan.md](RETEST_EXTENDED_TIME.plan.md)).

## Симптом (исторический S3)

Train **Done** (Need=0), TipR **canon**, gate **FAIL**: FLAG `result=2` / `landscape_ok=0`, silent mid / NonSeparable.  
Не AmpNorm EOL и не EstDelay runaway.

## Retest W4 (Console `b66711b5…`)

Log: `metrics/SOFTCOLD_w4_nonsep_retest.log`. **LandscapeOk не ослабляли.**

| case | TipR live | Need@end | gate | rc | note |
|------|-----------|----------|------|----|------|
| asym25_preinh | (no live snap; flag early) | 1@flag | 1 | **1** | mid dbg: MaybeStart Need=0 MidEn=1; SoftCold incomplete/flush — не чистый A |
| br25_preinh | `2e7×2` + mid≈6.8e7 | 1 (poll117) | **0** | **1** | gate PASS при Need=1 → verify всё равно FAIL |
| br25_on | live mid≈4.2e7; report TipR@Rmin canon | 0 (report) | 1 | **1** | fires_missing / gate_fail |

**Итог:** Cold PASS нет; классический A (Done+canon+NonSeparable) на HEAD **не** воспроизведён чисто.  
Гипотеза «ослабить LandscapeOk» **отклонена** — пороги без изменений.

## Гипотезы (quality, не budget)

1. Mid-zone / LandscapeOk порог корректно режет неотделимый mid — **не** ослаблять.
2. На HEAD AmpNorm/TipR-path меняет путь к Done vs S3 — отделять от TipR@Rmin Need=1 (AmpNorm b).
3. br25_preinh: gate_rc=0 недостаточен без Need=0 / fires.
