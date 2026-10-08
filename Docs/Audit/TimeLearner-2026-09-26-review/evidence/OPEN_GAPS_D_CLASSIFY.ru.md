# Open Gaps — D_objective и переклассификация D (без D_algo_open)

Дата: 2026-10-07. Phase D_obj.  
`D_algo_open` **DEFERRED** — не чинить. EstDelay rewrite PhaseA — follow-up, не эта фаза.

## DEFERRED рядом с E

Фикс AmpNorm Done для **E1/E3** и C++ под `psi01` overshoot@Rmin — **отложен** (2026-10-07). См. [`OPEN_GAPS_E_B.ru.md`](OPEN_GAPS_E_B.ru.md). `D_algo_open` по-прежнему DEFERRED отдельно.

## D_obj.1 psi01_050

Live SNAP (diag sync_as_keep / SoftCold work):

| | |
|--|--|
| TipR | CanonRmin `2e7×3` |
| L | MaxL `100×3` |
| amp_dt | **&lt;0** (overshoot) |
| LastAbsDt | 0.06–0.30 ≫ SyncTol×4 |
| Need | 1 |

Метки: **D_objective** + EOL **E3** (нет Done при overshoot@Rmin) + **E1** (length sync).  
Production XML не менять. Param-policy: Sync/EstDelay меняют путь (потолок → Rmin), но Need→0 не дают — basin/паттерн, не MaxL-hold bug.  
C++ AmpNorm hold **не** патчить под psi01 в этой волне.

## D_obj.2 Переклассификация после full49 HEAD SNAP

Источник: [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md) — **D=20** все с TipR≥`1e11` на ≥1 dend.

| Метка | Cases (full49) |
|-------|----------------|
| **D_algo_open DEFERRED** | `pa00_baseline`, `phase6_thr_only`, `phase6_480`, `tn_classic` (+ близкие `phase6_ltzcal_twin`, `phase6_preinh250`) |
| **D ceiling (PSI/PhaseA/ltz)** | `pa01_ltz_sweep`, `pa02_ltzone_avg`, `pa06_ltzone_int`, `psi01_050`, `psi14_260`, `psi15_270`, `psi21_100`, `psi31_200`–`psi35_400`, `ltz100_preinh`, `ltz50_preinh` |
| **D_objective (diag, не full49 path)** | `psi01_050` на diag Sync/EstDelay=keep шёл @Rmin; в full49 production XML снова **ceiling @Rmax** |

Критерий `D_algo_open`: @Rmax + L&lt;MaxL + grow + overshoot (Inv1). DEFERRED не снят full49.

## Follow-up (не Open Gaps)

- EstDelay / L=`97…` Phase6 vs live gold L
- Param-policy документ для SyncTol на PSI/PhaseA
- Следующая AmpNorm-итерация **только** после снятия DEFERRED с `D_algo_open`
