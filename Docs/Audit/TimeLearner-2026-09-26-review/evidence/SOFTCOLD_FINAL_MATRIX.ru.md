# SoftCold final matrix — follow-up W0–W6 (2026-10-01)

## Базовая матрица 37 RC

Источник: [`SOFTCOLD_DEFER_rcs_after_softcold_fix.txt`](../../../Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_DEFER_rcs_after_softcold_fix.txt)  
**37 / 37 `rc=1` · 0× `rc=0` (Cold PASS).**

Taxonomy snapshot: [`FAIL_TAXONOMY.json`](FAIL_TAXONOMY.json) (after SoftCold fix; subtypes A/B/… — не переписывать историю S3).

## Remediations на HEAD AmpNorm (`bb438c4` / Console `b66711b5…`)

| WS | Цель | SoftCold PASS? | Эффект |
|----|------|----------------|--------|
| W0 | реестры / taxonomy | — | SoftCold DEFER closed; 0 PASS зафиксирован |
| W1 | TipR mid-band (a) | **нет** | fs50 TipR@Rmin; fs* Need=1 |
| W2 | TipR@Rmin Need=1 (b) | **нет** | asym* TipR@Rmin; Need/gate fail |
| W3 | Phase6 EstDelay | **нет** | L≈gold (не ~97); Need/TipR/gate fail |
| W4 | NonSeparable mid | **нет** | LandscapeOk не ослаблен; asym25/br25 rc=1 |
| W5 | R01/R04 + TL-06 | — | headers done; R01/R04 **blocked: time** |
| W6 | closeout | — | эта матрица |

## Вердикт кампании

- SoftCold **desync** (S1–S3) — успех (исторически).
- **Cold PASS** после W1–W4 remediations — **по-прежнему 0**.
- SUCCESSFUL SoftCold: **пусто** (только GoldTest/SkipTrainGold PASS в реестре).
- LandscapeOk / Acc / fires пороги **не** менялись.

Ссылки: [STATUS.ru.md](../STATUS.ru.md), [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md), [PHASE6_ESTDELAY_FIX.ru.md](PHASE6_ESTDELAY_FIX.ru.md), [A_NONSEPARABLE_MID.ru.md](A_NONSEPARABLE_MID.ru.md), [W5_R01_R04.ru.md](W5_R01_R04.ru.md).
