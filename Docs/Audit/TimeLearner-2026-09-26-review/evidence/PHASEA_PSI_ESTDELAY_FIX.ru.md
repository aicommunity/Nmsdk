# PhaseA / PSI EstDelayPerSeg SoftCold fix

Дата: 2026-10-05.  
Скрипт: `Bin/Configs/SpikeSamples/StructTrain/scripts/patch_phasea_psi_estdelay.py`.  
Паттерн: [PHASE6_ESTDELAY_FIX.ru.md](PHASE6_ESTDELAY_FIX.ru.md).

## Проблема

SoftCold-source PhaseA/PSI без `EstDelayPerSeg` → runtime default `0.005`.  
При Dissync≈0.48 SoftCold L → `97 81 49` вместо gold.

## Формула

`T = (L_softcold_obs − 1) × 0.005` (из W4), `EstDelay = T / (L0_gold − 1)`.

| case | L0_gold | L_soft | T | EstDelayPerSeg |
|------|--------:|-------:|--:|---------------:|
| pa00_baseline | 49 | 97 | 0.48 | 0.01 |
| pa01_ltz_sweep | 49 | 97 | 0.48 | 0.01 |
| pa02_ltzone_avg | 49 | 97 | 0.48 | 0.01 |
| pa06_ltzone_int | 49 | 97 | 0.48 | 0.01 |
| psi01_050 | 49 | 97 | 0.48 | 0.01 |
| psi14_260 | 51 | 100 | 0.495 | 0.0099 |
| psi15_270 | 51 | 100 | 0.495 | 0.0099 |
| psi21_100 | 11 | 20 | 0.095 | 0.0095 |
| psi31_200 | 23 | 41 | 0.2 | 0.0090909091 |
| psi32_300 | 32 | 63 | 0.31 | 0.01 |
| psi33_300 | 33 | 67 | 0.33 | 0.0103125 |
| psi34_400 | 41 | 79 | 0.39 | 0.00975 |
| psi35_400 | 43 | 89 | 0.44 | 0.01047619 |

Правка: Train `Parameters_00.xml` + `Model_00.xml` в архивах-источниках (не `_work`). Phase6 не трогали.

## Smoke + full matrix (Console SHA16 `8589daff…`)

| case | SoftCold rc | live L | note |
|------|------------:|--------|------|
| pa00_baseline | 1 | `49 41 25` | EstDelay OK (≠`97 81 49`); TipR@Rmax Need=1 (D) |
| pa01_ltz_sweep | 1 | `49 41 25` | same |
| psi01_050 | 1 | `25 25 25` | length settled ≠97; TipR path still FAIL |

Phase6 (`0.01` / `0.0096`) не меняли. `phase6_480` в rematrix всё ещё L=`97 81 49` (отдельный EstDelay/Dissync хвост, не PhaseA/PSI).
