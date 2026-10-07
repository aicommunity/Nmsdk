# D-core vs keep: archive Train parameters (objective axis)

Дата: 2026-10-07. Снято с archive `Train/Parameters_00.xml` (до soft-cold reset TipR/L).

| case | MaxL | Rmax | SyncTol | EstDelay | Gain | span / notes |
|------|------|------|---------|----------|------|----------------|
| `pa00_baseline` | 100 | 1e11 | **0.02** | **0.01** | 0.4 | PhaseA span25 |
| `phase6_thr_only` | 100 | 1e11 | **0.02** | **0.01** | 0.4 | span480 |
| `phase6_480` | 100 | 1e11 | **0.02** | **0.01** | 0.4 | span480 PostTune |
| `tn_classic` | 100 | 1e11 | **0.02** | **0.01** | 0.4 | TimeNeuron |
| `psi01_050` | 100 | 1e11 | **0.02** | **0.01** | 0.4 | preinh050 |
| `asym50` | 100 | 1e11 | **~0.00208** | **0.002** | 0.4 | keep |
| `ltz50_gen` | 100 | 1e11 | **~0.00208** | **0.002** | 0.4 | keep |
| `fs25_gen` | 100 | 1e11 | **~0.00104** | 0.005 | 0.4 | keep |
| `br50_gen` | 100 | 1e11 | **~0.00208** | (var) | 0.4 | keep Branch |

**Вывод:** MaxL/Rmax одинаковы. D отличается **паттерном** и более крупными SyncTol/EstDelay. Residual после anti-bounce при hold@Rmax + перелёт + `L≥MaxL` + keep зелёный → кандидат `D_objective` (не «мало MaxL»).

### Diag `psi01_sync_as_keep` (2026-10-07)

Скрипт: `Bin/.../scripts/diag_psi01_sync_as_keep.py` (work-only patch SyncTol=`0.00208333`, EstDelay=`0.002`; production archive не трогали).

| | TipR | L | amp_dt | Need | SoftCold |
|--|------|---|--------|------|----------|
| antibounce psi01 | @Rmax | 100 | −0.041 | 1 | FAIL (`D_objective`) |
| diag sync_as_keep | **@CanonRmin** | 100/100/100 | −0.05…−0.10 | 1 | FAIL |

**Вердикт:** Sync/EstDelay как keep **меняет путь** (нет потолка Rmax), но Need→0 не даёт. MaxL-hold impl-bug **не** подтверждён. Param-policy для D — отдельный план; XML production не менять в этой волне.

Артефакт: `_repro/diag/psi01_sync_as_keep/last_result.json`.

Критерий меток: см. anti-bounce plan / [`AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md`](AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md).
