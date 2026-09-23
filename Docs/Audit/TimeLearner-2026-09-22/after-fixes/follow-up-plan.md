# Follow-up после исправлений аудита TimeLearner-2026-09-22

## Обязательно до заявлений о calibration-quality на HEAD

1. ~~Пересобрать `NeuroModelerConsole`~~ — done (`Bin/Platform/Linux/…`, SHA в after-fixes).
2. ~~Прогнать `Scripts/audit-probes`~~ — done: GUI 13, CE 9/9 без A12, Branch 8/8; A12 diagnostic FAIL.
3. ~~Прогнать `posttune_verify.py` (V1–V6)~~ — **partial**: PASS `asym50`, `br100_search`; FAIL `br25_on/off`, `asym25`, `br100_keep`, `phase6_480`.
4. ~~Обновить gitlink root~~ — после коммитов F5.

Не заявлять полный calibration-quality на весь V1–V6 до закрытия fail-list.

## Осталось (новый короткий fail-list)

- Branch soft_cold retrain: PostTune NonSeparable / fires≠10000000 при TipR canon (gold inherited-weights OK).
- `asym25`, `phase6_480` cold gate.
- soft_cold уже сбрасывает FixedLTZ→1 (stall Phase6 morph).

## Опционально (вне исходного обязательного плана)

- Held-out / robustness (новые ISI, jitter, порядок сэмплов).
- A12: интегратор / guard большого шага в `NAperiodicLink`.
- Prefix-response mode (явный параметр), если понадобится исследование.

## Не требуется повторно

Повторная реализация уже PASS в Branch (`9a6cee0`): finite silent guard, Search Train silent, best free-run reprobe, suppress второго mid.
