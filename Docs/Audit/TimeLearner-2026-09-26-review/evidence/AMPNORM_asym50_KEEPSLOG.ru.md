# AmpNorm asym50 keep-slog — TipR@Rmin Need=1

Дата: 2026-10-01.  
Bundle: `asym50_preinh_20261001T052512Z` · log: `metrics/AMPNORM_asym50_keepslog.log`.  
Console: **старый** (до `kRminLengthTolFactor` / PulseLib `bb438c4`).

## Вердикт (poll#20 SNAP)

| | |
|--|--|
| TipR live | **`2e7×3 8.6e7` (=Rmin)** |
| L | `27 22 15 1` (gold-like) |
| Need | 1 |
| SyncTolerance | **0.00208333** (tight) |
| LastAbsDt | `0.0031, 0.0004, 0.0001, 1.501` |
| AmpDt | `0.042, 0.025, 0.016, 0` |
| ResSt / NoImp | `0,0,0,0` / `0,7,11,0` |

## Root cause

`length_ok` false на dend0: **LastAbsDt[0]=0.0031 > SyncTolerance=0.00208**.  
`at_r_min && dt_positive` уже истинны, но EOL требует `length_ok` → Need=1.

Не: AmpDt skip `|dt|>5`; не: TipR mid-band.

При `2×SyncTol` dend0 проходит (`0.0031 ≤ 0.00417`).

## Fix (W2.2)

`kRminLengthTolFactor=2`: при TipR@Rmin принимать `LastAbsDt ≤ 2×SyncTolerance` в `AllDendritesSynced` / `AllSynapsesNormalized` (PulseLib `bb438c4`).

## Полный хвост (NM exit)

| | |
|--|--|
| Train | poll **#511** Need=1, slog **~7.18 GiB**, TipR live **весь прогон** `2e7×3 8.6e7` |
| Gate | **rc 0** (`skip-tipr-mid`, selective fires=`10000000`, Acc 8/8) |
| Verify | **FAIL** `train_incomplete:exited` + **Need=1** (`POSTTUNE_VERIFY_RESULT.md`) |
| Wall | ~4.5 ч (`posttune_exit=0`) |

Этот прогон — только диагностика на pre-fix Console; SoftCold asym* — на Console после `bb438c4`.

## Следующий инкремент (2026-10-01, после autosave)

Classic `kRminLengthTolFactor=2` уже в `bb438c4`. Зеркало в **TimeLearnerBranch** `AllSynapsesNormalized` (тот же Rmin length override) — SoftCold `br*` / PulseLib `b29b595`.

Harness: `--autosave-model-s 10` закрывает gap свежести Need XML.

### Live SoftCold `asym50_preinh` (autosave wave)

Console `e018c024…` · poll#10 `AUTOSAVE_SEEN`: TipR **`2e7×3 8.6e7`**, L≈`27 22 15 1`, Need=1 — корзина B всё ещё на якоре; матрица продолжает очередь (`SOFTCOLD_full_matrix.log`).
