# SoftCold FAIL — границы и стоит ли чинить

Дата: 2026-10-01. Источники: [FAIL_TAXONOMY.json](FAIL_TAXONOMY.json), W1–W4 remediations, [SOFTCOLD_PLAN_RESULT.md](SOFTCOLD_PLAN_RESULT.md).

**Цель продукта:** рабочий C++ cold Train (`Working=SoftCold`), не зелёный rc ценой порогов. LandscapeOk / Acc / fires **не** ослаблять.

| Корзина | Признак | Типичные кейсы | Чинить? |
|---------|---------|----------------|---------|
| **A_nonseparable_mid** | Need=0, TipR canon, LandscapeOk=0 / NonSeparable | asym25, br25 | Research; можно оставить FAIL как объективную неразделимость |
| **B / AmpNorm Need=1** | Рост L/TipR есть, EOL не закрывает Need | asym50/100, fs* | **Да** — PulseLib EOL/Save (якорь asym50 + model-time autosave) |
| **EstDelay / runaway L** | L≈97 при span480 | phase6_* | XML EstDelay **done** (L≈gold); остаток → B |
| **Harness desync** | TipR flat, L=1, SBM | asym50 historically | **Закрыто** SoftCold fix |
| **Gold PASS + SoftCold FAIL** | Working=GoldTest | почти все SUCCESSFUL | Ожидаемо; не регрессия Gold |

См. также: **[SOFTCOLD_CONVERGENCE_AUDIT.ru.md](SOFTCOLD_CONVERGENCE_AUDIT.ru.md)** (full-matrix 46/49: корзины D/E/B + код vs harness vs объективное), [A_NONSEPARABLE_MID.ru.md](A_NONSEPARABLE_MID.ru.md), [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md), [PHASE6_ESTDELAY_FIX.ru.md](PHASE6_ESTDELAY_FIX.ru.md), [PROTOCOL_WORKING_VS_LASTCHECK.ru.md](PROTOCOL_WORKING_VS_LASTCHECK.ru.md).
