# Покрытие осей экспериментов и gaps (2026-10-19)

Канон группировки: [RESULT_GROUPING_HIERARCHY.ru.md](RESULT_GROUPING_HIERARCHY.ru.md).  
Матрица: ~313 кейсов в `TimeLearnerMatrix/matrix.json`. Полный прогон вне скоупа; ниже — gaps для cold §4 и структуры §0b/§7.

## Оси

| Ось | Значения |
|---|---|
| Trainer | Classic / Branch |
| Mode | N0 / N1 (равн. M0/M1 track) |
| Span | 25 / 50 / 100 / **480** (480 cold отложить) |
| NeuronModel | baseline W10/W01, AsymRm, FastSpan, LTZ, FastResponse |
| Mod | gen, preinh, nextseg, PSI |
| PostTune | ON / OFF (парный протокол) |

## Что закрыто контролем

| Trainer×Mode | Span | NeuronModel | Mod | Статус |
|---|---|---|---|---|
| Branch×N1 | 25 | baseline | nextseg | PASS×3 |
| Branch×N1 | 50/100 | baseline | preinh | PASS×3 |
| Branch×N1 | 25 | baseline | gen/preinh | Need=0; ON silence; OFF gen detected (A2.1) |
| Branch×N1 | 50/100 | baseline | nextseg | Incomplete D6 |
| Branch×N0 | ~480 | baseline W04 | PSIoff | Need=1 peak-blind |
| Classic×N0 | 25/50 | baseline W01 | PSIoff | N+1: stall / Need0-silent |

## Gaps

| Gap | Действие |
|---|---|
| **Branch×FastSpan** — конфигов нет | §0b: 12 мин. EXP в `SelectivityBranchFastSpan/`, W48 |
| Classic FastSpan: нет `fs50_gen` в matrix | §7: `W12_HIST_fs50_gen` → `EXP_span50ms_fast_C1e9` (каталог есть) |
| Classic FastSpan N0 близнецы | §7 имена |
| `br100_gen` baseline | §7 под SelectivityBranch |
| Classic Asym @25 в cold фикса | §4B `W09_HIST_asym25` |
| Classic N1 short в cold фикса | §4D ≥1 кейс |
| Span 480 cold | **отложить**; в matrix оставить |

## ID cold §4 (после PostTune-фикса)

**A Branch baseline:** `W10_HIST_br25_gen`, `W10_HIST_br25_preinh`, `W10_HIST_br50_gen` (+ PASS×3 §5).  
**B Asym:** `W09_HIST_asym25` (+ preinh slot).  
**C FastSpan Classic:** `W12_HIST_fs25_gen`, `W12_HIST_fs25_preinh`, ≥1@50, ≥1@100.  
**D W01:** CL25/CL50 N0 + ≥1 N1 short.  
**E Branch×FastSpan:** `W48_BR_FS25_N1_gen` + (preinh\|nextseg).

## Имена §0b (минимум 12 EXP)

Корень: `Bin/Configs/SpikeSamples/StructTrain/SelectivityBranchFastSpan/`  
`EXP_br_fs_span{25,50,100}_{gen,preinh,nextseg}_N1_C1e9` (9) +  
`EXP_br_fs_span25_{gen,preinh,nextseg}_N0_C1e9` (3).  
Matrix ids: `W48_BR_FS{25,50,100}_N1_{gen,preinh,nextseg}`, `W48_BR_FS25_N0_*`.

## §7 расширение

Полная сетка Branch×FastSpan 18 EXP (N0@50/100); Classic FastSpan симметрия gen/preinh; `br100_gen`; 480 в spec без cold.
