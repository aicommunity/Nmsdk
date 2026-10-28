# Состояние полного плана на 28.10.2026

Цель активна. Полностью завершён этап 0. Этапы 1–7, 9, 10 и 12 частичны;
этапы 8 и 11 по новой спецификации не завершены. Scoped native API и зелёные
тесты отдельных подэтапов не заменяют весь перечень требований.

## Принятая отправная точка develop

| Репозиторий | Опубликованный merge SHA |
|---|---|
| Root | `2ad95250fb91c32826399702081c636852a0d56a` |
| PulseLib | `caf19a343b62e96c5076e84b6c4c2710114128bc` |
| Rdk | `1812624ff75c60f03ad57c10b379d3e3848590bc` |
| Bin, без новых изменений | `f5e1d0200127223981daa71da22cf5ee02fdbc60` |

Приняты pooled direct-property / Copy lifetime corrections, явный audit Default
и native completed solo-state transport. На обоих workers прошли четыре
maintained CTest suites: PulseLib 397 cases, 387 pass / 10 skip / 0 failures;
по 9 Python tests, 16 обученных пакетов и 208 primary JSON/CSV trials.
Полные проходы относятся к root 7fb92a4 / PulseLib 4919bac / Rdk 1223bcc;
деревья дочерних develop merges совпадают с tested. Новый source не объявляется
покрытым старым full run. [Приёмка](PooledFullAcceptance.ru.md).

Свежий recursive checkout root 2ad95250 проверен на M40, все семь сабмодулей
на записанных SHA и дерево чистое. [Git evidence](../../../Reports/StructTrain/TimeLearner/s05-accepted-closure-m40/README.md),
commit `43b16d63796cfa5ae8a886c69008af2ab333f231`; локально проверены 7 stored /
5 raw hashes. Первая ошибка отсутствующего root object устранена явным fetch
в тот же clone и сохранена как preparation error.

## Последующие проверенные и рабочие подэтапы

**Остановленный solo-state** (`stage05/stopped-training-state`, ещё не merge в
develop): 20 native / 10 Python cases на каждом worker, M40 ASan, по 66 primary
trials; по 20 fresh-process parent controls. Git replay: 16 M40→Elder-1 и
20 Elder-1→M40, model hashes и frozen CSV byte-exact. Elder-1 дополнительно:
22 service/cold/completed regressions, 9 certified-evidence tests по 62 trials.
Пакеты опубликованы, 2317 stored / 2313 raw hashes проверены локально.
Null certificate сохраняет diagnostic outcome; partial capture не становится
полной целью. [Подробности и ограничения](StoppedTrainingState.ru.md).

**Эффективные N1 области** (`stage07/native-dynamic-bounds`): baseline на обоих
workers воспроизвёл по два mesh failures, по 20 primary trials проверены.
Запрещённые Rs не применялись: preflight срабатывал, но расходовал search budget.
Read-only preview API проверен четырьмя native cases нормально и под ASan;
Elder-1 также прошёл восемь editor regressions при 2/20 кГц. Публикация содержит
132 + 48 stored / 130 + 46 raw hashes; compile failure A1 сохранён отдельно.

Native controller e875ca5 требует physical domain provider, пересчитывает mesh
после edits и сохраняет domain evidence отдельно от declared bounds. Root
c2507722 прошёл два исходных native controller cases на каждом worker;
независимый audit проверил по 24 primary trials и четыре domain assessments.
Нижняя эффективная граница реально измерена. Расширенный source 157a5301:
14 arithmetic/controller tests и шесть native cases (2/20 кГц, shared/separated
Branch geometry) проверяются на обоих workers. Подэтап ещё не принят.
[Детали](DynamicResistanceDomains.ru.md).

## Незакрытый объём исходных этапов

| Этап | Что ещё требуется |
|---|---|
| 1 | Полная история с августа, все audit waves и evidence levels; 211 исходных + 6 новых свойств code-reviewed, но не все runtime-validated; классификация всех старых инструментов |
| 2 | Production runtime/worker protocol, полная loaded-library provenance, isolated builds всех нужных targets, воспроизводимый run bundle |
| 3 | Сквозная schema/scorer/adapters matrix и единственный production verdict; повреждённые/неполные данные не дают PASS |
| 4 | Полный охват lifecycle/storage/growth/heterogeneous physics, все поддерживаемые конфигурации и режимы |
| 5 | Recognition/conversion/PostTune/calibration transfer, полный physical matrix; stopped-state merge; run-level diagnostics для аварийных nonfinite данных |
| 6 | Завершение общего controller/adapters, configured retarget/reconfiguration и всех совместимых режимов |
| 7 | Приёмка dynamic N1 domains; N0 repeatability/quantization; полный поиск/recovery, physics/inhibition/C-trim matrix и честные причины остановки |
| 8 | Immutable Solo→Recognition conversion, transactional PostTune, real-threshold calibration и независимый frozen Test |
| 9 | Все production CLI команды и lossless config adapter; перенос активных инструментов и удаление исторических файлов из прежних деревьев с Git migration manifest |
| 10 | ConditionSpec, fingerprints, owned-process leases/queues/cancellation и fail-closed Git publisher; удаление rsync/scp pipeline |
| 11 | Исторический saved replay и cold retrain, legacy/v2 comparison, actual order/ITI controls и полная научная матрица |
| 12 | Сквозная актуализация root/PulseLib/Bin/Rdk/config/ClDesc и устранение конкурирующих актуальных спецификаций |

Серия D не возобновлялась. Августовские визуальные 4/8–6/8 сохраняются как
наблюдения исходного протокола. Научные 8/8 не являются условием завершения.
ControllerVersion=2 пока не рекомендуется для всей экспериментальной матрицы.
