# Storage/prepared-model SDK: адресная ASan-проверка M40

Приняты 26 нативных тестов и 19 проверок чтения результатов без failures,
errors или skips. Проверка относится к SDK **до** нового кандидата
SingleImpulseMaximum; её нельзя переносить на новый измеритель автоматически.

## Источники и исполнение

Compiled root `b97b6cde2cea8e9299f4502fc27bd8889cebece7`, PulseLib
`8702d264bc7b4f4c464e200f4a1092e55c6b44ff`, Bin
`fc67a3b0958e8becdfbe1cd3f0e4e054d966d54f`, Rdk
`10e9d05aa658dd2203c89bc84ba9166595b50014`.
Все семь gitlinks сверены с фактическими дочерними HEAD.

Сборка RelWithDebInfo: `-O1 -g1 -fsanitize=address -fno-omit-frame-pointer`,
linker `-fsanitize=address`, один compiler job. Запрошен
`ASAN_OPTIONS=detect_leaks=0`; leak check не выполнялся. Это сохранённая
настройка производителя/production runner, не отдельное чтение окружения
тестового процесса через kernel. Реальная загрузка libasan подтверждена
сохранёнными process mappings и file hashes.

Изолированный runtime:
`/media/user/Data/TimeLearnerRefactor/runtime-feedback-storage-asan-a1`.
Неактивный source/build cache обновлён через Git после свежей проверки closure
и released leases всех четырёх прежних зависевших от него заданий. Новый runtime
не использует изменяемые symlink в source/build. Сохранены 52 прежних file
bindings четырёх runtime: все совпали до и после сборки/прогона.

Outer worker ограничен 4 GiB / 128 tasks, native gate wall limit 10800 s;
весь worker — 21600 s. M40 ledger schema1 не мигрировал; он защищает пути,
а не объявляется глобальной квотой RAM/disk. Фактические OS limits сверены
по привязанной cgroup. Lease освобождена только после закрытия всей группы.

## Что проверено

Тот же заранее объявленный набор26, который прошёл normal на M40 и входил
в Elder normal163: storage feedback recipes/collisions, custom child physics,
отсутствие неявной LT membrane, growth/Reset/XML, native single-pulse lifecycle
и восстановление после prepared/sample/final faults, профилированный graph
import/roundtrip и установка prepared model в fresh owner с отказом повтора.
Нативный набор занял 957.522 s по JUnit.

Readers:13 single-pulse,2 inherited feedback,2 profiled import,2 prepared owner.
Все19 прошли без skips. Console собрана с ASan; новых Console probes этим
worker не выполнялось. Некоторые проверки используют инженерные физические
профили и пороги: они не являются новой классификационной серией.

## Первичные данные и независимая приёмка

Evidence commit `a504189cd43a12cc9d6a8c1276f0209d840bb406`.
[Bundle](../../../Reports/StructTrain/TimeLearner/s07-feedback-storage-asan-a1/bundle.json):
222 members,639728 compressed bytes, SHA256
`045a4a04416535e1a910cda35cf0f68c605cd8c31949b9fa2842dfeed0d61c23`.
Содержит worker/spec, нативные fixtures, JUnit, runtime/process/loaded-file
records, reader outcomes, исходные flags/cache и предыдущие closures.

[Независимая проверка](FeedbackStorageASanVerification.json) сверила все members,
494 root и265 PulseLib source hashes, точный JUnit inventory26 и все19 reader
outcomes. Проверены73 фактически загруженных file records, owned process и
его runtime fingerprint. Шесть generated flags/link command files сверены
с hashes; compiler flags трёх targets и linker flags двух executable содержат
ASan. Архивирование static library само по себе не требует sanitizer linker
flag и не используется вместо проверки её compiler flags.

Новый schema5 measurement кандидат, его Console replay, полный training
assignment, C-search/physics/modes matrix и итоговые научные Train→Test
остаются отдельными gates. Этот PASS закрывает адресный memory gate API8702,
не весь этап4/5/7 либо общий план.
