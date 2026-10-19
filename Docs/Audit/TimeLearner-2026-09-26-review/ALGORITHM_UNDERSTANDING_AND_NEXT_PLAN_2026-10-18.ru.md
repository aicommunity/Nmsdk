# Понимание алгоритмов обучения и план после P0

Дата: 2026-10-19 (обновление после Post-P0 GATE + план N+1).  
PulseLib: `20c3e22` (D7+D2). Console `.17` d2v4: `6f6624ab`.  
PASS regress: `tl-m1-pass-regress-d2v4-17-20261018-21-57` (3/3).  
M0 финал: `tl-m0-d7-20261018-20-27` Need=1, D7_bad=0, peak0=0.  
Актуальный план: [POST_P0_SYNTHESIS…](POST_P0_SYNTHESIS_AND_NEXT_CYCLE_2026-10-19.ru.md).

**Разделение тренеров:** §1–4 ниже — **Trainer=Branch** only. Classic — [CLASSIC_BOUNDARY_MAP…](evidence/CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md).

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

## 2. Стабильный PASS-остров Branch (C++ fires=`10000000`, Need=0)

Группировка: **Trainer=Branch · Mode=N1 · NeuronModel=baseline** (канон [RESULT_GROUPING…](evidence/RESULT_GROUPING_HIERARCHY.ru.md)).

| Span | Mod | Case | L | Срезы |
|---|---|---|---|---|
| 25 мс | nextseg | `W10_HIST_br25_nextseg` | `[7,6,4,1]` | P0 + d2v4 regress |
| 50 мс | preinh | `W10_HIST_br50_preinh` | `[15,12,6,1]` | то же |
| 100 мс | preinh | `W10_HIST_br100_preinh` | `[21,18,11,1]` | M1-ext + d2v4 regress |

На том же Trainer×Mode×NeuronModel при Mod=`gen`/`preinh` @25 Need=0, но Test silence при PostTune ON (BR-D3); PostTune OFF у gen даёт частичный detected (`10110000`).

## 3. Итог дефектов Branch (после Post-P0)

| ID | Статус | Остаток |
|---|---|---|
| BR-D2 | ✅ TipR@Rmin×SyncTol×4 | — (Need=0; Test → BR-D3) |
| BR-D7 | ✅ BE∧seg_ok | — |
| BR-D3 | open | gen+preinh@25 silence |
| BR-D6 | open | nextseg@50/100 + M0 pulse0 peak-blind |
| thrash 1↔3 | ✅ | — |

## 4. Post-P0 реализация (Branch)

| Item | Статус |
|---|---|
| **P0b / BR-D7** | ✅ unit+cold; M0 финал Need=1 peak0=0 D7_bad=0 |
| **P1 / BR-D2** | ✅ cold Need=0; PASS×3 regress |
| **P2 / BR-D3** | evidence; фикс mid — цикл N+1 A |
| **P3 / BR-D6** | evidence; цикл N+1 B/C |
| **P4 sync** | ✅ sync общий; amp/BE mode-gated (**Branch-only** формулировка seg_ok/D7) |
| Параллель N+1 | `.11`≤8 BR B/C; `.17`≤12 BR A + Classic CL |

## 5. Критерии успеха (цикл N+1)

- BR-D3: ≥1 silence→PASS или документированный предел mid.
- BR-D6: PeakSeen@50≠0 или PeakLock/inh evidence; M0 pulse0 классифицирован.
- Classic: ≥2 cold `matrix_result` в CLASSIC map (отдельный трекер).
- PASS×3 Branch зелёный на SHA любого Branch-фикса.
- Монитор `check_n1_status.sh` + чат-тики; лимиты Console.

## 6. Ссылки на evidence

- `POST_P0_SYNTHESIS_AND_NEXT_CYCLE_2026-10-19.ru.md` — сводка + N+1  
- `evidence/M1_BOUNDARY_MAP_2026-10-17.ru.md` — Branch PASS / D6  
- `evidence/M0C_W04_CURRENT_REPEAT_2026-10-17.ru.md` — BR-M0  
- `evidence/CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md` — Classic only  
- Runs: `/home/user/TimeLearnerAudit-20261017/dualtrack/runs/`
