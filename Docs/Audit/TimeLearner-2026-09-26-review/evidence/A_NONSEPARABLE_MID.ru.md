# A — NonSeparable mid (asym25 / br25)

Дата: 2026-10-01.  
Класс: **A_nonseparable_mid** ([SOFTCOLD_PLAN_RESULT.md](SOFTCOLD_PLAN_RESULT.md), [RETEST_EXTENDED_TIME.plan.md](RETEST_EXTENDED_TIME.plan.md)).

## Симптом

Train **Done** (Need=0), TipR **canon**, gate **FAIL**: FLAG `result=2` / `landscape_ok=0`, silent mid / NonSeparable.  
Не AmpNorm EOL и не EstDelay runaway.

## Известные якоря (до W4 retest)

| case | Train | TipR | gate | источник |
|------|-------|------|------|----------|
| asym25_preinh | Done | canon | NonSeparable mid | S3.b `S3_QUEUE_RESULT.md` |
| br25_on | Done | canon | NonSeparable | S3.b |

## Гипотезы (quality, не budget)

1. Mid-zone / LandscapeOk порог корректно режет неотделимый mid — **не** ослаблять LandscapeOk ради PASS.
2. Preinh / packA mid silent при коротком span 25 мс — проверить live mid_source + landscape metrics после SoftCold на HEAD.
3. Иное: thr/search path; отделять от TipR@Rmin Need=1 (AmpNorm b).

## Retest план

`posttune_verify --case asym25_preinh` + `br25_preinh` (и/или `br25_on` как S3 контроль).  
Критерий фикса: Need=0 + tipr=canon + **LandscapeOk=1** / gate PASS **без** ослабления порогов.  
Иначе: оставить FAIL + документировать A; extended `-t` не применять.

## После retest

(заполнить)
