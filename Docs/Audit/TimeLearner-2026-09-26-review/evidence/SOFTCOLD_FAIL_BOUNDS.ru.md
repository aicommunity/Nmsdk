# SoftCold FAIL — границы и стоит ли чинить

Дата: 2026-10-09. Срез full49: **0 PASS / 49 FAIL** (W3 off, derived Rs/Rm).  
Источники: [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md), [`SOFTCOLD_CONVERGENCE_AUDIT.ru.md`](SOFTCOLD_CONVERGENCE_AUDIT.ru.md), [`FAIL_TAXONOMY_FULL49_NOTE.md`](FAIL_TAXONOMY_FULL49_NOTE.md).

**Цель продукта:** рабочий C++ cold Train (`Working=SoftCold`), не зелёный rc ценой порогов. LandscapeOk / Acc / fires / Need→0 **не** ослаблять.

| Корзина | Признак на срезе | Чинить? |
|---------|------------------|---------|
| **train_incomplete** | Need=1 до конца `-t`; TipR mid/`other` | **Да** — логика cold при derived bounds (не harness) |
| **cpp_training_failure_1** | TipR@Rmax, `failure_reason=1`, W3 off | Не возвращать W3; отдельный research path |
| **E / Rmin floor** | TipR≈derived rmin | Исследовать, не absolute floor 20 МΩ |
| **G (br100 keep/search)** | search/keep аномалии; `br100_search` rc=137 | Отдельно от AmpNorm-D |
| **Gold PASS + SoftCold FAIL** | Working=GoldTest | Ожидаемо на этом срезе |

См. также: [A_NONSEPARABLE_MID.ru.md](A_NONSEPARABLE_MID.ru.md), [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md), [PROTOCOL_WORKING_VS_LASTCHECK.ru.md](PROTOCOL_WORKING_VS_LASTCHECK.ru.md).
