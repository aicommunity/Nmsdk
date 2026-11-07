# Дубли статических link caches на Elder — 07.11.2026

Для подготовки повторной серверной проверки освобождено около 2.59 GiB на
Elder-1. Удалены только 275 SHA256-подтверждённых дублирующих `.a` в
`/home/user/timelearner-refactor/runtime-*/Lib.CMake`. Для каждого удалённого
файла сохранена независимая проверенная копия с теми же байтами. Каталоги
runtime не удалялись. Уникальные библиотеки сохранены.

Проверены 1000 статических архивов; кандидаты ограничены сохранённым явным
списком 74 runtime старых gates s01/s03/s04/s06. Имена использовались для
выбора устаревших link caches, не для удаления всего содержимого каталогов.
Current integrated runtime, historical August runtime и runtime s07 в список
удаления не входили. Исполняемые файлы, shared libraries, source/build trees,
модели и экспериментальные primary data не являлись целями.

Для 462 остальных файлов/ссылок внутри выбранных runtime совпали readbacks до
и после. Для каждой сохранённой копии повторно проверен SHA256 после удаления.
Удаление static cache меняет старый runtime file inventory: прежние receipts
описывают его состояние во время своего эксперимента. Старый executable
продолжает существовать; для повторного линкования может понадобиться вернуть
указанный `.a` из keeper либо заново собрать cache. Не следует объявлять весь
старый каталог побитово неизменным после этой операции.

## Исполнение и доказательства

Использован production-модуль
`Scripts/StructTrain/TimeLearner/static_archive_cleanup.py`, source root
`9e3f18ba23f21ca9da34b803b1f93fafde3c60ac`. Он требует owned write lease всего
заданного root, проверяет canonical paths, обычный AR header, regular file и
единственную hardlink, inode/размер/timestamps/SHA256. Keeper не может входить
в список удаления. Все preimages проверяются до первого удаления, затем перед
каждым unlink повторно проверяются target и keeper. План и каждый intent/result
записываются с fsync. При частичном отказе нет неявного продолжения: нужны
проверка журнала и новый план. Наличие AR header не является полной проверкой
содержимого object archive; для этой операции существенны тип cache и точное
равенство удаляемой/сохраняемой копий.

На Elder прошли шесть filesystem/reservation tests без skips: duplicate-only
удаление и сохранение executable/primary; изменение target/keeper до операции;
отсутствующая/недостаточная lease; symlink/hardlink/thin format; выход за scope
или удаление keeper; сохранение одной копии при retirement всех дубликатов.
Те же шесть tests повторены внутри maintenance worker перед основной операцией.
Нативные расчёты и сборки не запускались.

Операция выполнена в отдельной ограниченной systemd user group. Перед ней
не было held production leases/других running TimeLearner units, проверено
отсутствие native/build процессов пользователя. Схема 2 ledger, capacity и slots
не изменились. Этот протокол защищает от совместных зарегистрированных writers;
он не заявляет защиту от произвольного внешнего процесса, нарушающего leases.
Финальная свежая проверка подтвердила закрытие всей группы и released lease.

Свободное место в интервале самой операции:
`1 633 234 944 → 4 416 393 216` bytes, прирост `2 783 158 272` bytes.
Сумма логических размеров удалённых `.a`: `2 783 246 386` bytes; это отдельная
величина, не подмена readback свободного места. Последующие задания могут
использовать освобождённое пространство.

Evidence commit `f7edf7cdb94c7b1c83d6e3797367dd4db0b3c4b8`,
[compact bundle](../../../Reports/StructTrain/TimeLearner/s02-static-archive-cleanup-elder-a1/bundle.json):
18 members, 53 372 compressed bytes, SHA256
`6d6b1f8b755c5145f64c5ed6d77a4cead5ea3b357fc114b77bc9476d98c7ad48`.
Git содержит полный план target→keeper, preimages, durable journal, before/after
file bindings, tests, исходник worker и closure. Никакие удалённые `.a` в Git
не копировались. [Независимая проверка](StaticArchiveCleanupVerification.json)
сверила все 18 members и 288 tool source hashes с указанным commit. Локально
выполнены только Git/archive/hash/metadata проверки.

Это принятый maintenance-подэтап подготовки Elder, не выполнение всей стадии 2
и не научный результат обучения. Повторные SDK gates и полный план остаются
открытыми; необходимость дополнительного дискового резерва оценивается перед
каждой конкретной сборкой.
