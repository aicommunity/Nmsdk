# D — Rmax overshoot: length escape (W3c)

Дата: 2026-10-06.  
Срез до фикса: SoftCold rematrix PARALLEL 13 PASS / 36 FAIL · Console `8589daff…` · PulseLib `b32d715` (W3 hold).

## Физика

`amp_dt = Initial − MaxAmp`. При TipR@ResistanceMax и `amp_dt < 0` (overshoot) R поднять нельзя. Down-step усиливает amp → re-climb → осцилляция `1e11↔0.85·Rmax` (снята W3 hold). Hold без DOF → ceiling freeze / Need=1 (корзина D).

**Рабочая степень свободы:** рост `DendriteLength` (cable attenuation) при hold R@Rmax; после `dt≥0` — штатный W3 undershoot down-step к CanonRmin.

**Отклонено:** latched R-descent (хуже overshoot + конфликт с W1 raise@Rmin).

## Код (W3c)

- `ChangeSynapseResistanceStatus`: overshoot-hold → `DendStatus=1` + cooldown; R не трогать; **сброс `DendStatus=-1`** на hold-тиках; **`restore_dend_status`** сохраняет `DendStatus=1` если `RmaxOvershootLengthGrow` (иначе конец функции откатывал к 0 после `DendStatus.assign(0)` в Finish).
- `ApplyPendingDendriteLengthChanges`: bypass settle; если флаг и `DendStatus==0` → force 1; forced `delta=1`; **skip** feedforward + keep TipR@Rmax; **запрет shrink при TipR@Rmax**.
- Twin: base + Branch.

## Selective note (2026-10-06)

Первый selective SHA `4c3da052…` / `da3a6424…`: keep 9/9 rc=0; D-якоря TipR@`1e11` — grow не apply’ился из‑за DendStatus restore. `phase6_480` SoftCold-source `EXP_480_gen_posttune` без EstDelay → C++ 0.005 + NM `-S`.

Фиксы волны apply+harness: DendStatus preserve; `sync_estdelay_from_gold` + patch posttune 0.01; `stall_autosave_n=8` abort TipR@Rmax + L stagnant.

## EstDelay gaps

| case | archive (SoftCold root) | EstDelay |
|------|-------------------------|----------|
| `phase6_480` | `EXP_480_gen_posttune` (+ gold tiprmin) | 0.01 |
| `tn_classic` | `TimeNeuronTimeLearner` | 0.01 |

## W3d (2026-10-06) — escape без `length_settled`

**D3 selective** (`SOFTCOLD_d_escape_selective_d3`, Console `24b5ac81…`): keep 2/2 PASS; D-якоря FAIL stall. Финал D:

- TipR ≈ `3.15e9 · 1e11 · 4.95e7 · 8.6e7`, L=`97 51 25 1`
- Live d1: `amp_dt≈-0.011`, `last_abs_dt≈0.0855` при TipR@`1e11`
- Порог `length_settled` @Rmax: `SyncTol×kRminLengthTolFactor` = `0.02×4 = 0.08` → d1 **не** settled

W3c arming (`RmaxOvershootLengthGrow`) жил только внутри `ready_for_r_tune = length_settled && !DendStatus`. При `!ready` — только `ResistanceStatus`, grow не ставится → multi-dend ceiling freeze.

**Фикс W3d** (base + Branch `ChangeSynapseResistanceStatus`):

- Rmax dwell / overshoot length-escape армируется **до** гейта `ready_for_r_tune`, если TipR@Rmax и `dt < -eps`.
- Обычный R-tune (damped-P, midband, W1@Rmin, W3 undershoot down-step) — по-прежнему только при `ready_for_r_tune`.
- Console после билда: `4421a660…` (полный SHA в metrics / provenance).

**Partial retest P12+P4** (`SOFTCOLD_w3d_P12` / `P4`, PARALLEL=6): keep/branch **8/8 PASS**; D-core **0/5 PASS** (stall @Rmax, L вырос до ~`97 82` / psi `100 100`, TipR не ушёл с `1e11`); objective P4 **3/3 FAIL** как ожидалось. Ворота full 49 — не открывать.

## Вне скоупа

LandscapeOk / `br25_on` / `fs50_preinh` / flat A / silent-mid gen (Need→0 + gate).
