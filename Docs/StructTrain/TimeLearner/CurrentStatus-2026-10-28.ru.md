# Состояние полного плана на 28.10.2026

Цель активна. Полностью завершён этап 0. Этапы 1–7, 9, 10 и 12 частичны;
этапы 8 и 11 по новой спецификации не завершены. Scoped native API и зелёные
тесты отдельных подэтапов не заменяют весь перечень требований.

## Принятая отправная точка develop

| Репозиторий | Опубликованный merge SHA |
|---|---|
| Root | `b62127538694a3442771598420fd78fa7e405c8b` |
| PulseLib | `32cb44bba481ca5ddb7d54e0288d5fa04695a9bb` |
| Rdk | `1812624ff75c60f03ad57c10b379d3e3848590bc` |
| Bin, без новых изменений | `f5e1d0200127223981daa71da22cf5ee02fdbc60` |

Предыдущий develop 2ad95250: приняты pooled direct-property / Copy lifetime
corrections, явный audit Default
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

## Новая приёмка stopped/domain/clock regression

Normal full source aeff4a9d / PulseLib 96766538 завершён на обоих workers:
4/4 maintained CTest groups, PulseLib 442 cases, 432 pass / 10 helper skips /
0 failures. Исправленный independent Python harness 75e020f6 проверил 58/58
cases без skips: 16 completed / 208 primary trials, 20 stopped / 66 trials,
8 shifted-clock probes и 81 physical-domain record. Старый Python setup error
«ровно четыре summaries» сохранён отдельно; новые cold/configured summaries
анализируются дополнительно, обязательные baseline cases проверяются явно.

Оба полных пакета опубликованы; локально проверены по 2552 stored / 2550 raw
hashes. PulseLib merge develop `32cb44bba481ca5ddb7d54e0288d5fa04695a9bb`
опубликован; его отличие от tested 96766538 — только документация. Корневой develop merge b62127538694a3442771598420fd78fa7e405c8b записывает
точный gitlink этого merge. Свежий recursive checkout на M40 подтверждает все
семь gitlinks и чистое дерево; пакет 7f4211bd, 6 stored / 4 raw hashes проверены. Это приёмка указанной
regression scope, не завершение этапов 4–8 или всего плана.
[Источники и ограничения](FullClockAcceptance.ru.md).

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
Branch geometry) прошли на обоих workers, всего по 20/20. Независимый production
аудит проверил по 68 primary trials и 15 domain assessments; запрещённых
integration edits нет. Controller-пакеты опубликованы: по 232 stored / 230 raw
hashes проверены локально. Новый ASan проход M40 завершён: 18/18 cases,
44 primary trials и 11 domain assessments, пакет 114 stored / 112 raw hashes.
Learning/export regressions на каждом worker: 22/22 native, 9/9 Python,
пять learned packages / 62 primary trials; по 508 stored / 506 raw hashes.
Все перечисленные hashes проверены локально, исходные данные доступны в Git.

Полный проход четырёх maintained groups для root 157a5301 / PulseLib e875ca5
**завершён с отказом на обоих workers**: M40 `s07-domain-full-normal-a4`,
Elder-1 `s07-domain-full-normal-a5`. Три Rdk groups pass; PulseLib parent:
430 cases, 22 failures, 10 skips. Одинаковые отказы: configured Classic N1,
six-input Branch transport и все 20 stopped-state controls. Native observations
при absolute time >128 s получают ложный sample_gap. Подэтап не принят.
Elder-1 A4 preparation failure из-за выключенного BUILD_TESTING сохранён отдельно.
Full failure / targeted clock baseline опубликованы: Elder-1 2211 stored / 2209 raw,
M40 2207 / 2205; контрольные суммы проверены локально.
[Детали](DynamicResistanceDomains.ru.md).

**Проверяемые основания N1 decisions** (`stage07/domain-decision-evidence`):
подготовлена domain schema 2 с полным immutable preview и явным ownership,
независимый Python-пересчёт физических bounds и corruption controls. Root
`37c57e1a3573328a670ebf260652a5db42b0ce7c`, PulseLib
`34a00239cf9a368961daef9c0cca7106c3cb9b3c`: на каждом worker прошли 22 native /
15 Python, по 44 primary trials и 17 independently recomputed physical records.
M40 ASan подтвердил byte-exact 44 CSV/probe JSON к предыдущему controller.
Elder-1 aligned A2 дополнительно: 20 cases при 2/20 кГц, 68 byte-exact trials
и 15 physical records. Пакеты опубликованы, hashes проверены локально.
Полные прогоны root 157a5301 не изменены и не объявляются покрытием этой
более поздней сериализации.

**Native analyze CLI**: root 268cc0b9, по 20 Python tests и 27 actual CLI calls
на каждом worker. Поддержаны domain/probe/learned-solo/stopped-solo; scientific
verdict всегда null. Code 0 не означает convergence. I/O process_error отделён
от invalid evidence. По 7 stored / 5 raw hashes проверены; native binary для
этого подэтапа не перестраивался.
[Границы подэтапа](DomainDecisionEvidence.ru.md).

**Absolute-clock sampling regression** (`stage07/absolute-clock-sampling`):
baseline f712e865 на обоих workers, M40 ASan: 9 failures из 10 cases, включая
восемь реальных probes на двух origins и частотах. Dropped-frame control проходит.
Рабочая PulseLib d4c0cf0 сохраняет масштаб absolute endpoints в sampling/coverage
comparison и отклоняет неразрешимый timestamp scale. Python auditor version 4
не переопределяет старые invalid flags. Проверка root 241db725: 52 selected cases,
явный test-only initial clock 131 s, fresh-process stopped/import controls и
независимый data audit: Elder-1 52/52 native; corrected Python source aeff4a9d —
25/25 tests, восемь clock probes, 6 learned / 84 trials и 20 stopped / 66 trials.
Все восемь clock CSV на каждом worker byte-exact к baseline. Старые четыре
Python subtest errors A2 сохранены: потребовалась также endpoint-проверка requested
duration. Elder-1 package опубликован, 1025 stored / 1023 raw hashes проверены.
M40 native seeded ASan завершён: 52/52 native и 25/25 corrected Python. Новый full normal gate aeff4a9d,
`s07-clock-full-normal-a3`, завершён на обоих workers; результаты новой
приёмки приведены выше.
[Причина, evidence и ограничения](AbsoluteClockSampling.ru.md).

**Immutable Solo→Recognition** (`stage08/recognition-conversion`): native API
сохраняет source solo, явные bounds/clipping/activation и scope сертификата.
Повторный import не масштабирует текущие Rs. Root a7a4ced6 / PulseLib 74ab08f:
на Elder-1 normal и M40 ASan A4 прошли по 11/11 native, 23/23 Python; восемь
packages, 108 source trials, 3528 полных paired frozen samples schema 1.
Опубликованы по 336 stored / 334 raw files; hashes проверены локально.
Root ca2f095b: отдельный fresh-process replay на каждом worker — 8/8 native
children, 29/29 Python, все 3528 samples byte-exact к Git-пакету Elder-1.
Тем самым M40 проверяет перенос Elder Qt5→M40 Qt6 под ASan. Трассы не содержат
spike observations и не доказывают scientific selectivity. Предыдущие A1/A2
failures инициализации свежего root сохраняются. Replay packages включены через merge; локально проверены Elder-1
1024 stored / 1022 raw и M40 694 / 692 hashes.
Develop prerequisites объединены в рабочую recognition-ветку через merge,
без изменения tested Core 74ab08f. Весь этап 8 ещё не принят: PostTune,
настоящая калибровка, independent scientific Test и полная матрица открыты.
[Контракт и ограничения](NativeRecognitionState.ru.md).

## Незакрытый объём исходных этапов

| Этап | Что ещё требуется |
|---|---|
| 1 | Полная история с августа, все audit waves и evidence levels; 211 исходных + 6 новых свойств code-reviewed, но не все runtime-validated; классификация всех старых инструментов |
| 2 | Production runtime/worker protocol, полная loaded-library provenance, isolated builds всех нужных targets, воспроизводимый run bundle |
| 3 | Сквозная schema/scorer/adapters matrix и единственный production verdict; повреждённые/неполные данные не дают PASS |
| 4 | Полный охват lifecycle/storage/growth/heterogeneous physics, все поддерживаемые конфигурации и режимы |
| 5 | Recognition/conversion/PostTune/calibration transfer, полный physical matrix; run-level diagnostics для аварийных nonfinite данных |
| 6 | Завершение общего controller/adapters, configured retarget/reconfiguration и всех совместимых режимов |
| 7 | Полная mode/physics matrix dynamic N1 domains; N0 repeatability/quantization; полный поиск/recovery, physics/inhibition/C-trim matrix и честные причины остановки |
| 8 | Полная матрица/production wiring Solo→Recognition; transactional PostTune, real-threshold calibration и независимый frozen Test |
| 9 | Помимо inventory и native подмножества analyze — остальные production CLI команды, recognition analysis и lossless config adapter; перенос активных инструментов и удаление исторических файлов из прежних деревьев с Git migration manifest |
| 10 | ConditionSpec, fingerprints, owned-process leases/queues/cancellation и fail-closed Git publisher; удаление rsync/scp pipeline |
| 11 | Исторический saved replay и cold retrain, legacy/v2 comparison, actual order/ITI controls и полная научная матрица |
| 12 | Сквозная актуализация root/PulseLib/Bin/Rdk/config/ClDesc и устранение конкурирующих актуальных спецификаций |

Серия D не возобновлялась. Августовские визуальные 4/8–6/8 сохраняются как
наблюдения исходного протокола. Научные 8/8 не являются условием завершения.
ControllerVersion=2 пока не рекомендуется для всей экспериментальной матрицы.
