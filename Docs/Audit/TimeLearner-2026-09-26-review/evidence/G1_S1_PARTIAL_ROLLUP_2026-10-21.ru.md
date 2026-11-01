# G1 S1 — частичный rollup исполнения (PARTIAL, 2026-10-21)

**Статус документа:** PARTIAL — **drv 12/12** `SERIES_DONE` + `EXIT=0` (tick 123); **matrix exit audit rep3: 3/12** с `launch.exit=0` (W01, W13, W33 на `.11`) — см. [`G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md`](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md). W08 rep3: `launch.exit=1`, queue `paused_after_training_or_evaluation_issue` — **ложный «зелёный» drv подтверждён**.

**Момент среза (UTC):** 2026-10-21T16:36Z (tick 124 exit-audit + metrics outline). Источники read-only: `drv-G1.S1.W*.log` на Elder-1 (`.11`) и M40 `.17` (`/media/user/Data/TLAgent-20261020/agent-reports/`), [`G1_LAUNCH_S1_2026-10-21.ru.md`](G1_LAUNCH_S1_2026-10-21.ru.md), [`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv), `$REPORTS/ASSIGNMENTS.tsv`, failure-analysis `$REPORTS/G1/G1_FAILURE_ANALYSIS_2026-10-21.ru.md` (копия кампании: `/home/user/TLAgent-20261020/agent-reports/G1/G1_FAILURE_ANALYSIS_2026-10-21.ru.md`). Запущенный **W08 rep3** на `.17` не останавливался.

## 1. Область (scope)

Плечо **G1 S1** стартовало после E2 R8 (`S0↔S1↔S2 EQUIVALENT`) и явного решения человека запускать baseline arm. В отбор вошли **32 случая** PSI-off с `excluded_A15=False` ([`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv)): ячейки trainer×norm×span, исторические шаблоны и оси AsymRm / FastSpan (W48). Runtime зафиксирован в плане запуска: Console sha256 `745d6061a50d0e5c3d8ec38ad4fabcc73de9d1db2362ed0c78cc408f1bf2dc57`, PulseLib `6d746ac`, **3 повтора** на волну через `run_series.sh`, очередь по волнам без пересечения хостов.

Распределение волн по хостам совпадает с [`G1_LAUNCH_S1_2026-10-21.ru.md`](G1_LAUNCH_S1_2026-10-21.ru.md) и строками `G1_S1 .host11` / `.host17` в `$REPORTS/ASSIGNMENTS.tsv`. На **Elder-1 (`.11`)** крутятся шесть волн (**12 случаев**): W01, W02, W13, W31, W33, W37 при `HOST_LIMIT=8`. На **M40 `10.245.1.17` (`.17`)** — семь волн (**20 случаев**): W04, W08, W09, W10, W11, W12, W48 при `HOST_LIMIT=12`. Лаунчеры: tmux `drv-G1.S1.launcher{11,17}`, логи `$REPORTS/G1/launch_{11,17}.log`.

## 2. Таблица статуса волн (исполнение серий)

Критерий строки ниже — **drv-лог волны**: наличие `SERIES_DONE` и финальной строки `EXIT=` после цикла rep (или явное «в процессе»). Это **не** заменяет извлечение training/Test метрик и **не** отменяет риск раннего `SERIES_DONE` при плохом `launch.exit` (см. §3).

| Host | Wave | Cases (G1 S1) | Серия drv | Примечание |
|------|------|---------------|-----------|------------|
| `.11` | W01 | W01_CL50_N0_PSIoff | **SERIES_DONE**, **EXIT=0** | rep3 `G1.S1.W01-11-20261021T113257Z-15892` |
| `.11` | W02 | W02_CL100_N0_PSIoff, W02_CL480_N0_PSIoff | **SERIES_DONE**, **EXIT=0** | rep3 `…124609Z-28711`; см. §3 про `queue_exit` |
| `.11` | W13 | W13_HIST_ltz50_gen | **SERIES_DONE**, **EXIT=0** | |
| `.11` | W31 | W31_CL480_N0_MARGIN_CURRENT | **SERIES_DONE**, **EXIT=0** | длительный rep3 до SD |
| `.11` | W33 | W33_CL50_N0_PSIoff_POST | **SERIES_DONE**, **EXIT=0** | |
| `.11` | W37 | 6× packB/packC classic | **SERIES_DONE**, **EXIT=0** | после `W37_JOBS3` / refresh |
| `.17` | W04 | W04_BR480_N0_PSIoff | **SERIES_DONE**, **EXIT=0** | rerun после libglog; §3 |
| `.17` | W08 | W08_BR480_N0_PSIoff_NEXT | **SERIES_DONE**, **EXIT=0** | rep3 `G1.S1.W08-17-20261021T132542Z-11858`; lane offloaded Data |
| `.17` | W09 | 5× HIST | **SERIES_DONE**, **EXIT=0** | |
| `.17` | W10 | 3× HIST branch | **SERIES_DONE**, **EXIT=0** | |
| `.17` | W11 | 3× HIST | **SERIES_DONE**, **EXIT=0** | |
| `.17` | W12 | W12_HIST_phase6_ltzcal_twin | **SERIES_DONE**, **EXIT=0** | |
| `.17` | W48 | 6× FS gen/nextseg | **SERIES_DONE**, **EXIT=0** | после `W48_JOBS3` |

**Итого на срезе:** **12 из 12** волн закрыты drv как `SERIES_DONE` + `EXIT=0`. **Exit-audit rep3:** только **3/12** `launch.exit=0`; кампания **не** matrix-complete для G1 vs C2 без rerun или partial extract ([`G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md`](G1_S1_METRICS_EXTRACT_OUTLINE_2026-10-21.ru.md)).

## 3. Риск ложного SERIES_DONE (libglog и rerun)

На `.17` первая волна инфраструктурных прогонов дала **`SERIES_DONE` при `launch.exit` ∈ {1,2,4}** из‑за отсутствия `libglog.so.0`, `SIGABRT` и `LANE_BUSY` на W04; механизм задокументирован в [`G1_FAILURE_ANALYSIS_2026-10-21.ru.md`](/home/user/TLAgent-20261020/agent-reports/G1/G1_FAILURE_ANALYSIS_2026-10-21.ru.md) (`$REPORTS/G1/G1_FAILURE_ANALYSIS_2026-10-21.ru.md`). Скрипт `run_series.sh` печатает `SERIES_DONE`, когда дождался файла `launch.exit`, **не проверяя его значение**, поэтому для rollup и сравнения с C2 нужно опираться на **последнюю rerun-серию** после `G1_S1_RERUN` (`reason=libglog_fixed+disk_ok`) и на **`launch.exit=0`** последнего `run_id` в `$TIMELEARNER_MATRIX_RUNS_ROOT`, а не на первые «зелёные» drv до rerun.

Для **W04** rep3 rerun `…130651Z-903`: drv `SERIES_DONE`, но **`launch.exit=1`**. **W08** rep3 `…132542Z-11858`: drv `SERIES_DONE`, **`launch.exit=1`**, training stop на case W08_BR480_N0_PSIoff_NEXT; две ранние SD не использовать. На `.11` часть промежуточных launch имела `queue_exit=1` (W37, W31, W02 rep3), при этом drv завершился `EXIT=0`; для метрик rollup предпочтителен **последний rep** и его `runs/…launch.exit`, как в §4 чеклиста failure-analysis.

## 4. Ссылки Train / Test (matrix inputs)

Корень StructTrain для G1 задаётся **per-wave lane** в `$REPORTS/ASSIGNMENTS.tsv` (поле `st=`). Шаблон Train/Test для каждого `case_id`:

`{st}/TimeLearnerMatrix/{WAVE}/inputs/{CASE}/Train/` и `…/Test/`  
(типовые файлы: `Project.ini`, `Parameters_00.xml`, `Model_00.xml`).

| Wave | Lane `st=` (StructTrain) | Cases |
|------|--------------------------|-------|
| W01 | `/home/user/tl-agent/lanes/g1-s1-w01/Nmsdk/Bin/Configs/SpikeSamples/StructTrain` | W01_CL50_N0_PSIoff |
| W02 | `…/g1-s1-w02/…/StructTrain` | W02_CL100_N0_PSIoff, W02_CL480_N0_PSIoff |
| W13 | `…/g1-s1-w13/…/StructTrain` | W13_HIST_ltz50_gen |
| W31 | `…/g1-s1-w31/…/StructTrain` | W31_CL480_N0_MARGIN_CURRENT |
| W33 | `…/g1-s1-w33/…/StructTrain` | W33_CL50_N0_PSIoff_POST |
| W37 | `…/g1-s1-w37/…/StructTrain` | W37_CL100_PACKB_N0 … W37_CL25_PACKC_N1 (6) |
| W04 | `/home/user/tl-agent/lanes/g1-s1-w04/…/StructTrain` (`.17`) | W04_BR480_N0_PSIoff |
| W08 | `…/g1-s1-w08/…/StructTrain` (`.17`) | W08_BR480_N0_PSIoff_NEXT |
| W09 | `…/g1-s1-w09/…/StructTrain` | W09_HIST_* (5) |
| W10 | `…/g1-s1-w10/…/StructTrain` | W10_HIST_* (3) |
| W11 | `…/g1-s1-w11/…/StructTrain` | W11_HIST_* (3) |
| W12 | `…/g1-s1-w12/…/StructTrain` | W12_HIST_phase6_ltzcal_twin |
| W48 | `…/g1-s1-w48/…/StructTrain` | W48_BR_FS* (6) |

Console для всех launch (из ASSIGNMENTS): `/home/user/tl-agent/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole`. Runs: `.11` → `$HOME/TLAgent-20261020/runs`, `.17` → `/media/user/Data/TLAgent-20261020/runs`. Предсказания C2 до запуска: [`G1_predictions_2026-10-21.tsv`](G1_predictions_2026-10-21.tsv) (32/32 `match_D=5.0` на срезе отбора).

## 5. Ограничения PARTIAL и следующий шаг

Этот rollup **не** является финальным вердиктом G1 против **C2**: нет полной матрицы case×rep с `training_convergence`, separation/detection и сопоставлением `m_oracle`/`feasible` по всем 32 строкам. Следующий шаг — batch extract summary (как E2 [`E2_matrix_2026-10-21.tsv`](E2_matrix_2026-10-21.tsv)), проверка `launch.exit` rep3 по всем волнам, группировка **Trainer×Mode → Span → NeuronModel → Mod** (PostTune ON/OFF).

Не использовать первые libglog-серии `.17` в таблицах PASS; при готовности метрик — заменить полным `G1_S1_ROLLUP_*`.

---
Собрано read-only с Elder-1; срез `.17` через SSH к `10.245.1.17`. Зеркало отчёта кампании: `/home/user/TLAgent-20261020/agent-reports/G1/G1_S1_PARTIAL_ROLLUP_2026-10-21.ru.md`.
