# D — Rmax overshoot: length escape (W3c)

Дата: 2026-10-06.  
Срез до фикса: SoftCold rematrix PARALLEL 13 PASS / 36 FAIL · Console `8589daff…` · PulseLib `b32d715` (W3 hold).

**Актуальная проверка масштаба D-кейсов (2026-10-08):** [`D_CASES_TIMESCALE_INVESTIGATION.ru.md`](D_CASES_TIMESCALE_INVESTIGATION.ru.md) сопоставляет `InputPattern`, `EstDelayPerSeg`, RC-параметры сегментов, `MaxDendriteLength` и сохранённые итерационные трассы. Она отделяет старый default-5ms случай (`L≈97/100`) от остаточного `Rmax + amp overshoot + рассинхронизации` после калибровки (`Need=1`).

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

### P12 finals (amp_dt) — диагноз после W3d

| case | TipR | L | amp_dt | LastAbsDt | блокер |
|------|------|---|--------|-----------|--------|
| `pa00` / `phase6_*` / `tn` | `1e11×2` | `97 82 25 1` | **`+` undershoot** | `~0.47 / 0.40` | W3 down-step только при `ready_for_r_tune` |
| `psi01_050` | `1e11×2` | **`100 100` MaxL** | **`-` overshoot** | `~0.23 / 0.31` | W3d не растит; W3 hold запрещает TipR-down |

## W3e / W3f (2026-10-07) — TipR сходит с Rmax после length-escape

См. также [`AMPNORM_W3_RMAX_HOLD.ru.md`](AMPNORM_W3_RMAX_HOLD.ru.md) (W3: down-step только при `dt≥0`).

**W3e (primary):** TipR@Rmax + dwell≥3 + `dt≥0` + `!pending_grow` + `DendStatus==0` + **`L ≥ MaxL/2`** → TipR `×(1−0.15)` **до** `ready_for_r_tune`. Не срабатывает на overshoot и во время pending length grow. Min-L: после P12v1 keep `asym50` FAIL (`fires=1e6` expect `1e7`) при TipR@Rmax на `L~49`; D stuck на `L≳80`.

**W3f (narrow, psi01):** TipR@Rmax + dwell≥3 + `dt<0` + `L≥MaxL` → paced TipR-down (cooldown `kRmaxOvershootLengthCooldown` + reset dwell). **Не** latched perpetual descent; при `L<MaxL` остаётся только W3d length grow (W3 hold).

**Инварианты:**
1. `dt<0 && L<MaxL` → никогда TipR-down (только length).
2. W3f не чаще чем cooldown + полный re-dwell.
3. W3e не down-step при `DendStatus==1` / `RmaxOvershootLengthGrow`.
4. ApplyPending Rmax grow: keep TipR@Rmax / no feedforward.
5. Twin base + Branch.

**Код:** `NNeuronTimeLearner.cpp` / `NNeuronTimeLearnerBranch.cpp` — блок после обновления `RmaxDwellCount`, до гейта `ready_for_r_tune`; флаг `escaped_rmax_this_call` блокирует double down-step в ready-path.

**Partial** (Console `af12e954…`, `SKIP_REGISTRY_APPLY=1`, `STALL_AUTOSAVE_N=8`):

| волна | результат |
|-------|-----------|
| P12b D-core | **0/5** FAIL — TipR `1e11↔0.85·Rmax`, Need=1, `tipr_class=other` |
| P12b keep | 6/8 PASS; `asym50`/`ltz50_gen` flake (усечённый CSV `nrows=6–7`) |
| P2 retry PARALLEL=2 | `asym50`+`ltz50_gen` **2/2 PASS** → keep **8/8** |
| P4 objective | **3/3 FAIL** как ожидалось (`br25_on`, `fs50_preinh`, `asym25`) |

Ворота full 49: **закрыты** (D <4/5). Нужна следующая C++-итерация против ceiling-осцилляции, не registry.

## Anti-bounce (2026-10-07) — hold вместо W3f TipR-down @MaxL+overshoot

**Мотив:** W3f paced TipR-down при `dt<0 && L≥MaxL` вернул sterile bounce `1e11↔0.85·Rmax` (waste wall-time без Need→0). SoftCold gate не ослаблять.

**Код:** ветка overshoot@Rmax+`L≥MaxL` → **HOLD** TipR (latch dwell / `ResistanceStatus=1`), без `ApplyComputedResistance`. W3e undershoot down-step (`dt≥0`, `L≥MaxL/2`) сохранён. Инвариант: `dt<0 && at_r_max → never TipR-down` (length DOF только при `L<MaxL`). Twin base+Branch. Console SHA `dde07ac6…`.

**Partial P12** (`SOFTCOLD_antibounce_P12`, PARALLEL=6, `SKIP_REGISTRY_APPLY=1`, done 11:57Z):

| группа | результат |
|--------|-----------|
| keep×8 | **8/8 SoftCold** после solo `asym50` (PARALLEL CSV flake; финал Need=0+canon+mid=cpp — см. Inv3) |
| D×5 | **0/5 PASS** — Need=1, TipR primary @Rmax |
| bounce L≥60 (monitor / D workdirs) | **~0** переходов primary `1e11↔0.85` (цель anti-bounce) |

### Residual class (финал live TipR / L / amp_dt)

| case | TipR₀ | L₀ | amp_dt₀ | LastAbsDt₀ | класс |
|------|-------|----|---------|------------|-------|
| `pa00_baseline` | `1e11` (d1=`0.85e11`) | 87 | −0.009 | ~0.36 | **D_algo_open** |
| `phase6_thr_only` | `1e11` | 72 | −0.017 | ~0.22 | **D_algo_open** |
| `phase6_480` | `1e11` | 73 | −0.017 | ~0.22 | **D_algo_open** |
| `tn_classic` | `1e11` | 89 | −0.008 | ~0.39 | **D_algo_open** |
| `psi01_050` | `1e11` | **100 MaxL** | −0.041 | ~0.23 | **D_objective** |

`D_waste_fixed` на D-core **нет**. Waste-bounce снят; SoftCold D не сходится.

**P4** (`SOFTCOLD_antibounce_P4`, done 12:23Z): **3/3 FAIL** как ожидалось — gate не ослаблен.

### Residual investigate 1–3 (2026-10-07) — вердикты

**Inv1 (`D_algo_open`, pa00 / phase6_480):** W3d **apply работает** (L cold→70–90). Код arm→`ApplyPending`→clear flag / keep TipR@Rmax согласован; forced `delta=1` после anti-overshoot OK. Остаётся overshoot + LastAbsDt ≫ SyncTol×4 → W3e (`dt≥0`) не армится. **Не impl-bug** arm/apply/restore → **algo/физика** (аттенюация/синх при D SyncTol). C++ не меняли.

**Inv2 (`psi01` objective):** diag [`scripts/diag_psi01_sync_as_keep.py`](../../../Bin/Configs/SpikeSamples/StructTrain/scripts/diag_psi01_sync_as_keep.py) — SyncTol/EstDelay как keep в work only. Итог: TipR остаётся @CanonRmin (нет потолка Rmax), L→MaxL, amp_dt&lt;0, Need≠0. SoftCold FAIL. Путь **не** MaxL-hold bug. **D_objective подтверждён** (чувствительность Sync/EstDelay/паттерн). Production XML не меняли.

**Inv3 (`asym50` Need=1 polls):** финальный Train XML **Need=0** + TipR canon; Test flag landscape_ok=1 mid=cpp. Polls `Need=1 flag=1` = autosave lag до flush. SoftCold **PASS** (accept_run). Keep **8/8**. Не регресс anti-bounce.

**Условный фикс:** нет доказанного impl-bug AmpNorm/hold → **код не трогали**.

**Full49 baseline (user override 2026-10-07/08):** SoftCold **13 PASS / 36 FAIL** на Console `18f0ef41…` / PulseLib `dc2866a` — [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md). Registry обновлён. **`D_algo_open` / E1–E3 по-прежнему DEFERRED** (матрица не открывает AmpNorm-фикс).

Следующая AmpNorm-итерация: algo для `D_algo_open` (как получить `dt≥0` @Rmax при L&lt;MaxL без TipR-down на overshoot) и отдельный param-policy для `D_objective`.

## Вне скоупа

LandscapeOk / `br25_on` / `fs50_preinh` / flat A / silent-mid gen (Need→0 + gate).
