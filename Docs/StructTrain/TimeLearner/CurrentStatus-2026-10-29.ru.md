# Состояние полного плана на 29.10.2026

Цель активна. Полностью завершён этап 0. Этапы 1–7, 9, 10 и 12 частичны;
этапы 8 и 11 по новой спецификации не завершены. Scoped native API и зелёные
тесты отдельных подэтапов не заменяют весь перечень требований.

Последний принятый develop: root `f00989cb1fd98f126e37784ebb9b9f2d9e34b8ae`,
PulseLib `9902545414b7381d328024caf28994d53f97f090`. Объединён проверенный
frozen-owner import/hold и перенос в новый Test learner/fresh process; область
проверок не расширяется самим merge. Следующий подэтап `stage03/spike-history-reset`
исправляет фиктивные timestamps после Reset: baseline воспроизведён на обоих
workers; fixed по 12/12 native pass, M40 ASan, native statuses=0. Outer-shell
status=1 объяснён и воспроизведён отдельной диагностикой login .bash_logout.
Пакеты опубликованы; по 98 stored / 96 raw hashes проверены. Scoped fix принят;
завершение всего этапа 3/4 или полного frozen recognition runner не утверждается.
[Дефект, проверки и действия после восстановления связи](SpikeHistoryReset.ru.md).

## Предыдущая принятая отправная точка develop

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

**Остановленный solo-state** (исходная ветка `stage05/stopped-training-state`,
позднее принят в develop b6212753 вместе с full clock gate): 20 native / 10 Python cases на каждом worker, M40 ASan, по 66 primary
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

**Branch PostTune reconstruction / TL-003** (`stage08/posttune-native-rebuild`):
реальный native graph заменяется через common snapshot/import с сохранением
heterogeneous child physics и Rs/Ns, без 1 nF fallback и wake-pass Build.
На обоих workers baseline старой implementation: восемь actual failures.
Fixed e7ee0104 / PulseLib d862127: Elder normal и M40 ASan — по 10 C++ / 7 Python,
10090 waveform pairs; N0 Ns=3 на 2/20 кГц, mode preparations, rollback и listener.
Оба пакета опубликованы; по 483 stored / 481 raw hashes проверены локально.
A5 generic auditor проверил immutable данные без новой симуляции. Все ошибки
постановки A1/A2/A3 сохранены. Это не вся candidate transaction и не полный
SearchSynthetic/calibration. Подмена transient InputPattern исправлена следующим подэтапом.
Новый код пока в working branch, не в develop.
[Контракт, исходники и ограничения](PostTuneNativeRebuild.ru.md).

**PostTune transient stimulus / TL-034**: production PulseLib 0e1b01ae,
root a5ada26f: на Elder normal и M40 ASan по 4 native cases, 8 presentations /
19368 samples; Python bb4a3511 — 8 tests. Correct baseline f9a30cb7 воспроизводит
4/4 подмены цели на обоих workers; 8 общих waveform проекций byte-exact к fixed.
По 198 stored / 196 raw hashes проверены. Ошибки include / Classic phase ранних
fixtures сохранены как setup failures. Полная candidate transaction, V2 wiring,
retarget и calibration открыты. [Подробности](PostTuneTransientStimulus.ru.md).

**PostTune graph boundary — текущая работа**: root 8e7b9e88 / PulseLib
436e7020 реализует immutable capture/restore нейрона вместе с Dataset и native
портами. A1 normal: 24/24 native и 10/10 Python, 16570 exact sample pairs. A1 ASan
контролируемо прерван из-за стоимости fixture full hashing. Lifecycle baseline
дал один ожидаемый failure после owner Reset. A2 root 325052a0 / PulseLib 32dc2e0:
по 14/14 native на Elder normal и M40 ASan. После восстановления связи independent
A2 audit прошёл на обоих workers: по 2 Python tests, 16570 exact sample pairs,
20 Elder / 8 M40 CSV совпадают с полными A1. Пакеты опубликованы и получены через
Git: Elder commit 241c10f2, 426 stored / 424 raw hashes; M40 45d55b03,
241 / 239. Все hashes проверены локально.
Текущая owner-policy реализация root 912ef71b / PulseLib c7266dcb:
Elder normal завершил 23/23 native (9 новых + 14 regression), независимый
664ced234 — 4/4 Python, 42 actual training packets и 8646 waveform sample pairs.
M40 ASan также завершил 23/23 native и оба independent audits по 4/4 tests,
42 packets / 8646 sample pairs. На каждом worker 20 graph CSV совпадают с
предыдущим A2. Пакеты owner-policy опубликованы: Elder 640a39df, M40 ec944b44;
на каждом локально сверены 324 stored / 322 raw hashes. Python A2 54b3d5607
дополнительно проверяет sample-count summary против raw CSV. Новый PulseLib
8683bbff отличается от native c7266dcb только обновлением документации.
Отдельные normal full regression gates root 912ef71b завершились на обоих
workers: по 491 cases / 480 pass / 11 helper skips / 0 failures, три Rdk CTest
groups pass. Independent Python 54b3d560: по 114/114 tests без skips/failures.
Оба пакета опубликованы (bc37077f / 182191b9), на каждом локально проверены
3268 stored / 3266 raw hashes. Позднейшие owner-bindings и Rdk BOM изменения
не относятся к этому native source. Merge проверенного scope в develop
выполнен: PulseLib 4db59424, root 9e06c339. Свежий Git closure проверен
на M40, evidence 7f214425 (первоначальная ошибка регистрации сабмодулей
устранена; семь gitlinks и чистое дерево подтверждены).
[Полная регрессия](IntegratedNativeRegression-2026-10-29.ru.md).
Полная controller/threshold transaction и
production candidate-loop wiring ещё открыты.
[Контракт, проверяемые сценарии и ограничения](PostTuneBoundaryTransaction.ru.md).

**Миграция исторических запускателей — два пакета**: удалены семь одноразовых
shell-файлов из Docs/evidence/metrics и четыре InhGrid launchers/monitors.
Полные archive/last-change SHA, blob SHA-1
и content SHA-256 записаны в [реестр](ScriptMigration.ru.md); wrappers/копий нет.
Исторические результаты сохранены, ссылки исправлены на immutable Git versions.
Активные Bin/PulseLib tools, физические модели и остальная миграция не завершены.

**Августовские source anchors — уточнение этапа 1**: шесть условий и 65 файлов
проверены по Git blob/content hashes. Для Branch разделены root данных 50b0cac1
и следующий report-only root d8a1e711; исторический flat layout восстановлен.
EXP02 Test_avg1 найден в августовской истории. Это metadata review, не новый
численный replay и не проверка всех волн.
[Источники и ограничения](HistoricalEvidenceAnchors.ru.md).

**Идентичности условий/runtime — рабочий подэтап 10**: добавлен content-addressed
ConditionSpec, отдельные matrix/attempt/analysis identities и runtime manifest
schema 2 без deploy/resource/compiler path в identity flags. Сохранена полная
provenance, старые manifests не пересчитываются. На обоих workers source
670f2ff79 прошёл 18/18 Python tests и реальный перенос A2 executable/INI с
переименованием binary в `.rs2`: production snapshot сохраняет identity;
перенесённый binary запускается и перечисляет native tests. Нового численного
прогона этот контроль не выполняет. Использован свежий чистый Git closure A2
со всеми семью точными gitlinks. Пакеты c05b75ae / 976bdfcf опубликованы,
на каждом проверены 14 stored / 12 raw hashes. Runner/queue не подключены.
[Контракт и ограничения](ConditionIdentities.ru.md).

**Связанные owner-параметры — новый подэтап 4**: конфликт native construction/
import с внешними scalar/vector источниками воспроизведён. Value-aware precommit
проверка cbbf56ce допускает совпадающие read-only значения, отвергает конфликт
до замены графа и не записывает в источники. M40 ASan: 16/16 tests; независимое
чтение 16 primary JSON. Baseline A4: 8 ожидаемых failures + 8 matching passes.
Пакет 1c55f903: 467 stored / 465 raw hashes сверены. Первый неверный vector
fixture и его авария сохранены как ошибка fixture. Последующий editor fix 0ca75b3 прошёл на обоих workers 46/46 native и по
2/2 independent Python tests (12 boundary probes / 4332 samples). Fixed пакеты
073b2906 / 37e6326c: по 530 stored / 528 raw hashes проверены. Baseline
2c08b5b4 / 1e9e52f2: по 331/329 hashes. Runtime control flags остаются
открытыми. PulseLib develop merge 4e6be0cb опубликован; Core совпадает
с проверенным 0ca75b3. Rdk develop c903b9bb принимает BOM correction: M40 ASan
и Elder normal прошли четыре Rdk groups, на Elder отдельно 2 encoding tests.
Elder BOM evidence fa39375f: 10 stored / 8 raw hashes проверены. Корневой
acceptance branch записывает оба точных gitlinks; это не закрывает весь этап 4.
[Ownership и ограничения](NativeOwnerBindings.ru.md).

## Незакрытый объём исходных этапов

**Lossless config adapter**: в отдельной ветке stage09/lossless-config-adapter
добавлены адресные text edits для настоящего Rdk dialect, включая `<00>`.
По 7 Python tests на workers, 1599 tracked StructTrain Project.ini byte-exact;
M40 ASan — native readback 4 файлов / 11 values и четыре выбранные Rdk CTest
groups. Воспроизведён и исправлен общий BOM+declaration defect TL-035 в Rdk
8ebf64dd; abc21b65 отличается только документацией. Native Elder/wide проверка,
effective component preflight и production prepare/runner остаются открытыми.
[Артефакты и неудачные попытки](ConfigDocument.ru.md).

**M40 storage**: по уточнению пользователя сохраняются уникальные трассы.
10 completed runtime / 5,41 GB перенесены на Data с per-file hash checks и
сохранением старых путей. Устранены 191 byte-identical immutable Git pack copies,
освобождено 18,39 GB; HEAD objects читаются в 75 затронутых Git directories.
Maintenance journal опубликован, 30 stored / 28 raw hashes сверены. Рабочие
full gates не перемещались; low-disk событие требует независимой проверки
полноты их первичных данных. Production resource scheduler этим не реализован.
[Журнал и размещение](M40Storage-2026-10-29.ru.md).

| Этап | Что ещё требуется |
|---|---|
| 1 | Полная история с августа, все audit waves и evidence levels; 211 исходных + 6 новых свойств code-reviewed, но не все runtime-validated; классификация всех старых инструментов |
| 2 | Production runtime/worker protocol, полная loaded-library provenance, isolated builds всех нужных targets, воспроизводимый run bundle |
| 3 | Сквозная schema/scorer/adapters matrix и единственный production verdict; повреждённые/неполные данные не дают PASS |
| 4 | Полный охват lifecycle/storage/growth/heterogeneous physics, все поддерживаемые конфигурации и режимы |
| 5 | Recognition/conversion/PostTune/calibration transfer, полный physical matrix; run-level diagnostics для аварийных nonfinite данных |
| 6 | Завершение общего controller/adapters, configured retarget/reconfiguration и всех совместимых режимов |
| 7 | Полная mode/physics matrix dynamic N1 domains; N0 repeatability/quantization; полный поиск/recovery, physics/inhibition/C-trim matrix и честные причины остановки |
| 8 | Полная матрица/production wiring Solo→Recognition; полная транзакция выбора/отката PostTune candidates, real-threshold calibration и независимый frozen Test |
| 9 | Помимо inventory и native подмножества analyze — остальные production CLI команды, scientific recognition evaluation и lossless config adapter; перенос активных инструментов и удаление исторических файлов из прежних деревьев с Git migration manifest |
| 10 | ConditionSpec, fingerprints, owned-process leases/queues/cancellation и fail-closed Git publisher; удаление rsync/scp pipeline |
| 11 | Исторический saved replay и cold retrain, legacy/v2 comparison, actual order/ITI controls и полная научная матрица |
| 12 | Сквозная актуализация root/PulseLib/Bin/Rdk/config/ClDesc и устранение конкурирующих актуальных спецификаций |

Серия D не возобновлялась. Августовские визуальные 4/8–6/8 сохраняются как
наблюдения исходного протокола. Научные 8/8 не являются условием завершения.
ControllerVersion=2 пока не рекомендуется для всей экспериментальной матрицы.

## Следующий приоритет: сквозной эксперимент

[ExperimentReadiness.ru.md](ExperimentReadiness.ru.md) фиксирует четыре
обязательных блока до первой ограниченной серии: конечная recognition model,
полные frozen probes с реальными spike timestamps, threshold/control protocol
и воспроизводимый Train→export→Test→analysis job. Initial scope допускает
C-trim/PostTune Off; остальные режимы и полный исходный план сохраняются.
На момент этого checkpoint все owner/editor native и Python jobs завершены;
новых серверных заданий здесь не заявлено.

## Последующая рабочая ветка frozen recognition owner

Owner/BOM зависимости приняты: PulseLib develop 4e6be0cb, Rdk c903b9bb,
root merge d7ee23f4. Свежий checkout M40 подтверждает семь точных gitlinks
и чистое дерево, пакет 0cf41c15: 4 stored / 2 raw hashes проверены.
Штатный remote SSH/HTTPS transport использован без переписывания истории.

В новой ветке stage08/frozen-recognition-owner root6ff1d43a / PulseLib0b9d0ff
реализован явный импорт recognition state в оба learner и frozen native hooks.
Запущены восемь owner controls и четыре cold regressions на обоих workers;
новая реализация ещё не принята. Дополнительные два configured V2 controls
пока только в source. Подробности: FrozenRecognitionOwner.ru.md. Полного
spike evaluation/calibration runner этот подэтап пока не даёт.

## Frozen owner gates завершены, сквозной Test ещё открыт

Рабочий Core PulseLib0b9d0ff: A1 по 12/12 native (8 owner + 4 cold),
A2 root112acdae по 12/12 owner на Elder normal и M40 ASan, включая configured
V2 и CalculateMode=0/1. Strict A3 по 8/8 Python без skips: 164 source trials /
5052 paired samples на worker. Пакеты aa75bc2d / 8b9febb3 опубликованы;
по 912 stored / 910 raw hashes проверены локально. Первый A2 CLI-class skip
сохранён и устранён отдельным Python-only аудитом, native rerun не подменялся.

Команда analyze --format recognition-owner доступна и проверена. Recognition
certificate/scientific verdict остаются null. Текущие controls заменяют
training learner на recognition; новый Test learner/fresh-process owner,
transient foils, real spike timestamps и threshold confirmation ещё открыты.
Этот working scope не принят в develop. См. FrozenRecognitionOwner.ru.md.
Все jobs перечисленных попыток terminal; новая активная серия не заявляется.

## Новые Test learners и fresh-process owner

На обоих workers по 2/2 distinct Test learner cases и 2/2 fresh-process imports
(7de61282 / abad4a68); независимый ab4a2f7a — по 12/12 Python tests без skips.
Для пары Classic N0 / Branch N1 V2 проверены source graph immutability, factory
defaults, полное восстановление и byte-exact 762 samples. Данные: 28 source trials,
762 paired samples. Пакеты 73b1427f / f079e707: по 108 stored / 106 raw hashes
сверены локально. См. FrozenRecognitionOwner.ru.md.
Следующий блок — реальные spike timestamps и frozen transient presentations,
затем threshold/calibration. На этом checkpoint все перечисленные jobs terminal.
