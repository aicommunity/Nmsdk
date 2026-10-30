# D1. Бисекция регрессии Classic N1 по коммитам PulseLib

**Цель:** найти первый коммит PulseLib, после которого Classic в параметрическом режиме (N1) перестал сходиться. Остальное (Bin-входы, скрипты, Rdk) фиксировано.
**Уровень:** средний. **Хост:** `.11` (8 Console). **Время:** 2–3 дня машинного времени.
**Зависит от:** A0 (нужен `bin_refresh_commit` из `A0/result.json`).

## Коммиты (по порядку, индекс i)

| i | PulseLib | Дата | Суть | root, впервые закрепивший коммит | Rdk там |
|---|---|---|---|---|---|
| 0 | `780ffc7` | 11.09 | AsymRm C=1e-9 для span25 | `336f6849` | `ea97e4b87a` |
| 1 | `fd79b0f` | 22.09 | PostTune AutoScale gap | `5db69b42` | `ea97e4b87a` |
| 2 | `8d429e7` | 24.09 | PostTune/Analyzer R01–R05 | `7c0c0d8d` | `c503a04090` |
| 3 | `09d37e2` | 30.09 | walk TipR to Rmin каждый mid-band тик | `0e298cec` | `c503a04090` |
| 4 | `bb438c4` | 01.10 | Rmin: допуск LastAbsDt (kRminLengthTolFactor) | `7972184a` | `c503a04090` |
| 5 | `5308aa5` | 03.10 | AmpNorm EOL W1–W3 | `2f4abd4d` | `b3b2472dc3` |
| 6 | `3cefd64` | 07.10 | hold TipR at MaxL overshoot | `3c9f528c` | `b3b2472dc3` |
| 7 | `b5229e4` | 08.10 | reciprocal resistance bounds | `cea2ae90` | `b3b2472dc3` |
| 8 | `2bb72a3` | 09.10 | restore cold-start resistance | `4a5b36b3` | `b3b2472dc3` |
| 9 | `38fc7d4` | 14.10 | per-input resistance floors | `f3296ff9` | `b3b2472dc3` |
| 10 | `5bfffe7` | 15.10 | preflight fixed-step stability bounds | `a337785f` | `b3b2472dc3` |
| 11 | `d52dc1c` | 19.10 | baseline (HEAD) | `03c8cb91` | `b3b2472dc3` |

Случаи: `W02_CL480_N1_PSIoff` (wave W02) и `W01_CL50_N1_PSIoff` (wave W01). **«Хорошо»** — `training_convergence` начинается с `converged`. **«Плохо»** — `not_converged_at_stop` или `cpp_training_refusal`.

## Подготовка сборки для коммита i

Каждый коммит собирается в своём полном клоне, чтобы исходники, Console и fingerprint очереди совпадали.

```bash
source "$HOME/tl-agent/env.sh"
BIN_REFRESH=<bin_refresh_commit из A0>
c=780ffc7                                    # PulseLib-коммит из таблицы
B="$DATA/bisect/$c"; test -e "$B" && { echo "exists: STOP"; exit 1; }
mkdir -p "$B" && cd "$B"
git clone -q "$NMSDK" Nmsdk && cd Nmsdk
for p in $(git config --file .gitmodules --get-regexp path | awk '{print $2}'); do git config "submodule.$p.url" "$NMSDK/$p"; done
git -c protocol.file.allow=always submodule update --init
git -C Bin checkout -q --detach "$BIN_REFRESH"
git -C Libraries/Nmsdk-PulseLib checkout -q --detach "$c"
git submodule status | cut -c1-12,42-
cmake --preset linux-gcc-release-local > "$B/configure.log" 2>&1 && \
cmake --build build/linux-gcc-release-local --target NeuroModelerConsole -j"$(( $(nproc) / 2 ))" > "$B/build.log" 2>&1; echo "build rc=$?"
sha256sum Bin/Platform/Linux/NeuroModelerConsole | tee "$B/console.sha256"
```

Если `build rc≠0`: повторить один раз с Rdk из таблицы:

```bash
git -C Rdk checkout -q --detach <Rdk из таблицы>
cmake --build build/linux-gcc-release-local --target NeuroModelerConsole -j"$(( $(nproc) / 2 ))" > "$B/build2.log" 2>&1; echo "build2 rc=$?"
```

Если и это не собралось, коммит помечается `BUILD_FAIL`: в отчёт идут последние 40 строк `build2.log`. Бисекция идёт дальше без него (берётся соседний индекс).

## Запуск двух случаев на коммите i

Два случая — две одновременные очереди. Нужна вторая полоса (lane), склонированная из клона коммита; Console один и тот же.

```bash
export NMSDK_CONSOLE="$B/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole"; export HOST_LIMIT=8
tmux new-session -d -s "drv-D1-$c-W02" "source $HOME/tl-agent/env.sh; export NMSDK='$B/Nmsdk' NMSDK_CONSOLE='$NMSDK_CONSOLE' HOST_LIMIT=8; \
  bash $TOOLS/run_series.sh d1-$c-w02 D1.$c W02 W02_CL480_N1_PSIoff 1 1 > $REPORTS/drv-D1-$c-W02.log 2>&1"
tmux new-session -d -s "drv-D1-$c-W01" "source $HOME/tl-agent/env.sh; export NMSDK='$B/Nmsdk' NMSDK_CONSOLE='$NMSDK_CONSOLE' HOST_LIMIT=8; \
  bash $TOOLS/run_series.sh d1-$c-w01 D1.$c W01 W01_CL50_N1_PSIoff 1 1 > $REPORTS/drv-D1-$c-W01.log 2>&1"
sleep 300; tail -3 $REPORTS/drv-D1-$c-*.log
```

`run_series.sh` сам создаёт полосу из `$NMSDK` (то есть из клона коммита) с теми же коммитами всех подмодулей. Результаты: `$REPORTS/D1/<RUN_ID>/summary.tsv`, список `RUN_ID` — в `$REPORTS/D1_runs.txt`.

## Порядок бисекции (максимум 6 коммитов на случай)

1. Собрать и запустить i = 11 (baseline) и i = 0. Можно параллельно.
2. Если i = 0 тоже «плохо» для обоих случаев — **СТОП**: на текущих входах регрессии внутри окна нет. Записать результат; это тоже ответ («ухудшение пришло не из PulseLib или раньше 11.09»).
3. Если i = 0 «хорошо», а i = 11 «плохо»: lo = 0, hi = 11. Пока hi − lo > 1: m = (lo + hi) // 2; собрать и запустить m; если «хорошо» — lo = m, иначе hi = m.
4. Ответ: первый плохой коммит = hi. Бисекцию вести отдельно для каждого случая (W02 и W01); коммиты, уже собранные для одного, переиспользовать.
5. Для найденного hi сделать 2 повтора (новые `RUN_ID`) обоих индексов lo и hi — проверка, что переход устойчив.

## Что записать по каждому прогону

`summarize_run.py` → `training_convergence`, `DendriteLength`, `TipSynapseResistance`, `fires`. Дополнительно из `matrix_result.json` поля `training_failure_reason` и `training_failure_phase`, если есть. Таблица: i × case × повтор.

## СТОП и риски

- Старый C++ может не знать свойств, которые есть в текущих XML. Обычно это предупреждение, а не ошибка. Если очередь не может распарсить результат (`evaluation_error`, нет `matrix_result.json`) на i ≤ 4, записать `INFRA_INCOMPATIBLE` для этого i и не считать его ни «хорошим», ни «плохим».
- Не запускать больше 8 Console на `.11`.
