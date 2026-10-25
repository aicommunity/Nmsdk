# D2. Абляции на baseline: какие параметры ломают и чинят Classic N1

**Цель:** однофакторными диагностическими вариантами проверить главные гипотезы аудита о причине несходимости Classic N1 и узнать разброс повторов.
**Уровень:** слабый. **Хост:** `.17` или `.11`. **Console:** до 6. **Время:** 1–2 дня.
**Зависит от:** A0, E0. Часть D2b — ещё и от E1.

Очередь держит lock на весь прогон в своём checkout, поэтому **каждый одновременно идущий вариант — в отдельной «полосе»** (lane, отдельный клон, `tools/make_lane.sh`). Повторы одного варианта идут последовательно в его полосе через `tools/run_series.sh`, у каждого повтора новый `RUN_ID`. На `.11` перед запуском задать `export HOST_LIMIT=8`.

## Варианты D2 (Console baseline из A0)

| ID | Wave | Case | Доп. флаги очереди | Гипотеза |
|---|---|---|---|---|
| D2.0 | W01 | `W01_CL50_N1_PSIoff` | — | контроль; разброс 3 повторов |
| D2.1 | W01 | `W01_CL50_N1_PSIoff` | `--train-param EstDelayPerSeg=0.01` | в Train W01 стартовая оценка 0.002 с/сегмент — в 5 раз меньше физической (≈ τ = 0.01). Тренер «промахивается» длиной |
| D2.2 | W01 | `W01_CL50_N1_PSIoff` | `--classic-gamma-mode shared-fixed-005` | неверная оценка γ (A7) |
| D2.3 | W02 | `W02_CL480_N1_PSIoff` | — | контроль 480 мс |
| D2.4 | W02 | `W02_CL480_N1_PSIoff` | `--classic-gamma-mode shared-fixed-005` | то же для 480 |
| D2.5 | W01 | `W01_CL50_N1_PSIoff` | `--train-param EstDelayPerSeg=0.01 --classic-gamma-mode shared-fixed-005` | сочетание D2.1 и D2.2 |

```bash
source "$HOME/tl-agent/env.sh"
export NMSDK_CONSOLE="$NMSDK/Bin/Platform/Linux/NeuroModelerConsole"     # baseline из A0
drv() { tmux new-session -d -s "drv-$2" "source $HOME/tl-agent/env.sh; export NMSDK_CONSOLE='$NMSDK_CONSOLE'; export HOST_LIMIT='${HOST_LIMIT:-12}'; bash $TOOLS/run_series.sh $* > $REPORTS/drv-$2.log 2>&1"; }
drv d2-0 D2.0 W01 W01_CL50_N1_PSIoff 1 3
drv d2-1 D2.1 W01 W01_CL50_N1_PSIoff 1 3 --train-param EstDelayPerSeg=0.01
drv d2-2 D2.2 W01 W01_CL50_N1_PSIoff 1 3 --classic-gamma-mode shared-fixed-005
drv d2-3 D2.3 W02 W02_CL480_N1_PSIoff 1 3
drv d2-4 D2.4 W02 W02_CL480_N1_PSIoff 1 3 --classic-gamma-mode shared-fixed-005
drv d2-5 D2.5 W01 W01_CL50_N1_PSIoff 1 3 --train-param EstDelayPerSeg=0.01 --classic-gamma-mode shared-fixed-005
sleep 300; tmux ls | grep drv-; tail -2 "$REPORTS"/drv-D2.*.log; cat "$REPORTS/D2_runs.txt"
```

**Ожидаемо:** 6 сессий `drv-D2.*`; в `D2_runs.txt` через 5–10 минут появляются первые 6 `RUN_ID`. Конец варианта — строка `SERIES_DONE D2.x` в его логе. Сводки лежат в `$REPORTS/D2/<RUN_ID>/summary.tsv`.

Проверка, что оверлей реально применён (для каждого RUN_ID с `--train-param`):

```bash
r=<RUN_ID>; f=$(find "$TIMELEARNER_MATRIX_RUNS_ROOT/$r" -name runtime_input_overrides.json | head -1); python3 -c "import json;d=json.load(open('$f'));print(d.get('train_params'), d.get('classic_gamma_mode'))"
```

**Ожидаемо:** `{'EstDelayPerSeg': '0.01'} None` для D2.1 и т. п.

## Варианты D2b (после E1; Console из E1, `NMSDK_CONSOLE` указывает на него)

| ID | Case | `--train-param` |
|---|---|---|
| D2b.0 | `W01_CL50_N1_PSIoff` | — (контроль на Console E1, флаги по умолчанию) |
| D2b.1 | `W01_CL50_N1_PSIoff` | `RminLengthTolFactor=1` |
| D2b.2 | `W01_CL50_N1_PSIoff` | `UseSignedDelayEstimate=1` |
| D2b.3 | `W01_CL50_N1_PSIoff` | `FreezeSynapseResistanceBase=1` |
| D2b.4 | `W01_CL50_N1_PSIoff` | `EstDelayPerSeg=0.01 UseSignedDelayEstimate=1 RminLengthTolFactor=1` (несколько `--train-param`) |
| D2b.5 | `W02_CL480_N1_PSIoff` | то же, что D2b.4, без `EstDelayPerSeg` |
| D2b.6 | `W10_HIST_br25_gen` (Branch) | `EstDelayPerSegInit=0.01` |
| D2b.7 | `W10_HIST_br25_gen` | — (контроль) |

D2b запускается так же через `drv`, с полосами `d2b-0 … d2b-7` и `NMSDK_CONSOLE`, указывающим на Console из E1. Полосы для D2b создаются от checkout E1 (`NMSDK=<checkout E1>`): там PulseLib с флагами. Для D2b обязательно проверь, что C++ видит флаг. В аудит-логе тренера в рабочей копии должна быть строка параметров, например `use_signed_delay_estimate=1`:

```bash
w=$(ls -d "$TIMELEARNER_MATRIX_RUNS_ROOT"/*_work | tail -1); grep -rhoa 'use_signed_delay_estimate=[01];rmin_length_tol_factor=[0-9.]*' "$w" | sort | uniq -c | head
```

Если строки нет совсем — СТОП: Console не из E1.

## Отчёт

Таблица: ID × повтор → `training_convergence`, `DendriteLength`, `TipSynapseResistance`, `fires`, `separation_quality`. Вывод по каждой гипотезе:

- «подтверждена» — вариант даёт `converged_*` хотя бы в 2 из 3 повторов, а контроль — в 0 из 3;
- «отвергнута» — нет разницы с контролем;
- «неясно» — всё остальное.
