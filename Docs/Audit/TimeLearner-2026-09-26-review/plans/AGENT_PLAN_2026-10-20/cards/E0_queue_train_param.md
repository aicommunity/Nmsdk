# E0. Оверлей очереди `--train-param NAME=VALUE`

**Цель:** запускать диагностические варианты (D2, E2) со стартовыми параметрами тренера, которых нет в штатных флагах очереди. Значение пишется только в копию Train данной попытки, попадает в fingerprint и в `runtime_input_overrides.json`, а канонические входы не меняются.
**Уровень:** слабый. **Хост:** каждый, где будут D2/E2. **Console:** 0. **Время:** 20 мин.
**Зависит от:** A0 (можно до или после B1; патчи не конфликтуют).

Разрешённые имена (`TRAIN_PARAM_WHITELIST` в `timelearner_matrix.py`):

| Имя | Тип | Где действует | Комментарий |
|---|---|---|---|
| `EstDelayPerSeg` | d | Classic | Стартовая оценка задержки на сегмент. На W01 в Train сейчас 0.002, а физически ≈ τ = 0.01 |
| `SyncTolerance` | d | оба | Допуск синхронизации |
| `AutoEstimateAttenuationGamma` | b | оба | 0 — фиксированная γ |
| `UseSignedDelayEstimate` | b | оба | **только Console из E1** |
| `RminLengthTolFactor` | d | оба | **только Console из E1**, по умолчанию 4 |
| `FreezeSynapseResistanceBase` | b | оба | **только Console из E1** |
| `EstDelayPerSegInit` | d | Branch | **только Console из E1**; у Branch `EstDelayPerSeg` не XML-свойство |

Если параметр из E1 используется со старым Console, C++ его молча проигнорирует. Поэтому для них обязательна проверка строки аудита (см. E2).

## Шаги

```bash
source "$HOME/tl-agent/env.sh"; cd "$NMSDK/Bin"
git rev-parse --abbrev-ref HEAD            # agent/tl-audit-20261020
git apply --check "$PLAN/patches/bin_train_param_overlay.patch" && git apply "$PLAN/patches/bin_train_param_overlay.patch"
cd "$ST/scripts"
python3 -m unittest test_timelearner_matrix.RuntimeTrainParamOverlayTests -v 2>&1 | tail -5
python3 run_timelearner_matrix_queue.py --help | grep -A2 -- '--train-param'
python3 run_timelearner_matrix_queue.py --train-param Foo=1 --waves W01 2>&1 | tail -1
```

**Ожидаемо:** 2 теста `OK`; справка содержит `--train-param NAME=VALUE`; последняя команда печатает `invalid parse_train_param value: 'Foo=1'`.

Сухая проверка без Console: подложный Console, который сразу выходит. Пайплайн доходит до worker, и видно, что значение дошло до рабочей копии Train:

```bash
printf '#!/bin/sh\nexit 0\n' > "$DATA/scratch/fakeconsole"; chmod +x "$DATA/scratch/fakeconsole"
cd "$ST"; R="$DATA/scratch/E0_runs"; mkdir -p "$R"
TIMELEARNER_MATRIX_RUNS_ROOT="$R" NMSDK_CONSOLE="$DATA/scratch/fakeconsole" timeout 900 \
  python3 -u scripts/run_timelearner_matrix_queue.py --run-id E0-dry-$RANDOM --allow-repeat --waves W01 \
  --cases W01_CL50_N1_PSIoff --jobs 1 --no-commit --train-param EstDelayPerSeg=0.01 > "$R/dry.log" 2>&1; echo "rc=$?"
grep -h -o '<EstDelayPerSeg[^<]*' "$R"/*_work/Train/Parameters_00.xml
```

**Ожидаемо:** `rc` ненулевой: worker не находит результата подложного Console и пишет `PAUSED … infrastructure`, так и должно быть. Ключевое — `grep` печатает `…>0.01`. Если печатает `0.002`, это СТОП: оверлей не дошёл до рабочей копии.

Коммит (локально):

```bash
cd "$NMSDK/Bin"
git add Configs/SpikeSamples/StructTrain/scripts/run_timelearner_matrix_queue.py \
        Configs/SpikeSamples/StructTrain/scripts/timelearner_matrix.py \
        Configs/SpikeSamples/StructTrain/scripts/test_timelearner_matrix.py
git -c user.name=tl-agent -c user.email=tl-agent@localhost commit -m "feat(matrix): diagnostic --train-param Train overlay [AGENT_PLAN E0]"
```

Каталог `$DATA/scratch/E0_runs` не удалять (запрещено), просто не использовать.

## Выход

SHA коммита, вывод тестов и сухой проверки, `REPORT.md`, `result.json`.
