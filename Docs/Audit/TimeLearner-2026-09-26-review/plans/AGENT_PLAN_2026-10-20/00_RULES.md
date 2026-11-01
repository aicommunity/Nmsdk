# 00. Общие правила для всех задач

Эти правила повторяют и уточняют `Docs/Audit/TimeLearner-2026-09-26-review/TIMELEARNER_EXPERIMENT_RUNBOOK.ru.md`. При противоречии действует runbook, а противоречие нужно отметить в отчёте.

## 1. Неизменные запреты

1. **Логика обучения — только в C++.** Скрипты готовят входы, запускают Console, собирают и анализируют результаты. Скрипт не может менять шаги обучения, длины, TipR, порог или решения тренера. Исключение — оверлеи очереди (`--train-param`, `--classic-gamma-mode` и т. п.). Они меняют стартовые параметры в копии Train, записываются в fingerprint и только так разрешены.
2. **Только Release.** Debug-сборки не запускать для экспериментов. Unit-тесты собирать в отдельном Release-каталоге с `BUILD_TESTING=ON`.
3. **Никогда:** `git clean`, `git reset --hard`, `git checkout -- <файл>` в рабочем checkout, `rm -rf` каталогов результатов, `git push` (пушит только человек), правка файлов в `TimeLearnerMatrix/**/inputs/` вне задачи B2.
4. **Уникальный `RUN_ID` на каждый вызов очереди.** Формат: `<task>-<host>-<UTC>-<rand>`, например `A1-17-20261021T0812Z-4821`. Повтор того же условия допускается только с новым `RUN_ID` и флагом `--allow-repeat`.
5. **Ресурсы.** Не больше 20 процессов `NeuroModelerConsole` суммарно: не больше 12 на `.17` и 8 на `.11`. Перед выдачей новой пачки запускать `tools/cpu_gate.sh N LIMIT`. При CPU > 85% новые задачи не выдавать; продолжать после двух замеров подряд ниже 70%.
6. **Долгие запуски — только в `tmux`** с именем сессии `tl-<RUN_ID>`. Потеря SSH не повод перезапускать: сначала `tmux ls`, `pgrep -af NeuroModelerConsole`, `queue_status.json`.
7. **Один wave на вызов очереди;** частичный набор случаев — только с `--no-commit`. Campaign-скрипты (`run_timelearner_matrix_campaign.*`) не использовать: они делают `git push`.
8. **Один случай — один хост.** Перед стартом впиши `RUN_ID`, хост и список случаев в `$REPORTS/ASSIGNMENTS.tsv`, проверив, что этих же случаев там нет в статусе `running`.

## 2. Переменные окружения

В A0 создаётся `$HOME/tl-agent/env.sh`. Каждая новая shell начинается с `source "$HOME/tl-agent/env.sh"`. Он задаёт следующее:

```bash
export NMSDK="$HOME/tl-agent/Nmsdk"                     # чистый checkout из A0 (не рабочая папка людей)
export PLAN="$NMSDK/Docs/Audit/TimeLearner-2026-09-26-review/plans/AGENT_PLAN_2026-10-20"
export TOOLS="$PLAN/tools"
export CABLE="$TOOLS/cable_model"
export ST="$NMSDK/Bin/Configs/SpikeSamples/StructTrain"
export DATA="/media/user/Data/TLAgent-20261020"           # диск с местом; на .11 — свой путь, см. A0
export TIMELEARNER_MATRIX_RUNS_ROOT="$DATA/runs"
export REPORTS="$DATA/agent-reports"
export HOSTTAG="17"                                       # или 11
```

Если `PLAN` ещё не закоммичен в репозиторий, распакуй пакет плана в любой каталог и задай `PLAN` на него. Остальные пути не меняются.

Шаблон уникального ID:

```bash
mkid() { echo "$1-$HOSTTAG-$(date -u +%Y%m%dT%H%MZ)-$RANDOM"; }
RUN_ID=$(mkid A1)
```

## 3. Стандартный запуск очереди

**Полосы (lanes).** Очередь держит lock `<checkout>/Bin/Configs/SpikeSamples/StructTrain/_repro/.timelearner_matrix_queue.lock` на весь прогон, и вторая очередь в том же checkout сразу падает (`another matrix launch owns …`). Поэтому одновременные запуски идут в разных клонах: `tools/make_lane.sh <имя>` делает клон с теми же коммитами, Console берётся через `NMSDK_CONSOLE`. Lock-файл **никогда не удалять**. Если он остался после упавшего процесса, это СТОП и эскалация.

**Инструменты:**

- `tools/launch_queue.sh TASK WAVE "CASES" JOBS [флаги]` — один запуск в tmux, с `cpu_gate`, записью в `ASSIGNMENTS.tsv` и проверкой lock;
- `tools/wait_run.sh RUN_ID SUBDIR` — дождаться и собрать `summary.tsv`;
- `tools/run_series.sh LANE TASK WAVE "CASES" JOBS REPEATS [флаги]` — N последовательных повторов в одной полосе.

Ниже — то же вручную (шаблон, если инструмент недоступен).

```bash
cd "$ST"
RUN_ID=$(mkid <TASK>)
SESSION="tl-$RUN_ID"
mkdir -p "$TIMELEARNER_MATRIX_RUNS_ROOT" "$REPORTS"
printf '%s\t%s\t%s\t%s\trunning\n' "$RUN_ID" "$(hostname)" "<WAVE>" "<CASES>" >> "$REPORTS/ASSIGNMENTS.tsv"
tmux new-session -d -s "$SESSION" "export TIMELEARNER_MATRIX_RUNS_ROOT='$TIMELEARNER_MATRIX_RUNS_ROOT'; cd '$ST'; \
  python3 -u scripts/run_timelearner_matrix_queue.py --run-id '$RUN_ID' --waves <WAVE> --cases <CASES> \
  --jobs <J> --no-commit --allow-repeat <EXTRA_FLAGS> > '$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.log' 2>&1; \
  echo \$? > '$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.exit'"
sleep 60; tail -5 "$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.log"; pgrep -af '[N]euroModelerConsole' | head
```

Проверка, что старт реальный: через 1–2 минуты `pgrep -af NeuroModelerConsole` показывает процессы с путями внутри `$TIMELEARNER_MATRIX_RUNS_ROOT`, а `$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID/queue_status.json` существует.

Ожидание: проверять раз в 30 минут:

```bash
cat "$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID/queue_status.json" 2>/dev/null | head -40
ls "$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.exit" 2>/dev/null && cat "$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.exit"
```

Конец: файл `.launch.exit` существует. После этого:

```bash
python3 "$TOOLS/summarize_run.py" "$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID" --json "$REPORTS/<TASK>_$RUN_ID/summary.json" \
  | tee "$REPORTS/<TASK>_$RUN_ID/summary.tsv"
```

В `ASSIGNMENTS.tsv` добавь строку с тем же `RUN_ID` и статусом `done` или `failed`. Существующие строки не правь.

## 4. Как читать результат случая

Для каждого случая в `summary.tsv` смотрим три независимых вопроса (runbook §5):

| Вопрос | Поле | Значения |
|---|---|---|
| Сходимость C++ | `training_convergence` | `converged_need0`, `converged_posttune_finalized` — сошлось; `not_converged_at_stop` — лимит; `cpp_training_refusal` — отказ C++ |
| Цель обнаружена | `detection_quality`, `fires` | `detected`; `fires` — маска из 8 символов, первый — цель. Идеал `10000000` |
| Разделение | `separation_quality`, `metrics` | `pass` / `fail` / `not_evaluated_training_incomplete` / `evaluation_error` |

Никогда не выводи качество из сходимости и наоборот. `not_evaluated` — это не ноль и не FAIL.

## 5. СТОП-условия (общие для всех карточек)

Немедленно остановить свою задачу (не трогая чужие процессы), заполнить отчёт и сообщить человеку, если:

- A0 не зелёный, или SHA коммитов/Console отличаются от записанных в A0;
- очередь завершилась с ненулевым кодом до старта Console (`launch.exit` ≠ 0 и нет `matrix_result.json`);
- `queue_status.json` или лог содержит `fingerprint`/`provenance` mismatch, `input sha mismatch`, `Traceback`;
- закончилось место (< 50 ГБ свободно на `$DATA`) или память (`free -g` → available < 4 ГБ);
- Console работает дольше 24 часов wall-clock на один случай;
- результат противоречит «Ожидаемому» в карточке более чем на указанный допуск.

Не ретраить больше одного раза. Ретрай — это новый `RUN_ID`, а причину записать в отчёт.

## 6. Отчёт

Для каждой карточки: каталог `$REPORTS/<TASK>_<RUN_ID или дата>/` с файлами:

- `REPORT.md` по `templates/REPORT_TEMPLATE.md`;
- `result.json` по `templates/result.schema.json`;
- `provenance.txt` — вывод `tools/provenance.sh "$NMSDK"`;
- все выходы, перечисленные в карточке (TSV/JSON), но **не** сырые логи Console: для них указать путь и `sha256sum`.

В git отчёты коммитит человек после ревью. Агент не коммитит в общие ветки.

## 7. Эскалация

Если шаг не описан, команда отсутствует, файл не найден или вывод не похож на ожидаемый, это СТОП. В отчёте указать: точную команду, полный вывод (до 100 строк), что ожидалось и номер шага. Не исправлять код без явной строки «исправь» в карточке.
