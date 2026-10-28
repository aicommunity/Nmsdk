# Проверяемые физические основания N1 domain decisions

Рабочий подэтап `stage07/domain-decision-evidence`, отдельно от проверяемого
controller e875ca5. Численный поиск, CapturedPerInput, допуски и lifecycle не
меняются. Старые full runs не считаются проверкой этой новой сериализации.

## Дефект доказательности

Domain schema 1 содержит готовые a/b и endpoints, но не весь физический preview.
Из такого файла нельзя независимо проверить происхождение проводимостей, C,
трёх R, частоты или shared-bank ownership. Проверка primary trial CSV подтверждает
измерение, но сама по себе не подтверждает derived domain.

## Изменение

`ResistanceDomainAssessment` сохраняет immutable semantic preview model schema 2,
его hash, source amplitude, topology, policy ratio/floor и явный ownership map
синапсов. Storage-образы и live graph не изменяются; preview не рассчитывается.
Контроллер остаётся независимым от Qt: serialized model хранится opaque string.
`EncodeResistanceDomainAssessment` выпускает отдельную domain schema 2 и
используется также внутри training summary; схема самого summary не меняется.

`Scripts/StructTrain/TimeLearner/domain_evidence.py`:

1. Проверяет preview hash, schema, per-input geometry и ownership возбуждения.
2. Читает effective typed child properties и реальные SynapticInputs bindings.
3. Заново считает secretion bound по TC/frequency, Weight, PSI и analog/pulse
   drive; затем a/R+b, averaging и условие fixed-channel strict stability.
4. Считает channel no-crossing lower bounds по фактическим C/R/Rm/Rfb/f,
   policy floor/ratio, shared-bank singleton и сравнивает endpoints и коэффициенты.
5. Отделяет `physics_verified` от обучения и scientific verdict, который всегда
   остаётся null. Roundoff allowance — относительный binary64, без абсолютного
   порога 1 для малых проводимостей и без физического percentage tolerance.

Schema 1 допускается только через явный `--allow-legacy` и возвращает
`physics_verified=false`. Неизвестная схема является ошибкой. Unavailable,
unsupported и failed records не получают физического подтверждения допустимой
области. Доказательство отсутствия области и actual live-vs-preview comparison
остаются отдельными проверками; Python не выдаёт их за выполненные.

## Проверки и ограничения

Используются настоящие Classic/Branch previews и fixed/scaled inhibition,
полученные из production storage fixtures. Corruption controls меняют child C
или связи с пересчитанным semantic hash, a/b, канал, ownership, lock, endpoint,
nonfinite и schema. Проверяются legacy adapter и отсутствие положительного
результата для unavailable. Локально тесты не выполняются; сборка и проверки
разрешены только на двух заданных workers.

Native producer отвечает за поддержку конкретных C++ equations и отсутствие
неподдерживаемых connected parameters. Auditor пересчитывает записанный preview,
но не доказывает происхождение произвольно изготовленного файла и не заменяет
проверку реального графа, build/runtime closure, observations или сертификата.
Результат не означает Exact, PhysicalInfeasible либо распознавание 8/8.

## Выполненная адресная проверка 28.10.2026

Native source: root `37c57e1a3573328a670ebf260652a5db42b0ce7c`, PulseLib
`34a00239cf9a368961daef9c0cca7106c3cb9b3c`. Последующий PulseLib `9c640961`
меняет только оформление документа; он не подставляется в tested manifest.

| Worker / attempt | Проверки | Первичные данные |
|---|---|---|
| Elder-1 normal A1 | 22 native/controller, 15 Python corruption/audit | 44 search/geometry trials, 17 independently recomputed physical records |
| M40 ASan A1, detect_leaks=0 | 22 native/controller, 15 Python corruption/audit | 44 trials, 17 independently recomputed physical records; все 44 CSV/probe JSON byte-exact к прежнему controller |
| Elder-1 aligned normal A2 | 20 native/controller, включая 2/20 кГц | 68 trials, 15 recomputed physical records; все 68 CSV/probe JSON byte-exact к прежнему controller |

Первые 22 cases включают 14 arithmetic и восемь native controls. Шесть прямых
preview/inhibition domain records входят в 17 physical records. Их отдельные
characterization CSV/JSON сохранены в пакете, но не включены в число 44
independently audited search/geometry trials; они не объявляются дополнительными
подтверждёнными training trials.
Первая normal A1 comparison использовала другой filter: двадцать Branch trials
имели иное абсолютное время и attempt IDs, а 24 предшествовавших — byte-exact.
Последующий A2 восстановил исходные filter/order и подтвердил byte-exact все 68.
Это implementation A/B, не научная проверка порядка/ITI.

Пакеты:

- [Elder-1 A1](../../../Reports/StructTrain/TimeLearner/s07-domain-physics-elder1/README.md), `2f3b774fd63932584219aa592eab6b50a5a9367c`, 152 stored / 150 raw hashes.
- [M40 A1 + A/B](../../../Reports/StructTrain/TimeLearner/s07-domain-physics-m40/README.md), `c8994c137375bf03f157d5d2c59c8de152bf1e5f`, 153 / 151.
- [Elder-1 A2](../../../Reports/StructTrain/TimeLearner/s07-domain-physics-matrix-elder1/README.md), `64281aaeba434aeb83b9455b7961f54ba478eaae`, 165 / 163.

Compressed и raw hashes всех пакетов проверены локально. Описание scope normal
пакетов исправлено отдельно: прежняя общая строка ошибочно содержала слово ASan;
поле build_kind, compiler/runtime manifest и сами данные не изменялись.

## Поддерживаемый analyze CLI

Root `268cc0b9fb9fa6b569b6fbd3f131ea29b05ffd66`: на каждом worker прошли 20
Python tests и 27 вызовов реального module CLI в свежих процессах: пять learned,
20 stopped packages, одна primary probe с CSV и один domain preview. Отдельный
Python-only worktree не меняет native runtime. Input provenance связывает SHA256
каждого исходного пакета с опубликованным Git manifest.

[Elder-1 A2](../../../Reports/StructTrain/TimeLearner/s07-domain-cli-status-elder1/README.md),
`b8832c3b6b3f5f1736cdd48dd38a44f87e996ed0`, и
[M40 A2](../../../Reports/StructTrain/TimeLearner/s07-domain-cli-status-m40/README.md),
`130387ccecf6ac1f50d2091559b27ed9f4fa631e`: по 7 stored / 5 raw hashes,
проверены локально. A1 сохранена отдельно. A2 исправляет оси статуса I/O failures:
process_error / unknown, а не completed / invalid, которое относится к ошибке
содержимого. Успешный анализ не создаёт scientific verdict.

Это только native подмножество `analyze`. Recognition scorer, runner, остальные
CLI-команды и удаление старых запускателей ещё не завершены. Full maintained runs
предыдущего root 157a5301 продолжаются отдельно. В develop этот подэтап не принят;
ни один из этапов 1–12 не объявляется полностью завершённым этими тестами.
