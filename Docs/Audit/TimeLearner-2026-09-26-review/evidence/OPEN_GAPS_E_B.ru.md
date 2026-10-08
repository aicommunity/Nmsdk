# Open Gaps — Phase E / B (исследование)

Дата: 2026-10-07. Baseline после rebuild EolGateAudit: Console SHA16 `dded4dcec965b8e4` · PulseLib `3cefd64` + PeakSeen audit.  
Diagnostic: `OPEN_GAPS_W0_focused_manifest.txt` / remain6 → `metrics/OPEN_GAPS_W0*.log`.

Инварианты: не ослаблять SoftCold Need→0 / LandscapeOk; base≠Branch copy-paste; C++ только на доказанный предикат.

## DEFERRED — фикс E1/E3 (2026-10-07)

**Статус: отложено.** Не менять `AllSynapsesNormalized` / Done / SyncTol-policy / LandscapeOk ради SoftCold E.

| | |
|--|--|
| Почему не impl-bug | TipR→CanonRmin работает; keep PASS на том же learner; гейты отказывают по записанным правилам |
| E1 | LastAbsDt vs length_ok @Rmin — algo/пороги + паттерн/span |
| E3 | overshoot@Rmin без Done — dt-sign by design |
| W0 FAIL (rc=1) | `asym100_gen`, `ltz100_gen`, `ltz25_gen`, `fs50_preinh` |
| Также | `psi01_050` (E3∩D_objective) — param-policy отдельно; тоже без C++ Done-патча сейчас |

Возобновление — только отдельный план с явной политикой EOL (не `if (at_r_min) return true`).


## Phase E — TipR@Rmin, Need=1

### Контраст keep

`asym50`, `ltz50_gen` — SoftCold PASS (Need→0 + canon) на том же `NNeuronTimeLearner`.

### Якоря FAIL (HEAD rematrix) — предикаты по SNAP

| case | Learner | ID | SNAP gist | C++ эта волна |
|------|---------|-----|-----------|---------------|
| `asym100_gen` | base | **E1** | @Rmin, dt&gt;0, LastAbsDt~0.008–0.01 | **DEFERRED** |
| `ltz100_gen` | base | **E1** | LastAbsDt~0.02 @Rmin | **DEFERRED** |
| `ltz25_gen` | base | **E1** | W0 SoftCold rc=1; silent mid gate | **DEFERRED** |
| `fs50_preinh` | base | **E3** | dend2 amp_dt&lt;0 @Rmin | **DEFERRED** |
| `asym100_preinh` | base | PASS rematrix | — | вне E |
| `br25_on` | Branch | **N** | LandscapeOk | gate не трогать |
| `psi01_050` | base | **E3+E1** | MaxL + overshoot @Rmin | **нет** |

### Почему C++ не правим сейчас

1. **E1:** length_ok / SyncTol slack — не доказан «ложный» гейт vs жёсткий sync; слепое ослабление tol рискует keep.
2. **E3:** overshoot@Rmin без Done — by design dt-sign; `if (at_r_min) return true` запрещён.
3. Diagnostic SoftCold (`OPEN_GAPS_W0.log`) подтвердит HEAD; узкий фикс — отдельный план после policy.

## Phase B — mid-band TipR, Need=1

### Rematrix сдвиг

`fs25_gen` / `fs25_preinh` — SoftCold **PASS**. Исторический B1 не открывает fix-волну.

### Остаточный Branch B

| case | ID | SNAP | C++ эта волна |
|------|-----|------|---------------|
| `br25_preinh` | **B4** | mid TipR 6.76e7, ResSt=0, NoImp=3, \|dt\|~0.02 | код B4 recovery **уже** в Branch (~1183–1196); новый патч не дублировать — retest HEAD via diag |
| `br480_*` | B4 / partial | rematrix FAIL | retest после B4 verify |

Запрещено: безусловный force Rmin при `dt&lt;0`; не лечить `-t`.

## Итог E/B Open Gaps

Предикаты **названы** (E1/E3/B4/N). C++ AmpNorm controller **не** расширяли; только EolGateAudit PeakSeen/BestEffort (лог).

**Full49 HEAD (2026-10-08):** E-корзина SNAP = `fs50_preinh`, `asym100_gen`, `ltz100_gen`, `ltz25_gen`, `fs100_gen`, `br25_preinh` (TipR@Rmin/canon FAIL). `br25_preinh` на full49 — TipR@Rmin (не mid B4). Branch B: `br480_*` + `ltz25_preinh`. DEFERRED E1/E3 **не** снят. См. [`SOFTCOLD_FULL49_SNAP.md`](SOFTCOLD_FULL49_SNAP.md).
