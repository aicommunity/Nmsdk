# A1. Повтор положительных контролей W10 на baseline

**Цель:** убедиться, что на свежей сборке baseline воспроизводится известное текущее состояние «острова PASS» Branch. Это эталон для всех последующих A/B.
**Уровень:** слабый. **Хост:** `.17`. **Console:** 3 параллельно. **Время:** 2–8 ч.
**Зависит от:** A0.

## Случаи и ожидаемые результаты

| Case ID (wave W10) | Ожидаемо `training_convergence` | Ожидаемо `fires` | Ожидаемо `separation_quality` | Источник ожидания |
|---|---|---|---|---|
| `W10_HIST_br25_nextseg` | `converged_posttune_finalized` | `10000000` | `pass` (8/8, FP=0) | STATUS.ru.md, повторы 16–17.10 |
| `W10_HIST_br25_preinh` | `converged_posttune_finalized` | `10000000` | `pass` | STATUS.ru.md |
| `W10_HIST_br50_gen` | `converged_posttune_finalized` | не `10000000` (цель не срабатывает) | `fail`, C++ Test-mid `NonSeparable` | STATUS.ru.md: «br50_gen сошёлся, но NonSeparable, 7/8» |

## Шаги

```bash
source "$HOME/tl-agent/env.sh"
bash "$TOOLS/cpu_gate.sh" 3 12
cd "$ST"; RUN_ID=$(mkid A1); echo "$RUN_ID"; mkdir -p "$REPORTS/A1_$RUN_ID"
printf '%s\t%s\tW10\tbr25_nextseg,br25_preinh,br50_gen\trunning\n' "$RUN_ID" "$(hostname)" >> "$REPORTS/ASSIGNMENTS.tsv"
tmux new-session -d -s "tl-$RUN_ID" "export TIMELEARNER_MATRIX_RUNS_ROOT='$TIMELEARNER_MATRIX_RUNS_ROOT'; cd '$ST'; \
 python3 -u scripts/run_timelearner_matrix_queue.py --run-id '$RUN_ID' --waves W10 \
 --cases W10_HIST_br25_nextseg W10_HIST_br25_preinh W10_HIST_br50_gen --jobs 3 --no-commit --allow-repeat \
 > '$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.log' 2>&1; echo \$? > '$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.exit'"
sleep 120; tail -5 "$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.log"; pgrep -af '[N]euroModelerConsole' | wc -l
```

**Ожидаемо через 2 минуты:** `pgrep` показывает ≥ 1 Console, в логе нет `Traceback`.

`--allow-repeat` нужен всегда: в истории (`diagnostics/full_matrix_followup_audit_2026-10-14.json`) уже есть строки с теми же факторами, и без флага очередь отказывается стартовать.

Ожидание и сбор результата — по `00_RULES.md` §3. Затем:

```bash
python3 "$TOOLS/summarize_run.py" "$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID" --json "$REPORTS/A1_$RUN_ID/summary.json" | tee "$REPORTS/A1_$RUN_ID/summary.tsv"
bash "$TOOLS/provenance.sh" "$NMSDK" > "$REPORTS/A1_$RUN_ID/provenance.txt"
```

## Проверки

1. В `summary.tsv` ровно 3 строки случаев.
2. Каждая строка сравнивается с таблицей выше. Совпадение — `MATCH`, иначе `DEVIATION`.
3. Для `br25_nextseg` и `br25_preinh` дополнительно выписать `DendriteLength`, `TipSynapseResistance`, `FixedLTZThreshold`: это эталон для E2.

## Готово, когда

`REPORT.md` содержит таблицу «ожидаемо / получено / MATCH|DEVIATION» по трём случаям и provenance.

## СТОП

- Любой из `br25_nextseg` / `br25_preinh` не `pass`. Тогда baseline не воспроизводится, и задачи E2 и G1 не начинать до разбора человеком. A2, C1, C2, D1 продолжать можно.
- `br50_gen` вдруг `pass` — это не ошибка, но отметить как `DEVIATION (лучше ожидаемого)`.
