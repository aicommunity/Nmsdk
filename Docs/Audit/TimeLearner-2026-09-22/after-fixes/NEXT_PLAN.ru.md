# План после повторной проверки исправлений и cold follow-up

Обновлено 2026-09-24 по [повторному аудиту](../../TimeLearner-2026-09-24-review/README.md). Подробные задачи, контроли и критерии приёмки: [PLAN.ru.md](../../TimeLearner-2026-09-24-review/PLAN.ru.md).

## Что изменилось в оценке

Первоначальный вариант этого плана (root 14286c9) считал A01–A16 закрытыми по probes и предлагал сразу исследовать soft_cold retrain. Повторная проверка воспроизвела GUI 13/13, CE 9/9 без A12, Branch 8/8 и verifier units 15/15, но обнаружила непокрытые пути:

| Область | Текущий вывод |
|---|---|
| Analyzer | Основные примеры A01–A04 исправлены; sample advance может обрезать окно; coincident неполный sample имеет неверный переход |
| Метрики | Foil FP и sum(ISI) исправлены; schema/NaN/N=1/полный N>5 и legacy-версионирование требуют доработки |
| PostTune | Helper finite/gap и TL reprobe исправлены; timeout/unobserved/NaN trace могут дать mid; Result не сбрасывается |
| Metric mode | Branch explicit LTZ загрязняется soma; TL Soma iteration и free-run измеряют разные величины |
| Verifier | Gate rc/SHA/snapshot улучшены; остаются старый Test mid, незавершённая Train, недоказанный Search/Keep и stale live salvage |
| Delay/Preinh/GUI/CLI | Конкретные правки обоснованы; GUI 13/13 не является проверкой CLI |
| Cold follow-up | Разработчик сообщает 2/7 PASS; свежие полные run-артефакты недоступны для независимой проверки |

[status.json](status.json) и [RECONCILE.md](RECONCILE.md) сохраняют заявленный разработчиком исторический статус. Проверенные текущие квалификации находятся в [новом status.json](../../TimeLearner-2026-09-24-review/status.json).

## Очередность

1. **P0 — надёжность измерения и запуска.** Чистые исполняемые run-каталоги; provenance Train/Test/weights; строгая приёмка завершения; visited/finite у probe-метрик; запрет mid при timeout/invalid; reset Result; явные sample/observation boundaries и CSV validity.
2. **P1 — единая метрика и минимальные контроли.** Исправить collector mode; Branch25 gold/fresh weights на одной новой калибровке; Asym50 со старым flag только в архиве и отдельный cold-run. Зафиксировать event log и преобразования Train→Test.
3. **P2 — морфогенез по результатам контролей.** Если FAIL сохраняется: soft_cold vs новая инициализация, AutoScale timing, Canon/Keep при одних L, residual sync/amp и причины best-effort остановки. Затем остальные cases.
4. **P3 — регрессии и документы.** Обновлять статусы по покрытым путям, публиковать run-bundles и отделять gold baseline от результата клона.

## Критерии и ограничения

- Branch25: свежие canon weights/mid, fires=10000000 и отсутствие скрытых foil-spikes на полном заявленном окне.
- Search: доказанный applied_best либо возврат к **собственному** snapshot; успешный fallback не доказывает улучшение Search.
- Phase6: нынешнее ожидание 10000010 — regression expectation с одним foil FP; строгая цель 10000000 имеет отдельный verdict.
- Negative global gap нельзя исправлять ослаблением LandscapeOk: сначала проверить полноту и физический смысл измерения.
- Gold Branch25 mid≈.0718 и Branch100 mid≈.00718 относятся к разным cases. Успех gold Test сам по себе не локализует cold FAIL исключительно в retrain.
- A07 — принятая same-Matrix калибровка; A12 отложен. Held-out/замена интегратора не обязательны.

[Сводка опытов](../../../../Bin/Configs/SpikeSamples/StructTrain/_repro/POSTTUNE_VERIFY_RESULT.md). Заявленные 2 PASS не объявляются ложными; текущие артефакты и harness недостаточны для независимой приёмки всего HEAD.

**Remediation (код):** см. [REMEDIATION_NOTES.ru.md](../../TimeLearner-2026-09-24-review/REMEDIATION_NOTES.ru.md) и [status.json remediation_2026_09_24](../../TimeLearner-2026-09-24-review/status.json). Контроли P1.5 / морфогенез P2: `_repro/CONTROL_RUNS_P15.md`, `_repro/MORPHOGENESIS_P2.md`.
