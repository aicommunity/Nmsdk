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

## D_obj.2 Переклассификация §4.1 D (22)

| Метка | Cases |
|-------|-------|
| **D_algo_open DEFERRED** | `pa00_baseline`, `phase6_thr_only`, `phase6_480`, `tn_classic` |
| **D_objective** | `psi01_050` (доказано); кандидаты PSI с TipR@Rmin+Need: `psi15_270`, `psi33_300`, `psi34_400`, `psi35_400` (по lookback — **D_unclassified** до SNAP) |
| **D_unclassified** | `pa01_ltz_sweep`, `pa02_ltzone_avg`, `pa06_ltzone_int`, `psi14_260`, `psi21_100`, `psi31_200`, `psi32_300`, `phase6_ltzcal_twin`, `phase6_preinh250`, `br480_preinh`, `ltz100_preinh`, `ltz50_preinh`, `ltz25_preinh` |

Критерий повышения до `D_algo_open`: @Rmax + L&lt;MaxL + grow был + overshoot (как Inv1). Без SNAP — не повышать; остаются unclassified или DEFERRED только для четырёх якорей.

## Follow-up (не Open Gaps)

- EstDelay / L=`97…` Phase6 vs live gold L
- Param-policy документ для SyncTol на PSI/PhaseA
- Следующая AmpNorm-итерация **только** после снятия DEFERRED с `D_algo_open`
