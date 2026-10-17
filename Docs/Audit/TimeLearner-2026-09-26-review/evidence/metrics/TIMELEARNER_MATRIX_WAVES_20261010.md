# Текущий статус матричных волн TimeLearner

Обновлено: 2026-10-11T16:24:27.058463+00:00 UTC. Это зафиксированный тогда срез: результаты базовых волн W01–W04 (32 опыта), а не актуальный итог всей матрицы.

Позже ветка `codex/timelearner-audit-followup-20261010` была доведена до W44 и содержит 312/312 результатов. Её сводный отчёт и разбор расхождений с текущими исходниками приведены в [аудите завершённой матрицы](../../TIMELEARNER_FULL_MATRIX_BRANCH_AUDIT_2026-10-13.ru.md). Здесь ниже сохранены строки исходного среза W01–W04 для исторического сравнения; прежнее утверждение «полный прогон не выполнялся» не относится к завершённой ветке.

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

