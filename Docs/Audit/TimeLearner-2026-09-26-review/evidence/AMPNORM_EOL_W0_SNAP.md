# AmpNorm / EOL — W0 SNAP summary (SoftCold matrix HEAD)

Источник: локальный `metrics/SOFTCOLD_full_matrix.log` (не в git) + `SOFTCOLD_HEAD_rcs.txt`.  
Дата извлечения: 2026-10-03. Полный slog — вне git (evidence policy).

**Актуальный full49 HEAD SNAP (2026-10-08):** [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md) — 13/36, D=20 E=6 B=4 A=3 N=1 G=2. Ниже — исторический W0 baseline.

**Инвариант W0:** критерии Done не менялись на этапе извлечения; таблица = baseline до W1–W3.

## Сводка корзин

| Bucket | Count | Симптом (TipR / Need) |
|--------|------:|------------------------|
| D | 22 | TipR → ~1e11 (Rmax) или runaway ≫Rmin, Need=1 |
| E | 6 | TipR@Rmin (`2e7`), Need=1, gate≠0 |
| B | 7 | TipR mid-band (2e7…8e7), Need=1 |
| A/C/G/other | 6 | SoftColdOff / Keep-Search / flat / NonSeparable |
| PASS | 8 | rc=0 (controls) |

Арифметика FAIL: 22+6+7+3+1+2 = 41 (N=`br25_on` пересекает E по TipR@Rmin + gate).

## PASS controls (keep)

| case | rc | TipR (last autosave) | L | gate |
|------|----|----------------------|---|------|
| `asym50_preinh` | 0 | `2e7 2e7 2e7 8.6e7` | `27 22 15 1` | 0 |
| `asym25_preinh` | 0 | `2e7 2e7 2e7 8.6e7` | `14 11 7 1` | 0 |
| `asym50` | 0 | `2e7 2e7 2e7 8.6e7` | `27 22 15 1` | 0 |
| `br50_gen` | 0 | `2e7 2e7 2e7 8.6e7` | `15 12 6 1` | 0 |
| `br100_preinh` | 0 | `2e7 2e7 2e7 8.6e7` | `22 18 11 1` | 0 |
| `br25_nextseg` | 0 | `2e7 2e7 2e7 8.6e7` | `7 6 4 1` | 0 |
| `br50_preinh` | 0 | `2e7 2e7 2e7 8.6e7` | `15 12 6 1` | 0 |
| `ltz50_gen` | 0 | `2e7 2e7 2e7 8.6e7` | `27 22 15 1` | 0 |

## E — TipR@Rmin, Need=1 (W1)

| case | TipR | L | gate | Гипотеза до правки |
|------|------|---|------|--------------------|
| `asym100_gen` | `@Rmin` | `54 43 27 1` | 1 | AmpNorm/sync гейт; ResSt или dt/length |
| `asym100_preinh` | `@Rmin` | `54 43 27 1` | 1 | то же |
| `ltz100_gen` | `@Rmin` | `54 43 27 1` | 1 | то же |
| `ltz25_gen` | `@Rmin` | `14 11 8 1` | 1 | то же |
| `fs50_preinh` | `@Rmin` | `11 10 6 1` | 1 | то же |
| `br25_on` | `@Rmin` | `7 6 4 1` | 1 | E∩N; NonSeparable отдельно |

**W1 гипотеза:** `AllSynapsesNormalized` блокирует при `ResistanceStatus=1` даже при `at_r_min&&length_ok`, либо `|dt|` в osc_band с mild overshoot (`dt<=0`) не проходит `dt_positive`. Узкие правки: не блокировать Status@Rmin+length_ok; Done при `|dt|<=osc_band`@Rmin.

## B — mid-band stall (W2)

| case | TipR (notable) | gate | Гипотеза |
|------|----------------|------|----------|
| `fs25_gen` | dend2≈`2.61e7` | 0 | B1: NoImprove→Status=0 freeze (keep-slog: `|dt|>5` hits=0) |
| `fs25_preinh` | dend2≈`3.96e7` | 0 | то же |
| `fs100_gen` | dend2≈`7.63e7` | 1 | mid + gate |
| `fs100_preinh` | dend2≈`3.22e8` | 1 | mid/runaway edge |
| `br25_preinh` | dend2≈`6.76e7` | 0 | B4 Branch: нет midband→Rmin; NoImprove→freeze |
| `br480_nextseg` | dend0=`8.6e7`, mid | 1 | Branch mid |
| `br480_tiprmin` | dend1≈`2.11e7` | 1 | Branch mid |

**W2 гипотеза:** base — убрать freeze Status=0 при R>Rmin, directional NoImprove step + midband walk; Branch — отдельный порт (не copy-paste verbatim).

## D — Rmax / runaway (W3)

Representative: `phase6_480`, `tn_classic`, `pa00_baseline`, `psi01_050`, `ltz25_preinh`, `ltz50_preinh`, `br480_preinh`, … — TipR=`1e11` на ≥1 dend, Need=1.

**W3 гипотеза:** damped-P + pathological amp гонит к `ResistanceMax`; нужен bounded Rmax-dwell recovery (не blind Rmax→Rmin jump). Успех волны — полная D=22, не только smoke.

## Harness (диагностика, не Done)

`posttune_verify._snap_tipr_live`: TipR/L + `amp_dt` / `res_st` / `no_imp` / `last_abs_dt` из StatisticLog traces.  
C++ `EolGateAudit` (EnableDebug): synced/normalized + per-dend TipR/dt/LastAbsDt/ResSt/NoImp.

## Решение до кода (W0 → W1)

1. E: править AmpNorm Done predicates @Rmin (не второй слепой bypass без length_ok).
2. B: NoImprove directional step; Branch midband отдельно.
3. D: RmaxDwell≥limit → step down; после подтверждения на smoke — полный D.
