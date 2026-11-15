# Storage/prepared-model SDK и поиск: проверка Elder — 07.11.2026

На Elder-1 успешно собраны `Test_PulseLib_StorageComponents` и
`NeuroModelerConsole`, выполнены163 нативные проверки и19 независимых проверок
чтения результатов, без failures/errors/skips. Это адресная техническая
приёмка выбранного контура на втором сервере. Она не означает прохождения
всей матрицы, завершения плана либо получения нового результата классификации.

## Проверенный снимок и окружение

Root`ac9ccc607dece61c0ade1900133654e05f10e62a`,
PulseLib`8702d264bc7b4f4c464e200f4a1092e55c6b44ff`,
Bin`fc67a3b0958e8becdfbe1cd3f0e4e054d966d54f`,
Rdk`10e9d05aa658dd2203c89bc84ba9166595b50014`.
SDK использует Release; это не ASan. Все семь gitlinks сверены с фактическими
HEAD дочерних repositories. Конфиги/физические ресурсы read-only берутся из
Bin`99f58da9296a794374cef679bbb878cb62af979a`; различия с recorded Bin ограничены
скриптами, документацией и двумя ClDesc learner, полный список сохранён.
Скрытой подмены физических конфигов не было.

Исходный source/build cache использован после новой проверки полного закрытия
семи ранее зависевших от него групп и released leases. Source обновлён точными
Git-пакетами, прежние shallow boundaries сохранены, `update --remote` не
использовался. Build/runtime работающих экспериментов не обновлялись.

Новый runtime: `/home/user/timelearner-refactor/runtime-feedback-storage-elder-normal-a1`.
У прежнего `runtime-integrated-acceptance-normal-a1` совпали все59 файловых
bindings до/после. Лимит worker6GiB/128 tasks, один compiler job, reserved
disk2GiB; preflight требовал8GiB свободной RAM и3GiB доступного диска.
Ledger schema2, capacity и slots сохранены. Lease оставалась held до свежего
подтверждения завершения всей cgroup, затем освобождена внешним supervisor.

## Что проверено

| Набор | Область |
|---|---|
|26 новых controls|Storage feedback recipes/collisions, сохранение custom child physics, отсутствие неявной LT membrane, физический import/roundtrip, native single-pulse lifecycle/fault restoration, установка prepared model в fresh owner и отказ повторной установки|
|137 regressions|Bounded N0/N1 search, repeats/refinement/fair domains, measured length/C contexts, invalid budgets, termination, FinalVerification, native training service, learned/stopped state transport и recovery configuration|
|13 readers|Реальные single-pulse fixtures и отказы при повреждении evidence|
|2+2 readers|Inherited feedback graph и profiled graph import|
|2 readers|Fresh-owner prepared-model fixtures обоих типов при2000/20000Гц|

Native163 заняли452.137с по JUnit. Набор строго равен заранее записанному union
26+137; это не отбор прошедших функций после запуска. Все137 IDs сверены с
сохранённым прежним normal137 inventory. Некоторые controls используют
синтетические observations или специальный допуск0.2, что видно в их именах
и fixtures; они не доказывают сходимость stock-моделей при default0.02.
Single-pulse controls не заменяют штатный Train.

На M40 соответствующий native storage/prepared контур26 уже прошёл отдельно;
Console12 и четыре exact baseline waveform pairs также проверены на M40.
На Elder Console только собрана: эти12 физических Console probes здесь не
повторялись. После normal выполнен отдельный
[ASan26/readers19 на M40](FeedbackStorageASan-2026-11-07.ru.md) для SDK8702.
Это собственный адресный gate API, а не перенос прежнего ASan37 другого SDK.

## Первичные данные и независимая проверка

Evidence`2d8c76cf319e49d71fc09af69e93acd3b68fdc87`,
[compact bundle](../../../Reports/StructTrain/TimeLearner/s07-feedback-storage-elder-normal-a1/bundle.json):
1018 members,1435844 compressed bytes, SHA256
`60091ded8b3ee10c4a0859b770288acccad8f83519958e8e594932a9c5063ec8`.
Сохранены реальные native fixtures/CSV/XML/JSON, JUnit, процессные записи,
cache/flags/link commands, readers и исходник worker.

[Независимая проверка](FeedbackStorageElderVerification.json) сверила каждый
member,493 root и265 PulseLib source hashes с точными Git commits, все163
JUnit IDs/статусы и19 reader outcomes. Проверены26 фактически загруженных
file records, включая executable с тем же SHA256, его owned PID/runtime
fingerprint и корректное завершение. Loaded files находятся в отдельном
`process/loaded-files.json`; исходный runtime manifest намеренно содержит
`loaded_process_files=null` и не подменяется поздним наблюдением.

Перед публикацией дополнительно сохранены шесть фактических generated
`flags.make`/`link.txt` для PulseLib core, native test и Console; пересборка для
этого не выполнялась. Whole group closed, lease released после closure.
Локально выполнены только Git/archive/hash/JUnit metadata проверки.

Отдельно открыты проверки нового schema5 измерителя, вся physics/modes matrix, причинное
сопоставление наложившихся откликов и итоговые научные Train→Test эксперименты.
Графики и результаты отдельной диагностики наложения не переоцениваются этим
техническим PASS.
