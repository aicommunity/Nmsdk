# StructTrain experiments — reference

## posttune_verify cases → канон

| `--case` | Каноническое Имя (реестр) | Work-клон | TipR expect | Train t (model s) |
|----------|---------------------------|-----------|-------------|-------------------|
| `br25_on` | `EXP_br_span25_packA_gen_C1e9` | `…_posttune` | canon | 320 |
| `br25_off` | `EXP_br_span25_packA_gen_C1e9` | `…_posttune_off` | legacy | 320 |
| `asym25` | `EXP_span25ms_packA_gen` | `…_posttune` | flat | 160 |
| `asym50` | `EXP_span50ms_packA_gen` | `…_posttune` | canon | 640 |
| `br100_keep` | `EXP_br_span100_packA_gen_C1e9` | `…_posttune_keep` | keep | 640 |
| `br100_search` | `EXP_br_span100_packA_gen_C1e9` | `…_posttune_search` | search | 2400 |
| `phase6_480` | `Phase6/EXP_480_gen_tiprmin` | `Phase6/…_posttune` | canon | 900 |

Skip-train gold control: тот же канон Branch25, протокол `SkipTrainGold` (не отдельный case-алгоритм).

## Протоколы

| Протокол | Смысл |
|----------|--------|
| `GoldTest` | Готовые веса на диске, канонический Test |
| `SkipTrainGold` | Контроль контура на frozen весах без Train |
| `SoftCold+PostTune` | Soft-cold Train + PostTune + gate |
| `SoftCold+PostTuneOff` | Soft-cold, `EnablePostTrainTuning=0` |
| `MatrixClone` | Pack B/C matrix-only, не независимое cold |

## Acc / Цель

- Acc = успешные пробы из 8.
- Цель = срабатывание на target. При Acc 8/8 → `да`. При Acc&lt;8/8 колонка обязательна (`да`/`нет`/`—`).
- Нет CSV gate → Acc/Цель/Режим = `—`.

## CLI

```bash
python3 Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py --case br25_on
python3 Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py --case all
# GoldTest NOT_RETESTED (no Train):
python3 Bin/Configs/SpikeSamples/StructTrain/scripts/gold_retest_batch.py \
  --manifest Bin/Configs/SpikeSamples/StructTrain/_repro/NOT_RETESTED_manifest_20260925.txt
# SoftCold wave C1/C2:
WAVE=C1 bash Bin/Configs/SpikeSamples/StructTrain/scripts/softcold_c_batch.sh
# debug only:
python3 …/posttune_verify.py --case br25_on --allow-salvage
python3 …/posttune_verify.py --case br25_on --use-archive-inplace
```

Console path (Linux): `Bin/Platform/Linux/NeuroModelerConsole`.

Extra SoftCold `--case` ids (wave C): `br50_gen`, `br*_preinh`, `br*_nextseg`, `br480_*`, `asym*_preinh`, `asym100_*`, `phase6_thr_only` / `preinh250` / `ltzcal_twin`, `fs*`, `ltz*`, `pa*`, `tn_classic`, `psi*` — see `CASES` in `posttune_verify.py`.
