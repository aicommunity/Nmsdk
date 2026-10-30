# Post-P0: сводка и цикл N+1

Дата: 2026-10-19.  
PulseLib: `20c3e22` (D7+D2). Console `.17` d2v4: `6f6624ab`.  
GATE Post-P0: `ALL_EXPERIMENTS_DONE=1` (M0 + PASS×3 + D2 preinh).

Документ **заменяет** рабочий черновик [POST_P0_MATRIX_EXPAND…](POST_P0_MATRIX_EXPAND_AND_NEXT_PLAN_2026-10-18.ru.md) как план продолжения.

---

## 0. Маркировка (обязательно)

| Поле | Значения |
|---|---|
| **Trainer** | `Classic` (`NNeuronTimeLearner`) **или** `Branch` (`NNeuronTimeLearnerBranch`) |
| **Track** | `CL` / `BR-M1` / `BR-M0` |
| **Mode** | N0 structural / N1 parametric; у Branch ещё TipR Mode=0 vs Mode=1 |
| **Case** | полный id (`W01_…` vs `W10_HIST_br…`) |

Правила:

- `run_id`: `tl-cl-*` | `tl-m1-*` | `tl-m0-*` — не пересекать.
- `TIMELEARNER_MATRIX_RUNS_ROOT` **на кампанию/трекер** (`…/n1-branch-d3/`, `…/n1-classic-w01/`, …).
- Таблицы PASS Branch **не** смешивать с Classic без колонки Trainer.
- Дефекты `D2/D3/D6/D7` помечать `BR-…`. Classic — отдельные ярлыки (`CL-Need0-silent`, `CL-N1-stall`, …).
- Chat-тик: первая строка `Trainer=… Track=… Host=…`.

---

## 1. Линия времени

| Этап | Суть |
|---|---|
| M0-C | sync/PeakSeen контракт; thrash Active 1↔3 снят; Need=0 в бюджете нет |
| P0 | early BE; abort **BR-D7** (BE∧¬seg_ok) |
| Post-P0 | **BR-D7** BE∧seg_ok; **BR-D2** TipR@Rmin×SyncTol×4; PASS×3 regress; M0 cold финал |
| N+1 (этот цикл) | BR-D3 / BR-D6 / BR-M0 peak0 diagnostic **+** Classic мини-набор |

---

## 2. Дефекты (Branch) после Post-P0

| ID | Статус | Остаток |
|---|---|---|
| **BR-D7** | ✅ closed | cold M0 без deadlock |
| **BR-D2** | ✅ closed | `br25_preinh` Need=0 (было Incomplete) |
| **BR-D3** | open | gen+preinh@25 Need=0 + C++ silence (mid/PostTune) |
| **BR-D6** | open | nextseg@50/100 PeakSeen=0; **и** M0 pulse0 PeakSeen=0 |
| **P4** | ✅ | sync Mode0/1 общий; amp/BE mode-gated |
| thrash 1↔3 | ✅ | не вернулся |

Classic-дефекты — только в [CLASSIC_BOUNDARY_MAP…](evidence/CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md), не в этой таблице.

---

## 3. Карта успешности — группировка по иерархии

Канон: [evidence/RESULT_GROUPING_HIERARCHY.ru.md](evidence/RESULT_GROUPING_HIERARCHY.ru.md).  
Ниже те же факты N+1/A2/Post-P0, переложенные в **Trainer×Mode → Span → NeuronModel → Mod** (колонки PostTune).

### Trainer=Branch · Mode=N1 (равн. BR-M1) · NeuronModel=baseline W10

#### Span=25 мс

| Mod | PostTune OFF | PostTune ON | Regress / notes |
|---|---|---|---|
| nextseg | — | **PASS** fires=`10000000` | d2v4 PASS×3 |
| gen | Need=0 fires=`10110000` **detected** (A2.1) | Need=0 silence thr=`1` (BR-D3) | A2.3 TipR×0.75 → all-fire |
| preinh | Need=0 silence (A2.1); A2.3 тоже silence | Need=0 silence thr=`1` (BR-D3) | после D2 Train Need=0 |

#### Span=50 мс

| Mod | PostTune OFF | PostTune ON |
|---|---|---|
| preinh | — | **PASS** fires=`10000000` (PASS×3) |
| nextseg | — | Incomplete BR-D6 PeakSeen all0 |
| gen | — | HIST Need=0+silence (cold фикса — отдельно) |

#### Span=100 мс

| Mod | PostTune OFF | PostTune ON |
|---|---|---|
| preinh | — | **PASS** fires=`10000000` (PASS×3) |
| nextseg | — | Incomplete BR-D6 |
| gen | — | дыра: нет канона `br100_gen` в W10 |

```
Branch @25:  nextseg → PASS | preinh → Need0+silence | gen → Need0+silence (OFF gen detected)
Branch @50:  preinh → PASS  | nextseg → Incomplete BR-D6
Branch @100: preinh → PASS  | nextseg → Incomplete BR-D6
```

**NeuronModel=FastSpan × Branch:** конфигов нет (дыра следующего цикла).

### Trainer=Branch · Mode=N0 (равн. BR-M0) · Span≈480 · baseline W04

| Run | Итог |
|---|---|
| `tl-m0-d7-20261018-20-27` | Need=1, L=`[81,97,89,1]`, sync=`[0,1,1,1]`, peak0=0, **D7_bad=0** → класс **BR-D6 pulse0**; BR-D7 ✅ |

**Расширение:** PASS×3 удержан (качество глубины); Train Need=0 @25 +1 (`preinh`).

---

## 4. Карта — Classic (Trainer=Classic)

Отдельно: [evidence/CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md](evidence/CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md) (перегруппирована по Mode→Span).  
Исторически: W01 CL50/N0 → Need=0 + NonSeparable/silent target; CL25/N0 — stall; N1 — broken path (**не** в мини-набор N+1).

---

## 5. Параллель хостов (N+1)

| Хост | Лимит Console | Треки |
|---|---|---|
| `.11` (локальная) | **≤8** | **B** BR-D6 nextseg@50; **C** BR-M0 pulse0 diagnostic |
| `.17` | **≤12** | **A** BR-M1 D3 + PASS regress; **CL** Classic мини-набор |

Изоляция: отдельный `RUNS_ROOT` на кампанию; перед стартом и на тике — `pgrep -c NeuroModelerConsole`.

Предлагаемые корни:

| Кампания | Host | `TIMELEARNER_MATRIX_RUNS_ROOT` |
|---|---|---|
| A D3 | `.17` | `…/TimeLearnerMatrixRuns/n1-branch-d3/` |
| A regress | `.17` | `…/TimeLearnerMatrixRuns/n1-pass-regress/` |
| CL | `.17` | `…/TimeLearnerMatrixRuns/n1-classic-w01/` |
| B D6 | `.11` | `…/dualtrack/runs/n1-branch-d6/` |
| C M0diag | `.11` | `…/dualtrack/runs/n1-branch-m0diag/` |

State-файлы (после execute): `/tmp/n1_*_run_id.txt`, `/tmp/n1_*_runs_root.txt`.

---

## 6. Мониторинг и чат

Скрипт: `/home/user/TimeLearnerAudit-20261017/dualtrack/check_n1_status.sh`  
Sentinel: `AGENT_LOOP_TICK_n1` каждые **5 мин** + `notify_on_output`.  
На каждый тик — ответ в чат с `Trainer=` / Track / Host / consoles / GATE.  
`ALL_N1_DONE=1` → финальный разбор, обновление docs, **stop loop**.  
Тики без ответа в чат — неприемлемо.

---

## 7. План экспериментов N+1

### A — Trainer=Branch Track=BR-M1 Host=.17 (D3)

Цель: ≥1 из `{br25_gen, br25_preinh}` → C++ PASS.  
Рычаг: mid/PostTune / amp-bias (не L/N growth ради роста). Затем PASS×3 regress.

**Факт N+1 cold (`tl-m1-n1-d3-silence-20261019-10-04`, PL `20c3e22`):**

| Case | Train | TipR after | `train_threshold_test` | `cpp_test_threshold` |
|---|---|---|---|---|
| `br25_gen` | Need=0 L=`[7,6,4,1]` | CanonRmin `20e6` | fires=`11111111` thr≈0.102 | fires=`00000000` thr=`1` |
| `br25_preinh` | Need=0 L=`[16,13,3,1]` | CanonRmin `20e6` | fires=`00000000` thr≈0.084 | fires=`00000000` thr=`1` |

Вывод: структура ок; **калибровка/порог** (и PostTune flatten) ломает селекцию. У gen без «cpp mid» получается **all-fire**, не silence. `cpp_test` с thr=`1` / FixedLTZ≈1 — отдельный подозреваемый fallback NonSeparable.

**Ближайшие эксперименты A2 (запланировать сразу после/параллельно хвосту N+1):**

1. **PostTune off / keep TipR** (без CanonRmin flatten) на `{br25_gen, br25_preinh}` — ожидание: не обязательно PASS; сравнить fires train-mid vs cpp-mid vs silence/all-fire.
2. **Порог = train_candidate_mid** на Test (diagnostic, без смены L/N) — для gen исторически/`11111111`; зафиксировать, даёт ли хоть target_detected.
3. **Amp overshoot bias (новая гипотеза):** после Need=0 (или на последней фазе TipR/+N) добиваться пика **чуть выше** эталона/цели, а не чуть ниже (типичный undershoot → тишина при завышенном mid). Варианты по одной оси:
   - Mode=1: небольшой шаг TipR вниз (сильнее amp) или запрет последнего undershoot-шага;
   - при необходимости Mode=0/structural: +1 синапс только если amp &lt; target−ε → пока amp &gt; target+ε′.
   Метрика успеха: не обязательно 8/8; достаточно `fires≠00000000` и `≠11111111` или target_detected при FP&gt;0.
4. Разобрать, почему `cpp_test_threshold.threshold=1` при NonSeparable (баг отчёта vs реальный LTZ=1).

### B — Trainer=Branch Track=BR-M1 Host=.11 (D6 @50)

Цель: PeakSeen≠0 на soft-cold tip-1; evidence PeakLock vs NextSeg-inh.

### C — Trainer=Branch Track=BR-M0 Host=.11

Diagnostic PeakSeen[0]=0 при L0≈81 N0≈12; без полной W04×480; не гнать poll ради Need=0.

### CL — Trainer=Classic Track=CL Host=.17

1. W01 Classic **50 мс / N0** — контроль Need=0 + качество.  
2. W01 Classic **25 мс / N0** — граница.  
3. Опционально: 50 мс / N0 Step=86 МОм.  
**Не** включать Classic N1 в этот мини-набор.

### Вне скоупа

Матрица 312; полный W01 factorial; `br50_gen` до снятия BR-D3@25; Classic N1 как основная ось.

### Критерии закрытия N+1

- BR-D3: detected **или** документированный предел mid.  
- BR-D6: PeakLock/inh evidence **или** PeakSeen@50≠0.  
- Classic: ≥2 `matrix_result` в CLASSIC map.  
- PASS×3 Branch зелёный при любом Branch-фиксе.  
- Монитор остановлен.

---

## 8. Готовность (docs-цикл; cold — по отдельному execute)

| Артефакт | Статус |
|---|---|
| Этот SYNTHESIS | ✅ |
| CLASSIC_BOUNDARY_MAP скелет | ✅ |
| `check_n1_status.sh` + `n1_host_layout.env` + `arm_n1_monitor.sh` | ✅ |
| RUNS_ROOT dirs `.11` / `.17` | ✅ созданы пустые |
| Чеклист execute | [N1_EXECUTE_READY.ru.md](N1_EXECUTE_READY.ru.md) |
| Cold A/B/CL | ✅ запущены 2026-10-19 ~10:04 (см. [N1_EXECUTE_READY…](N1_EXECUTE_READY.ru.md)) |
| C M0diag | ✅ без повторного W04 — разбор `tl-m0-d7-…` |

---

## 9. Ссылки

- [STATUS.ru.md](STATUS.ru.md)  
- [ALGORITHM…](ALGORITHM_UNDERSTANDING_AND_NEXT_PLAN_2026-10-18.ru.md)  
- [M1_BOUNDARY_MAP…](evidence/M1_BOUNDARY_MAP_2026-10-17.ru.md) — Branch only  
- [M0C…](evidence/M0C_W04_CURRENT_REPEAT_2026-10-17.ru.md) — BR-M0  
- [CLASSIC_BOUNDARY_MAP…](evidence/CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md) — Classic only  
- Runs Branch dualtrack: `/home/user/TimeLearnerAudit-20261017/dualtrack/runs/`
