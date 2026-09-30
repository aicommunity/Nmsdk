# Анализ выполнения плана SoftCold fix → retest

Дата: 2026-09-28.  
План: [SOFTCOLD_FIX_THEN_RETEST.plan.md](SOFTCOLD_FIX_THEN_RETEST.plan.md).  
Fix tag: `softcold_fix=2026-09-27_sbm2_strip_tip1`.  
Console: `ec86430e…`.

## Вердикт по целям плана

| Цель плана | Итог | Комментарий |
|------------|------|-------------|
| S0 стоп сломанного SoftCold | **успех** | Phase5 aborted |
| S1 harness SoftCold (SBM=2 all + tip-1 strip + membrane sync + contract) | **успех** | unit test OK |
| S2 smoke: рост стартует | **успех** | asym50/25 ~30 s, L↑ TipR≠flat |
| S3.a снять `timing_softcold_desync` | **успех** | asym50/100_* live TipR→canon, L≈gold |
| S3.a Cold PASS | **провал** | Need≠0, XML не Save, gate FAIL |
| S3.b не сломать Train Done (asym25/br25) | **успех** | Done + tipr=canon; gate FAIL как раньше (A) |
| S3.b fs25/phase6 → PASS | **провал** | incomplete / runaway |
| S3.c полная DEFER C1+C2 | **в запуске** | хвост после S3.a/b |
| S3.d extended `-t` | **в запуске** | P0: fs25 + B_partial asym* |
| Cold PASS / SUCCESSFUL PASS rows | **не достигнуто** | ни один из 9 не PASS |

**Итог кампании фикса:** целевая проблема SoftCold (**desync / frozen TipR**) устранена.  
Кампания **не** дала SoftCold Cold PASS — остались независимые корзины A (quality) и B_partial/runaway (EOL / EstDelay).

---

## Успехи (что доказано)

1. **Корневая причина frozen asym50/100** была в harness SoftCold (SBM last=0 + fat Model при L-теге=1 → `DelayLenOf=0`), не в eps и не в span-формуле.
2. После фикса рост **стартует за минуты**; TipR уходит с flat cold на canon Rmin; L выходит к gold-like (`29≈25`, `52≈52`).
3. Регрессии Train Done на asym25/br25 **нет** (flag + tipr=canon).
4. Контракт soft-cold теперь явный: tip-1 physically, SBM=2 everywhere.

## Провалы и причины

| Корзина | Кейсы after-fix | Причина | Лечится SoftCold-фиксом? | Дальше |
|---------|------------------|---------|--------------------------|--------|
| **A_nonseparable_mid** | asym25, br25 | Need=0/Done, tipr=canon, mid silent / NonSeparable LandscapeOk=0 | Нет (quality) | mid/Landscape research |
| **B_partial_growth_need1** | asym50, asym100_*, fs25 | L/TipR выросли (или почти gold), EOL/Need=0 не в budget; у asym* XML flat из‑за no Save | Частично (desync снят) | extended `-t` + разбор EOL/Save |
| **B_runaway_length** | phase6_* | L≫gold (`97…`), TipR ceiling — `EstDelayPerSeg` vs span480 | Нет | параметры EXP / EstDelay, не SBM |
| Harness artifact | asym50/100 XML tipr=flat | poll-cap SIGTERM до Save; live≠params; после prune slog=0 | Нет | live-aware fail notes; prune StatisticLog |

## Сдвиг таксономии (до → после фикса)

| case | до | после |
|------|----|-------|
| asym50/100_* | `B_tipr_frozen_cold` / `timing_softcold_desync` | `B_partial_growth_need1` / `timing_ok_budget`* |
| asym25, br25 | A | A (без регрессии) |
| fs25 | B_partial / timing_ok_budget | B_partial (сохр.) |
| phase6_* | B_runaway / timing_est_delay | B_runaway (сохр.) |

\* timing: budget теперь уместен для extended; XML report всё ещё пишет tipr=flat — смотреть live/`tipr_live`.

## Что не закрыто планом

- EndOfLearning при уже settled TipR/L (asym50/100).
- NonSeparable mid.
- Phase6 EstDelay vs span.
- Полный покрытие C1+C2 (S3.c) и extended P0 (S3.d) — хвосты запускаются отдельно.

## Артефакты

- [S2_SMOKE_RESULT.md](S2_SMOKE_RESULT.md)
- [S3a_DESYNC_SUMMARY.md](S3a_DESYNC_SUMMARY.md)
- [S3_QUEUE_RESULT.md](S3_QUEUE_RESULT.md)
- [FAIL_TAXONOMY.json](FAIL_TAXONOMY.json) (секция after_softcold_fix)
- RC: `_repro/SOFTCOLD_DEFER_rcs_after_softcold_fix.txt`
