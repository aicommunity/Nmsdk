# SoftCold протокольные / gate FAIL — объяснение без ослабления gate

Дата: 2026-10-07. Open Gaps Phase Proto.  
Инвариант: **не** ослаблять LandscapeOk / Acc / fires / SoftCold Need→0.

Связано: [SOFTCOLD_CONVERGENCE_AUDIT.ru.md](SOFTCOLD_CONVERGENCE_AUDIT.ru.md), [AMPNORM_EOL_W0_SNAP.md](AMPNORM_EOL_W0_SNAP.md).

## E_gate — Need→0 (или Train Done), падает gate/Landscape

Train AmpNorm/EOL **не** главный блокер. Примеры семейств rematrix: silent mid / LandscapeOk=0 при каноне TipR (`fs100_gen` и соседние gen с gate_fail).  
Действие: фиксировать Train Done vs gate rc раздельно; quality/mid research — вне AmpNorm. SoftCold PASS не выдавать при gate_fail.

## N — NonSeparable mid

| case | Смысл |
|------|--------|
| `br25_on` | TipR может быть @Rmin / Train почти Done; `LandscapeOk=0`, mid NonSeparable |

Объективное свойство ландшафта/паттерна. **Не** чинить ослаблением LandscapeOk. В W0: Train-EOL отдельно от gate.

## C — metrics после Need≈0

| case | Смысл |
|------|--------|
| `fs50_preinh` | overlap с E; metrics/verify после «почти готового» Train |
| `br25_off` (SoftColdOff) | Need=0, verify fires/Acc — отдельный протокол Off |

Не ослаблять expect_fires / Acc ради зелёного SoftColdOff.

## A — flat LastR / протокол сегментации

| case | Смысл |
|------|--------|
| `asym25` | flat / cold TipR path |
| `br50_nextseg`, `br100_nextseg` | L=`1 1 1 1` — R-tune часто не стартует; протокол nextseg |

Не считать дефектом CanonRmin AmpNorm без отдельного nextseg-плана.

## G — другой TipRMode

| case | Смысл |
|------|--------|
| `br100_keep` | KeepDone — mid TipR допустим для режима |
| `br100_search` | SearchSynthetic |

Вне критериев SoftCold CanonRmin. Не использовать как свидетельство бага base AmpNorm.

## SoftColdOff

`br25_off` — PASS SoftColdOff на rematrix при своём контракте; verify-отличия не смешивать с CanonRmin SoftCold+PostTune.

## Итог Proto

Эти корзины **документированы как объяснённые / вне AmpNorm E/B fix**. C++ TimeLearner не менять ради них в Open Gaps волне.

**Full49 HEAD:** N=`br25_on`, A=`asym25`+nextseg, G=`br100_keep/search` подтверждены в [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md).
