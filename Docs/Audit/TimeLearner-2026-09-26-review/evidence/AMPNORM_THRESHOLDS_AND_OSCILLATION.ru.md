# AmpNorm пороги и потолочная осцилляция TipR

Дата: 2026-10-07. SoftCold Need→0 **не** ослаблять (no always-success SoftCold).

## A. Пороги решений

| Порог | Значение | Гейт | «Почему» | Relax для D-core |
|-------|----------|------|----------|------------------|
| SyncTolerance | default 0.02 s; SoftCold XML keep ~0.002 | length/peak sync, часть length_settled | «~1 model step» ADefault | не снимает LastAbsDt~0.4; риск keep |
| kRminLengthTolFactor | 4 | slack LastAbsDt @Rmin/Rmax в settled; EOL slack только @Rmin | keepslog ×2 → SoftCold E ×4 | ×N не до 0.4 |
| dwell / cooldown | 3 | arm ceiling escape / pace length | heuristic | не лечит перелёт |
| TipR step | 0.15 | midband / ceiling escape | was 0.05; даёт 0.85·Rmax | ↑ усиливает bounce |
| L≥MaxL/2 | undershoot TipR-down pre-ready | keep-guard asym50 fires | документировано | ↓ ломал keep |
| SoftCold Need→0 | accept_run | train complete | R06 anti false-PASS | **не снимать** |

Главный waste D после length-escape: **bounce** `1e11↔0.85·Rmax` от TipR-down при перелёте@Rmax (в т.ч. MaxL), не SyncTol.

## B. Осцилляция = waste

- PASS keep (asym50/ltz50/br50/fs25): финал TipR@Rmax **0**; путь midband→CanonRmin→Need=0 **без** потолочного bounce.
- D-core P12b: prolonged Rmax; mixed `1e11+0.85e11` после paced down; **0** bounce→Need=0.

Вердикт: длительная потолочная осцилляция для SoftCold **always waste**.

## C. Need vs метрики

Need=0 = EOL(+PostTune); Acc/fires = Test gate (ортогональны). SoftCold PASS при Need=1 **запрещён**. Diagnostic gate при incomplete допустим только как note, не как SoftCold PASS.

## D. Anti-bounce (эта волна)

При TipR@Rmax и amp перелёт (`dt<0`): **hold** TipR всегда; length grow только при `L<MaxL`. TipR-down с потолка только при недолёте (`dt≥0`) и L≥MaxL/2.

См. [`AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md`](AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md).
