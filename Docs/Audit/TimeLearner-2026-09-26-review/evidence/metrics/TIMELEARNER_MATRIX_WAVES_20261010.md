# Текущий статус матричных волн TimeLearner

Обновлено: 2026-10-10T20:19:31.501237+00:00 UTC.

Реестр подготовлен: 312 опыта, 47 волн, максимум 8 в волне. Полный прогон не выполнялся в рамках подготовки. Существуют только сохранённые результаты: 32 базовых опытов W01–W04; exact Console SHA в этих записях отсутствует.

### W01

| Случай | Сходимость C++ | Качество разделения | Детекция цели | Acc / FP | Need | Fires | Категория |
|---|---|---|---|---|---:|---|---|
| W01_CL25_N0_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W01_CL25_N0_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W01_CL25_N1_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W01_CL25_N1_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W01_CL50_N0_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W01_CL50_N0_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W01_CL50_N1_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W01_CL50_N1_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |

### W02

| Случай | Сходимость C++ | Качество разделения | Детекция цели | Acc / FP | Need | Fires | Категория |
|---|---|---|---|---|---:|---|---|
| W02_CL100_N0_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W02_CL100_N0_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W02_CL100_N1_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W02_CL100_N1_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W02_CL480_N0_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W02_CL480_N0_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W02_CL480_N1_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W02_CL480_N1_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |

### W03

| Случай | Сходимость C++ | Качество разделения | Детекция цели | Acc / FP | Need | Fires | Категория |
|---|---|---|---|---|---:|---|---|
| W03_BR25_N0_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W03_BR25_N0_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W03_BR25_N1_PSIoff | converged_need0 | legacy_gate_pass_strict_unavailable | detected | 7/8 legacy; FP=1; strict audit not saved | 0 | 10100000 | обучение сошлось; качество=legacy_gate_pass_strict_unavailable; цель=detected |
| W03_BR25_N1_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W03_BR50_N0_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W03_BR50_N0_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W03_BR50_N1_PSIoff | converged_need0 | legacy_gate_fail | target_not_detected | 7/8 legacy; FP=0; strict audit not saved | 0 | 00000000 | обучение сошлось; качество=legacy_gate_fail; цель=target_not_detected |
| W03_BR50_N1_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |

### W04

| Случай | Сходимость C++ | Качество разделения | Детекция цели | Acc / FP | Need | Fires | Категория |
|---|---|---|---|---|---:|---|---|
| W04_BR100_N0_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W04_BR100_N0_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W04_BR100_N1_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W04_BR100_N1_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W04_BR480_N0_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W04_BR480_N0_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W04_BR480_N1_PSIoff | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |
| W04_BR480_N1_PSI25 | not_converged_at_stop | not_reached_or_unknown | not_evaluated_training_incomplete | — | 1 | — | обучение не сошлось |

