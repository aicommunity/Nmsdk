# AmpNorm asym50 keep-slog — TipR@Rmin Need=1

Дата: 2026-10-01.  
Bundle: `asym50_preinh_20261001T052512Z` · log: `metrics/AMPNORM_asym50_keepslog.log`.

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

## Fix (W2.2)

`kRminLengthTolFactor=2`: при TipR@Rmin принимать `LastAbsDt ≤ 2×SyncTolerance` в `AllDendritesSynced` / `AllSynapsesNormalized`.

## Полный хвост

(дописать после NM exit)
