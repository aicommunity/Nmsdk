# Цикл N+1 — execute запущен (2026-10-19 ~10:04) · closeout ~11:20

Дата: 2026-10-19.  
Группировка итогов: [RESULT_GROUPING_HIERARCHY…](evidence/RESULT_GROUPING_HIERARCHY.ru.md) и [STATUS…](STATUS.ru.md).

Мы запускали dual-host cold с изоляцией `RUN_ID`/`RUNS_ROOT` и остановили монитор после DONE треков. Ниже сохранены инфра и RUN-реестр; итоговые метрики переложены в иерархию Trainer×Mode → Span → NeuronModel → Mod.

## Docs ✅

| Файл | Назначение |
|---|---|
| [POST_P0_SYNTHESIS…](POST_P0_SYNTHESIS_AND_NEXT_CYCLE_2026-10-19.ru.md) | сводка + план A/B/C/CL |
| [CLASSIC_BOUNDARY_MAP…](evidence/CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md) | Classic only |
| [STATUS.ru.md](STATUS.ru.md) | иерархия Branch/Classic |
| [ALGORITHM…](ALGORITHM_UNDERSTANDING_AND_NEXT_PLAN_2026-10-18.ru.md) | Branch модель + критерии N+1 |
| [RESULT_GROUPING…](evidence/RESULT_GROUPING_HIERARCHY.ru.md) | канон группировки |

## Инфра ✅

| Артефакт | Путь |
|---|---|
| Layout | `/home/user/TimeLearnerAudit-20261017/dualtrack/n1_host_layout.env` |
| Status | `…/check_n1_status.sh` (smoke: NOT_ARMED на всех треках) |
| Monitor arm | `…/arm_n1_monitor.sh` (запускать **после** старта cold + Shell `notify_on_output`) |
| RUNS_ROOT `.11` | `…/runs/n1-branch-d6`, `…/runs/n1-branch-m0diag` |
| RUNS_ROOT `.17` | `…/n1-branch-d3`, `n1-pass-regress`, `n1-classic-w01` |

Лимиты: `.11` ≤8, `.17` ≤12 Console. Перед стартом проверить `pgrep -c NeuroModelerConsole`.

## Реестр RUN (N+1 + A2) — по Trainer×Mode

### Trainer=Branch · Mode=N1

| ID | Span / Mod | Host | RUN_ID | Статус |
|---|---|---|---|---|
| A D3 ON | 25 gen+preinh | `.17` | `tl-m1-n1-d3-silence-20261019-10-04` | DONE: silence thr=`1` |
| A2.1 OFF | 25 gen+preinh | `.11` | `tl-m1-n1-a21-ptoff-20261019-10-34` | DONE: gen detected `10110000`; preinh silence |
| A2.3 | 25 TipR×0.75 | `.11` | `tl-m1-n1-a23-overshoot-20261019-10-52` | DONE: gen all-fire; preinh silence |
| B D6 | 50 nextseg | `.11` | `tl-m1-n1-d6-br50ns-20261019-10-04` | DONE Need=1 peak-blind |
| PASS×3 | 25 ns / 50+100 preinh | `.17` | d2v4 regress (ранее) | зелёный на d2v4; N+1 **не** arm |

### Trainer=Branch · Mode=N0

| ID | Span / Mod | Host | RUN_ID | Статус |
|---|---|---|---|---|
| C | ~480 W04 | `.11` | `tl-m0-d7-20261018-20-27` | DONE peak0=0 D7_bad=0 |

### Trainer=Classic · Mode=N0

| ID | Span / Mod | Host | RUN_ID | Статус |
|---|---|---|---|---|
| CL | 25+50 PSIoff | `.17` | `tl-cl-n1-w01-20261019-10-04` | DONE: CL25 Need=1; CL50 Need=0 silent |

PulseLib `.11`/`.17`: `20c3e22`.

## Cold closeout (2026-10-19 ~11:20)

Монитор `AGENT_LOOP_TICK_n1` **остановлен** (cold-треки DONE; PASS×3 намеренно NOT_ARMED до Branch-фикса).

Цикл N+1 закрыл критерии документации mid/D6/Classic≥2, но не закрыл BR-D3 как PASS: PostTune ON оставляет silence и thr=`1`, а OFF у gen даёт частичный detected. Дальнейшая работа — трёхуровневый PostTune-фикс и явный arm PASS×3 на SHA фикса.

| Критерий N+1 | Итог |
|---|---|
| BR-D3 mid | gen: PostTune OFF → detected `10110000`; preinh: silence (A2.3 TipR×0.75 не помог) |
| BR-D6 @50 | Need=1 L=`[1,1,1,1]` peak-blind |
| Classic ≥2 results | CL25 incomplete; CL50 Need=0 silent/`cpp_nonseparable` |
| PASS×3 | **не запускался** — ждать фикс / явный arm |
| A2 | A2.1 DONE; A2.3 DONE (не лечит preinh); A2.4 thr=1 — следующий разбор |

## A2 — статус

| # | Гипотеза | Статус |
|---|---|---|
| A2.1 | PostTune off / keep TipR | **DONE** `tl-m1-n1-a21-ptoff-20261019-10-34`: **gen** Need=0 fires=`10110000` **detected** (не silence/all-fire); TipR midband. **preinh** Need=0 fires=`00000000` silence, TipR midband. matrix.json restored. |
| A2.2 | Test на train_mid | evidence (gen с PostTune on → `11111111`) |
| A2.3 | Amp overshoot | **DONE** `tl-m1-n1-a23-overshoot-20261019-10-52` TipR×0.75: **gen** `11111111` fire_all (A2.1 был `10110000`); **preinh** всё ещё `00000000` silence thr≈0.19 |
| A2.4 | cpp thr=`1` | при PostTune on; A2.1 gen обошёл silence без thr=1 path |
