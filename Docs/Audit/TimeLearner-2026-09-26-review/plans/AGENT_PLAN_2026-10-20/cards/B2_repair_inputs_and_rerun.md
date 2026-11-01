# B2. Починка 45 повреждённых Test-входов и парный перезапуск

**Цель:** (1) получить версию матрицы с исправленной проводкой 45 Test-входов на отдельной ветке; (2) на 8 представительных случаях измерить, как исправление меняет результат, запуская парно повреждённую и починенную версии на одном и том же Console.
**Уровень:** средний. **Хост:** `.17`. **Console:** до 8. **Время:** часть 1 — 20 мин; часть 2 — 1–2 дня.
**Зависит от:** A2 (`A2_MATCH`), B1, E0. Часть 2 — ещё и от вердиктов A3.

## Часть 1. Ветка с починенными входами

```bash
source "$HOME/tl-agent/env.sh"; cd "$NMSDK/Bin"
git checkout agent/tl-audit-20261020 && git checkout -b agent/tl-a15-inputs
python3 "$TOOLS/repair_matrix_inputs.py" "$ST" "$PLAN/cards/data/A2_expected_test_failures.tsv" --dry-run | tail -3
python3 "$TOOLS/repair_matrix_inputs.py" "$ST" "$PLAN/cards/data/A2_expected_test_failures.tsv" | tee "$REPORTS/B2_repair.txt" | tail -2
python3 "$TOOLS/audit_matrix_wiring.py" "$ST" --side Test | tail -2
git status --short | grep -vc matrix_input_manifest.json
```

**Ожидаемо:** dry-run — 45 строк `WOULD_REPAIR`, `SUMMARY cases=45 failed=0 dry_run=True`; реальный прогон — `SUMMARY cases=45 failed=0 dry_run=False`; аудит — `FAIL Test 0`. В `git status` изменены 45 `Test/Model_00.xml` и 45 `matrix_input_manifest.json`; последняя команда печатает `45`.

```bash
git add -A Configs/SpikeSamples/StructTrain/TimeLearnerMatrix
git -c user.name=tl-agent -c user.email=tl-agent@localhost commit -m "fix(matrix): repair A15 wiring of 45 Test inputs (manifests updated) [AGENT_PLAN B2]"
git log -1 --format=%H
git checkout agent/tl-audit-20261020       # рабочий checkout возвращается на ветку без починки
```

## Решение о части 2 (по A3)

| A3.1 | A3.2 | Действие |
|---|---|---|
| `A15_ACTIVE_AT_RUNTIME` | `CPP_RELINKS_TO_DENDRITELENGTH` | выполнить часть 2 |
| `A15_NO_EFFECT` | любое | часть 2 не нужна; записать: «проводка входов перестраивается C++, A15 не влияет на результаты» |
| `A15_ACTIVE_AT_RUNTIME` | `CPP_KEEPS_XML_LINKS` | **СТОП, эскалация.** Gate переносит обученные длины в Test, не трогая отводы, поэтому обе версии входа меряют не те длины. Нужна правка gate или C++ (A16) — задача senior |
| `UNCLEAR` | любое | СТОП, эскалация |

## Часть 2. Парный перезапуск (A — повреждённые, B — починенные)

Для B нужен второй checkout на ветке `agent/tl-a15-inputs`. Console тот же: исходники C++ совпадают, поэтому provenance честный.

```bash
source "$HOME/tl-agent/env.sh"
cd "$HOME/tl-agent"; git clone "$NMSDK" Nmsdk-a15 && cd Nmsdk-a15
for p in $(git config --file .gitmodules --get-regexp path | awk '{print $2}'); do git config "submodule.$p.url" "$NMSDK/$p"; done
git -c protocol.file.allow=always submodule update --init
git -C Bin fetch "$NMSDK/Bin" agent/tl-a15-inputs && git -C Bin checkout --detach FETCH_HEAD
git -C Libraries/Nmsdk-PulseLib rev-parse HEAD          # должно быть d52dc1ca15…
export ST_B="$HOME/tl-agent/Nmsdk-a15/Bin/Configs/SpikeSamples/StructTrain"
export NMSDK_CONSOLE="$NMSDK/Bin/Platform/Linux/NeuroModelerConsole"
sha256sum "$NMSDK_CONSOLE"                              # = A0_CONSOLE_SHA256
```

Случаи (по одному вызову очереди на волну, A и B одновременно, `--jobs` = число случаев):

| Wave | Cases |
|---|---|
| W01 | `W01_CL25_N0_PSIoff W01_CL25_N1_PSIoff` |
| W09 | `W09_HIST_asym25` |
| W12 | `W12_HIST_fs25_gen` |
| W13 | `W13_HIST_ltz25_gen` |
| W31 | `W31_CL25_N1_MARGIN_CURRENT` |
| W46 | `W46_HIST_FAST_D002_C2_5E10` |
| W47 | `W47_HIST_FAST_D002_C1E9_TIPRMIN` |

Для каждой строки (пример W01):

```bash
bash "$TOOLS/cpu_gate.sh" 4 12
for ARM in A B; do
  if [ $ARM = A ]; then D="$ST"; else D="$ST_B"; fi
  RUN_ID=$(mkid B2$ARM); echo "$ARM $RUN_ID" | tee -a "$REPORTS/B2_runs.txt"
  tmux new-session -d -s "tl-$RUN_ID" "export TIMELEARNER_MATRIX_RUNS_ROOT='$TIMELEARNER_MATRIX_RUNS_ROOT'; export NMSDK_CONSOLE='$NMSDK_CONSOLE'; cd '$D'; \
   python3 -u scripts/run_timelearner_matrix_queue.py --run-id '$RUN_ID' --waves W01 --cases W01_CL25_N0_PSIoff W01_CL25_N1_PSIoff \
   --jobs 2 --no-commit --allow-repeat > '$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.log' 2>&1; echo \$? > '$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.exit'"
done
```

После завершения каждой пары: `summarize_run.py` для обоих `RUN_ID`, затем в отчёт — таблица:

| case | arm | training_convergence | fires | separation | DendriteLength | TipR | FixedLTZThreshold |
|---|---|---|---|---|---|---|---|

Дополнительно для каждого случая проверь, что Test-модель в рабочей копии B действительно починена:

```bash
for m in $(ls -d "$TIMELEARNER_MATRIX_RUNS_ROOT"/*_work 2>/dev/null); do echo "$m $(python3 "$TOOLS/check_model_wiring.py" "$m/Test/Model_00.xml" | head -1)"; done | tail -20
```

## Как читать

Обучение (Train) в A и B одинаковое: Train-входы не чинились, и SoftCold срезает Train-модель. Различия возможны только на этапе Test и gate. Если `training_convergence` или `DendriteLength` в A и B различаются, сначала сравни SHA Train-входов (`inputs_manifest.json` в рабочих копиях). Если SHA совпадают, это недетерминизм обучения: отметь в отчёте и сравни с разбросом повторов из A1/E2. Если SHA различаются, это СТОП.

## Выход

`B2_repair.txt`, `B2_runs.txt`, сводные таблицы, `REPORT.md`, `result.json`.
