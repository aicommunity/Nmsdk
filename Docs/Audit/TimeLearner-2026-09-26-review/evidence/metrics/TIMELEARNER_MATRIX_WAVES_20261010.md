# Текущий статус матричных волн TimeLearner

Обновлено: 2026-10-11T16:24:27.058463+00:00 UTC.

Реестр подготовлен: 312 опытов, 47 волн, максимум 8 в волне. Полный прогон не выполнялся в рамках подготовки. В репозитории сохранены результаты всех 32 базовых опытов W01–W04. По каждой строке `results.json` содержит SHA бинарника Console и исходников запуска; сырых пошаговых runtime-логов волн в Git нет. Текущая классификация: 4 `Need=0`, 28 `Need=1`, 0 строгих PASS. Подробности и ограничения причинной интерпретации: [расследование сходимости](../../../HISTORICAL_CONVERGENCE_INVESTIGATION_2026-10-11.ru.md).

### W01

| Случай | Сходимость C++ | Качество разделения | Детекция цели | Acc / FP | Need | Fires | Категория | Provenance (SHA, начало) |
|---|---|---|---|---|---:|---|---|---|
| W01_CL25_N0_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=75b4988095ef; Bin=2f19736dd852; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W01_CL25_N0_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=75b4988095ef; Bin=2f19736dd852; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W01_CL25_N1_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=75b4988095ef; Bin=2f19736dd852; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W01_CL25_N1_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=75b4988095ef; Bin=2f19736dd852; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W01_CL50_N0_PSIoff | converged_need0 | evaluation_error | evaluation_error | — | 0 | — | обучение сошлось; качество=evaluation_error; цель=evaluation_error | root=75b4988095ef; Bin=2f19736dd852; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W01_CL50_N0_PSI25 | converged_need0 | evaluation_error | evaluation_error | — | 0 | — | обучение сошлось; качество=evaluation_error; цель=evaluation_error | root=75b4988095ef; Bin=2f19736dd852; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W01_CL50_N1_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=75b4988095ef; Bin=2f19736dd852; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W01_CL50_N1_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=75b4988095ef; Bin=2f19736dd852; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |

### W02

| Случай | Сходимость C++ | Качество разделения | Детекция цели | Acc / FP | Need | Fires | Категория | Provenance (SHA, начало) |
|---|---|---|---|---|---:|---|---|---|
| W02_CL100_N0_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=aef5b5875b8b; Bin=28eec7138f63; PulseLib=2bb72a3b6b28; Console=e4df62fb9163 |
| W02_CL100_N0_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=aef5b5875b8b; Bin=28eec7138f63; PulseLib=2bb72a3b6b28; Console=e4df62fb9163 |
| W02_CL100_N1_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=aef5b5875b8b; Bin=28eec7138f63; PulseLib=2bb72a3b6b28; Console=e4df62fb9163 |
| W02_CL100_N1_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=aef5b5875b8b; Bin=28eec7138f63; PulseLib=2bb72a3b6b28; Console=e4df62fb9163 |
| W02_CL480_N0_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=e4df62fb9163 |
| W02_CL480_N0_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=aef5b5875b8b; Bin=28eec7138f63; PulseLib=2bb72a3b6b28; Console=e4df62fb9163 |
| W02_CL480_N1_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=e4df62fb9163 |
| W02_CL480_N1_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=e4df62fb9163 |

### W04

| Случай | Сходимость C++ | Качество разделения | Детекция цели | Acc / FP | Need | Fires | Категория | Provenance (SHA, начало) |
|---|---|---|---|---|---:|---|---|---|
| W04_BR100_N0_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W04_BR100_N0_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W04_BR100_N1_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W04_BR100_N1_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W04_BR480_N0_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W04_BR480_N0_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W04_BR480_N1_PSIoff | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |
| W04_BR480_N1_PSI25 | not_converged_at_stop | not_evaluated_training_incomplete | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось | root=d80dfb6d6036; Bin=1dc2e3f41d69; PulseLib=2bb72a3b6b28; Console=51da1f19a441 |

