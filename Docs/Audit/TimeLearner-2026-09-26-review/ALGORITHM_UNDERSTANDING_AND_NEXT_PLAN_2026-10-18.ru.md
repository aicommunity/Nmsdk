# Понимание алгоритмов обучения и план после P0

Дата: 2026-10-18.  
Срезы: PulseLib `e23f2e9` (+D7 seg-order gate), Console `.11` `9d8da6ad` / `.17` `26f0d6da`.  
PASS-остров + регрессия `.17`: `tl-m1-p0-regress-17-20261018-18-25` (3/3 PASS).  
M0 abort (D7): `tl-m0-c-w04-86m-p0-20261018-18-20` / `MANUAL_STOP.json`.

## 1. Как сейчас работает Branch TimeLearner (сжатая модель)

Обратный порядок пульсов (якорь N−1 → … → 0). На активном пульсе:

1. **Длина (L)** — подгонка delay по `Dissync` / `DendLastAbsDt` (`ChangeDendriteStatus`).
2. После structural ±1 — **scoped invalidate** sync только для пульсов `≤ edited`; якорь и более поздние остаются synced.
3. **Синапсы (N)** — Mode=0: early amp-collapse BE с пола **N≥8**, но **только если** `L[k]>L[k+1]` (seg_ok); иначе продолжать ±L. Cap **128**.
4. **TipR (Mode=1)** — параметрическая нормализация амплитуды после/параллельно структуре.
5. **Sync commit** требует PeakSeen + свежий length_ok (не stale Dissync после reopen) **и** seg-order.
6. **NoImprove** после реальных length-apply: best-effort stop (streak не сбрасывается на scoped edit; BE также не ставится при broken order).
7. **InvalidPeakNoRecovery** — refuse, если много burst’ов с peak, но без полезного действия (не пустые окна); Mode=1 length recovery при invalid peak + `|dt|>tol`.

PostTune TipR CanonRmin — отдельная фаза после Need=0; C++ Test калибрует mid. Train-candidate mid ≠ C++ Test mid (часто fire-all / silence vs selective).

## 2. Стабильный PASS-остров (C++ fires=`10000000`, Need=0)

| Case | L | Срезы |
|---|---|---|
| `W10_HIST_br25_nextseg` | `[7,6,4,1]` | `.11` P0 + `.17` regress |
| `W10_HIST_br50_preinh` | `[15,12,6,1]` | то же |
| `W10_HIST_br100_preinh` | `[21,18,11,1]` | M1-ext + `.17` regress |

## 3. Итог P0 по дефектам

| ID | После P0 (`e23f2e9`) | Остаток |
|---|---|---|
| D2 | refuse@3 снят (`invalid_peak=0`) | L-thrash `17↔18` @Rmin, Incomplete (`br25_preinh`) |
| D1 | early BE на pulse1 при N=8 | pulse2 всё ещё N=128; плюс **D7** |
| **D7** | обнаружен на M0 abort | BE[1]=1 при L=`[1,65,89,1]` → sync commit вечно ждёт `L[k]>L[k+1]`; фикс: BE∧seg_ok |
| D3 | без изменений | `br25_gen` Need=0 + C++ silence |
| D6 | без изменений | nextseg@50/100 peak_seen all0, L stuck1 |
| thrash | Active 1↔3 не вернулся | — |

## 4. Post-P0 реализация (в коде / evidence)

| Item | Статус |
|---|---|
| **P0b / D7** | ✅ unit+cold: BE∧seg_ok; M0 `tl-m0-d7-*` без deadlock; pulse0 peak-blind остаток |
| **P1 / D2** | ✅ TipR@Rmin × SyncTol×4 на invalid-peak path; cold Need=0; PASS regress ×3 |
| **P2 / D3** | ✅ evidence (CanonRmin + NonSeparable mid); `br25_preinh` теперь тоже silence-после-Need=0 |
| **P3 / D6** | ✅ evidence nextseg@25 vs @50 peak pipeline |
| **P4 sync** | ✅ общий sync-контракт; mode-gated только amp/BE |
| Параллель | ✅ `.11` / `.17` isolated `RUNS_ROOT`; лимиты соблюдены |

## 5. Критерии успеха

- Unit D7 зелёный; M0 rerun без BE-deadlock (Need=0 или synced=`[1,1,1,1]`).
- `br25_preinh` без refuse@3; регрессия 3× PASS.
- D3/D6: evidence или фикс.
- P4: вердикт «sync Mode=0/1 совпадает» или документированное отличие.
- Нет коллизий RUNS_ROOT/lock/work.

## 6. Ссылки на evidence

- `evidence/M1_BOUNDARY_MAP_2026-10-17.ru.md` — PASS-остров, D6, P0/D7  
- `evidence/M0C_W04_CURRENT_REPEAT_2026-10-17.ru.md` — M0 + D7 abort  
- Runs: `/home/user/TimeLearnerAudit-20261017/dualtrack/runs/`
