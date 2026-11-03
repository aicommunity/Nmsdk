# StructTrain experiments — исторический справочник

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

## Протоколы / Working

Лестница **Working**: SoftCold > SoftColdOff > SkipTrainGold > GoldTest ≈ MatrixClone.

| Протокол / Working | Смысл |
|--------------------|--------|
| SoftCold (`SoftCold+PostTune`) | Soft-cold Train + PostTune + gate (cold-from-scratch) |
| SoftColdOff | Soft-cold, `EnablePostTrainTuning=0` |
| SkipTrainGold | Контроль контура на frozen весах без Train |
| GoldTest | Готовые веса на диске, канонический Test |
| MatrixClone | Pack B/C matrix-only, не независимое cold |

**GoldTest PASS ≠ SoftCold.** Колонки реестра: **Working** (сильнейший PASS) + **LastCheck** (эта проверка). См. [PROTOCOL_WORKING_VS_LASTCHECK.ru.md](../../../Docs/Audit/TimeLearner-2026-09-26-review/evidence/PROTOCOL_WORKING_VS_LASTCHECK.ru.md).

## Acc / Цель

- Acc = успешные пробы из 8.
- Цель = срабатывание на target. При Acc 8/8 → `да`. При Acc&lt;8/8 колонка обязательна (`да`/`нет`/`—`).
- Нет CSV gate → Acc/Цель/Режим = `—`.

## Исторические запускатели

Таблицы выше сохраняют прежнюю семантику case/registry. Они не доказывают
современную приёмку алгоритма и не заменяют пять осей статуса текущего контура.
SoftCold/OpenGaps/T2/T4 shell entrypoints удалены из текущего Bin без wrappers.
Исходники доступны в Bin commit `39d811e5e0798eecf124f32356c9fc6edbe4538a`; точные пути и хеши:
[реестр миграции](../../../Docs/StructTrain/TimeLearner/SoftColdLauncherRetirement.ru.md).

Для нового задания использовать [корневой CLI](../../../Scripts/StructTrain/TimeLearner/README.ru.md)
с явными job/runtime manifests и только проверенными capabilities. Старый shared
`Bin/Platform` и команды posttune_verify/--case относятся к историческому протоколу.
Не возобновлять прежние очереди ради повторной генерации документации.
