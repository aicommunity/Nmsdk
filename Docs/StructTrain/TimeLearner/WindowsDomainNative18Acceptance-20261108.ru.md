# Windows: адресная приёмка native domain18

На `user@10.245.1.14` завершено отложенное задание
`windows-domain-fixture-native-a6`: **18/18 C++ cases**, девять native gates
с actual cooperative module capture. Пересборки не выполнялись.

Исходный root `818dd80aa9c0a311ab3fae314449600f7edbc29f`, PulseLib
`3accbed3c5d6ac2eaff98970227485a9d899835c`; все Git links совпали с фактическими
HEAD, tracked source status пуст до/после. Точные executable hashes заданы
в [плане задания](WindowsDomainNative18PreparedManifest.json).
Пользовательский `C:/Projects/Nmsdk` не изменялся.

## Что проверено

- Десять capture/codec boundary cases.
- Четыре настоящие Classic/Branch domain-capture пробы при 2000/20000 Гц.
- Classic и Branch при N=6: dimension fixtures и full-burst fixtures.
- Четыре независимых Python domain-reader проверки сохранённых JSON/CSV на .14.
- Во всех девяти gates: реальные mappings, ready/ack с теми же PID и creation
  FILETIME, JobObject limits 3 GiB / один процесс до продолжения native child.
- Девять JobObjects после завершения отсутствуют; Schedule Task завершён с0,
  активных экземпляров нет. Все три прежних/текущий runtime inventories неизменны.

Доступная физическая память перед запуском составляла 10 915 479 552 bytes
при необходимом минимуме 3 489 660 928 bytes. Ранее отложенный запуск теперь
прошёл без снижения native memory budget и без автоматического повторения
старых неуспешных заданий. Никаких удалений и переноса build/source не было.

## Первичные данные и границы вывода

Evidence commit `2a26896f45693f2d55b2f0f51cab18ed9eb90059` содержит
268 primary members в `primary.tar.xz`, 387 352 bytes, SHA256
`283388ee3aeea1bad2a334cbb0d6ff939925cd45115957d07ebba67dcb20853d`.
[Независимая квитанция](WindowsDomainNative18Verification.json) проверила каждый
member, точные JUnit ID, 423 actual module records, девять creation-identity pairs,
20 post-closure source hashes по Git и неизменность runtime.
Численные расчёты и Python replay выполнялись только на .14; локально —
проверка метаданных, Git, хешей и JUnit.

Это scoped portability/measurement приёмка прежнего compiled snapshot. Reader
использовал root818dd80, поле `fcc_reader_root_matched=false` сохранено.
Она не переносится автоматически на новые Pulse2c3eb8d / portable codec и
не доказывает физическое закрепление пика, завершённое обучение, классификацию
или полный допуск Windows worker для научной матрицы. Первоначальные build
и module-capture отказы сохранены; их статусы не переоценены. Новый полный
compile/link gate текущего кода с правильным telemetry guard и resources,
а затем его адресные runtime controls остаются следующей проверкой Windows.
