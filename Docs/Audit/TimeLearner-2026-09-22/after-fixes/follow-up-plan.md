# Follow-up после исправлений аудита TimeLearner-2026-09-22

## Обязательно до заявлений о calibration-quality на HEAD

1. Пересобрать `NeuroModelerConsole` (PulseLib с A01–A11/A13 + tipr_snapshot/PostTuneResult).
2. Прогнать `Scripts/audit-probes` (`audit_counterexamples`, `audit_branch_update`, GUI suite) — бывшие FAIL должны стать PASS (A12 diagnostic отдельно).
3. Прогнать `posttune_verify.py` (V1–V6) в изолированные `_repro/runs/`; классифицировать как **calibration-quality**, не held-out.
4. Обновить gitlink root на PulseLib/Bin/Rdk после успешной приёмки.

## Опционально (вне исходного обязательного плана)

- Held-out / robustness (новые ISI, jitter, порядок сэмплов).
- A12: интегратор / guard большого шага в `NAperiodicLink`.
- Prefix-response mode (явный параметр), если понадобится исследование.

## Не требуется повторно

Повторная реализация уже PASS в Branch (`9a6cee0`): finite silent guard, Search Train silent, best free-run reprobe, suppress второго mid.
