# SoftCold final matrix — follow-up W0–W6 (2026-10-01)

> **Актуальный SoftCold full49 HEAD (2026-10-07/08):** **13 PASS / 36 FAIL** — см. [`SOFTCOLD_CONVERGENCE_AUDIT.ru.md`](SOFTCOLD_CONVERGENCE_AUDIT.ru.md) и [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md). Ниже — исторический closeout W0–W6 (0 SoftCold PASS), не путать с HEAD rematrix.

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
- SUCCESSFUL SoftCold: **пусто** (только GoldTest/SkipTrainGold PASS в реестре) — колонки **Working**/**LastCheck**: [PROTOCOL_WORKING_VS_LASTCHECK.ru.md](PROTOCOL_WORKING_VS_LASTCHECK.ru.md).
- LandscapeOk / Acc / fires пороги **не** менялись.
- Границы FAIL: [SOFTCOLD_FAIL_BOUNDS.ru.md](SOFTCOLD_FAIL_BOUNDS.ru.md). Autosave: [MODEL_TIME_AUTOSAVE.ru.md](MODEL_TIME_AUTOSAVE.ru.md).

Ссылки: [STATUS.ru.md](../STATUS.ru.md), [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md), [PHASE6_ESTDELAY_FIX.ru.md](PHASE6_ESTDELAY_FIX.ru.md), [A_NONSEPARABLE_MID.ru.md](A_NONSEPARABLE_MID.ru.md), [W5_R01_R04.ru.md](W5_R01_R04.ru.md).


## Волна autosave / Working (2026-10-01)

- Console SHA-256 `e018c02430d905be…` · PulseLib `b29b595` (Branch AmpNorm b mirror) · harness `--autosave-model-s 10`.
- Инвентарь: [`SOFTCOLD_CANON_INVENTORY.md`](../../../Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_CANON_INVENTORY.md) · очередь [`SOFTCOLD_QUEUE_manifest.txt`](../../../Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_QUEUE_manifest.txt).
- Лог матрицы: [`metrics/SOFTCOLD_full_matrix.log`](metrics/SOFTCOLD_full_matrix.log) · RCS [`SOFTCOLD_HEAD_rcs.txt`](../../../Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_HEAD_rcs.txt).
- Цель: рост `Working=SoftCold` где объективно возможно; GoldTest не обнулять. Working≠SoftCold без cold PASS.

### Статус очереди autosave (live)

- Запущена softcold_full_matrix.sh (49 case), якорь первый: asym50_preinh.
- Smoke autosave OK; SoftCold workdir писал Project auto-save call completed @ model t=10/20.
- RCS: _repro/SOFTCOLD_HEAD_rcs.txt; реестр обновляется apply_softcold_rcs_to_registry.py после каждого case.
- Working≠SoftCold, пока нет cold PASS.
### Autosave wave — first Cold PASS

- **asym50_preinh SoftCold PASS** (rc=0) 2026-10-01 · Console `e018c024…` · TipR@Rmin Need=0 fires=`10000000`.
- Working=`SoftCold` в реестре. Очередь продолжается (`asym25_preinh`…).
- **asym25_preinh SoftCold PASS** (rc=0) 2026-10-01; очередь 2 PASS / 0 FAIL, сейчас `br25_on`.

